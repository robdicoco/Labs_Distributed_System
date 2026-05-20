# Lab: 2PC + Blockchain Sepolia

## Objetivo

Simular uma transferência bancária distribuída:

```sh

|=============================================|
| Conta A  ---- transfere R$ 50 ----> Conta B |
|=============================================|

Coordenador 2PC:
1. envia PREPARE para Banco A e Banco B
2. coleta votos YES/NO
3. decide COMMIT ou ABORT
4. registra a decisão final em um smart contract na Sepolia
```

## Arquitetura

```sh

+------------------+
| Cliente          |
+--------+---------+
         |
         v
+------------------+
| Coordenador 2PC  |
+----+---------+---+
     |         |
     v         v
+---------+ +---------+
| Banco A | | Banco B |
+---------+ +---------+
     |
     v
+--------------------------+
| Smart Contract Sepolia   |
| Registro de decisão 2PC  |
+--------------------------+
```

### Conceito explicado

#### Onde entra o 2PC?

O 2PC decide se a transação distribuída pode ser concluída.
    - Se todos os participantes responderem YES, o coordenador envia COMMIT.
    - Se algum participante responder NO, o coordenador envia ABORT.

#### Onde entra a blockchain?

A blockchain não substitui o 2PC neste lab. Ela funciona como:
    - trilha de auditoria;
    - registro imutável da decisão;
    - prova pública de que a transação foi finalizada como COMMIT ou ABORT.

### Estrutura do Projeto

```sh
lab-2pc-foundry/
├── src/
│   └── CommitLog.sol
├── script/
│   └── DeployCommitLog.s.sol
├── coordinator.js
├── bankA.js
├── bankB.js
├── foundry.toml
├── package.json
└── .env
```

## 1 - Criar o Projeto

Instale o Foundry:

```sh
curl -L https://foundry.paradigm.xyz | bash
```

Inicialize o Foundry:

```sh
foundryup
```

Crie o projeto:
```sh
mkdir lab-2pc-foundry
cd lab-2pc-foundry

forge init
npm init -y
npm install ethers dotenv
```

## 2 - Smart Contract

Crie o `src/CommitLog.sol` 

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract CommitLog {
    enum Decision {
        UNKNOWN,
        COMMIT,
        ABORT
    }

    struct TransactionRecord {
        string transactionId;
        Decision decision;
        uint256 timestamp;
        address coordinator;
    }

    mapping(string => TransactionRecord) public records;

    event DecisionRecorded(
        string transactionId,
        Decision decision,
        uint256 timestamp,
        address coordinator
    );

    function recordDecision(
        string memory transactionId,
        Decision decision
    ) public {
        require(
            records[transactionId].decision == Decision.UNKNOWN,
            "Decision already recorded"
        );

        require(
            decision == Decision.COMMIT || decision == Decision.ABORT,
            "Invalid decision"
        );

        records[transactionId] = TransactionRecord({
            transactionId: transactionId,
            decision: decision,
            timestamp: block.timestamp,
            coordinator: msg.sender
        });

        emit DecisionRecorded(
            transactionId,
            decision,
            block.timestamp,
            msg.sender
        );
    }

    function getDecision(
        string memory transactionId
    ) public view returns (Decision) {
        return records[transactionId].decision;
    }
}
```

## 3 - Sepolia

Crie o `.env`:

```env
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/SUA_CHAVE
PRIVATE_KEY=SUA_PRIVATE_KEY_COM_0x
CONTRACT_ADDRESS=
```

## 4 - Configure o Foundry

Edite `foundry.toml`:

```toml
[profile.default]
src = "src"
out = "out"
libs = ["lib"]
solc_version = "0.8.24"
optimizer = true
optimizer_runs = 200

[rpc_endpoints]
sepolia = "${SEPOLIA_RPC_URL}"
```

## 5 - Deploy do contrato:

Crie `script/DeployCommitLog.s.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "../src/CommitLog.sol";

contract DeployCommitLog is Script {
    function run() external returns (CommitLog) {
        vm.startBroadcast();

        CommitLog commitLog = new CommitLog();

        vm.stopBroadcast();

        return commitLog;
    }
}
```

### 5.1 - Compilar:

```sh
forge build
```

### 5.2 - Fazer o Deploy na Rede Sepolia


Carregue as variáveis de ambiente:

```sh
source .env
```

Faça o deploy:
```sh
forge script script/DeployCommitLog.s.sol:DeployCommitLog \
  --rpc-url $SEPOLIA_RPC_URL \
  --private-key $PRIVATE_KEY \
  --broadcast
```

> O Foundry também permite deploy direto com forge create, mas para aula o forge script é mais didático porque mostra o fluxo de implantação como código. A própria documentação do Foundry apresenta forge como ferramenta de build, teste, debug, deploy e verificação de smart contracts.

### 5.3 - Após o deploy, copie o endereço do contrato e atualize o .env:

```env
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/SUA_CHAVE
PRIVATE_KEY=SUA_PRIVATE_KEY_COM_0x
CONTRACT_ADDRESS=0xENDERECO_DO_CONTRATO
```

## 6 - Participante Banco A

Crie `bankA.js`

```js
const net = require("net");

let balance = 100;

const server = net.createServer((socket) => {
  socket.on("data", (data) => {
    const msg = JSON.parse(data.toString());

    if (msg.type === "PREPARE") {
      console.log("[Banco A] PREPARE recebido");

      if (balance >= msg.amount) {
        socket.write(JSON.stringify({ vote: "YES" }));
      } else {
        socket.write(JSON.stringify({ vote: "NO" }));
      }
    }

    if (msg.type === "COMMIT") {
      balance -= msg.amount;
      console.log(`[Banco A] COMMIT. Novo saldo: ${balance}`);
      socket.write(JSON.stringify({ status: "OK" }));
    }

    if (msg.type === "ABORT") {
      console.log("[Banco A] ABORT. Nenhuma alteração feita.");
      socket.write(JSON.stringify({ status: "OK" }));
    }
  });
});

server.listen(5001, () => {
  console.log("[Banco A] Escutando na porta 5001");
});
```

## 7 - Participante Banco B

Crie `bankB.js`

```js
const net = require("net");

let balance = 20;

const server = net.createServer((socket) => {
  socket.on("data", (data) => {
    const msg = JSON.parse(data.toString());

    if (msg.type === "PREPARE") {
      console.log("[Banco B] PREPARE recebido");
      socket.write(JSON.stringify({ vote: "YES" }));
    }

    if (msg.type === "COMMIT") {
      balance += msg.amount;
      console.log(`[Banco B] COMMIT. Novo saldo: ${balance}`);
      socket.write(JSON.stringify({ status: "OK" }));
    }

    if (msg.type === "ABORT") {
      console.log("[Banco B] ABORT. Nenhuma alteração feita.");
      socket.write(JSON.stringify({ status: "OK" }));
    }
  });
});

server.listen(5002, () => {
  console.log("[Banco B] Escutando na porta 5002");
});
```

## 8 - Coordenador 2PC + Sepolia

Crie `coordinator.js`

```js
require("dotenv").config();

const net = require("net");
const { ethers } = require("ethers");

const participants = [
  { name: "Banco A", host: "127.0.0.1", port: 5001 },
  { name: "Banco B", host: "127.0.0.1", port: 5002 },
];

const abi = [
  "function recordDecision(string transactionId, uint8 decision) public",
  "function getDecision(string transactionId) public view returns (uint8)",
];

const provider = new ethers.JsonRpcProvider(process.env.SEPOLIA_RPC_URL);
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);

const contract = new ethers.Contract(
  process.env.CONTRACT_ADDRESS,
  abi,
  wallet
);

function sendMessage(participant, message) {
  return new Promise((resolve, reject) => {
    const client = new net.Socket();

    client.connect(participant.port, participant.host, () => {
      client.write(JSON.stringify(message));
    });

    client.on("data", (data) => {
      resolve(JSON.parse(data.toString()));
      client.destroy();
    });

    client.on("error", reject);
  });
}

async function run2PC() {
  const transactionId = `tx-${Date.now()}`;
  const amount = 50;

  console.log(`\nIniciando transação ${transactionId}`);
  console.log(`Transferência: Banco A -> Banco B | Valor: ${amount}`);

  const votes = [];

  for (const p of participants) {
    const response = await sendMessage(p, {
      type: "PREPARE",
      transactionId,
      amount,
    });

    console.log(`[Coordenador] Voto de ${p.name}: ${response.vote}`);
    votes.push(response.vote);
  }

  const decision = votes.every((v) => v === "YES") ? "COMMIT" : "ABORT";

  console.log(`[Coordenador] Decisão final: ${decision}`);

  for (const p of participants) {
    await sendMessage(p, {
      type: decision,
      transactionId,
      amount,
    });
  }

  const blockchainDecision = decision === "COMMIT" ? 1 : 2;

  console.log("[Coordenador] Registrando decisão na Sepolia...");

  const tx = await contract.recordDecision(transactionId, blockchainDecision);
  await tx.wait();

  console.log("[Coordenador] Decisão registrada na blockchain.");
  console.log("Hash da transação:", tx.hash);
}

run2PC().catch(console.error);
```

## 9 - Execute o Lab

Abra 3 terminais:

### Terminal 1

```sh
node bankA.js
```

### Terminal 2

```sh
node bankB.js
```

### Terminal 3

```sh
node coordinator.js
```
> Não esqueça de anotar os dados do `tx-`

### 10 - Consultar Decisão com CAST

> Ajuste o valor de `tx-123` de acordo com o valor obtido no deploy do contrato

```sh
cast call $CONTRACT_ADDRESS \
  "getDecision(string)(uint8)" \
  "tx-123" \
  --rpc-url $SEPOLIA_RPC_URL
```

### Resultado esperado:

```sh
1
```

### Interpretação:

```sh
0 = UNKNOWN
1 = COMMIT
2 = ABORT
```

> `cast` é a ferramenta de linha de comando do Foundry para interação com redes Ethereum.


### Explicação:

Papel do 2PC

O protocolo 2PC controla a decisão distribuída:

 ```sh
 |===============================|
 | PREPARE → VOTE → COMMIT/ABORT |
 |===============================|
 ```

 Ele garante que os participantes não fiquem em estados contraditórios.

 ### Papel da blockchain

A Sepolia registra:

```sh
transactionId
decision
timestamp
coordinator
```

## 10 - Teste de ABORT

Altere o `coordinator.js`:

```js
const amount =150;
```

Como o Banco A tem saldo `100`, ele votará `NO`.

### Resultado esperado:

```sh
[Coordenador] Voto de Banco A: NO
[Coordenador] Voto de Banco B: YES
[Coordenador] Decisão final: ABORT
```

### Nesse caso, nenhuma conta é alterada, mas a decisão ABORT também é registrada na blockchain.

## 11 - Comando para ler o registro do contrato:

```sh 
cast call $CONTRACT_ADDRESS \
  "records(string)(string,uint8,uint256,address)" \
  "tx-123" \
  --rpc-url $SEPOLIA_RPC_URL
  ```

> para converter o Unix timestampt UTC:

  ```sh
  date -d @1714421100
  ```
Hands On Sepolia.md
Displaying Hands On Sepolia.md.