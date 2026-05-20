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
lab-2pc-blockchain/
├── contracts/
│   └── CommitLog.sol
├── scripts/
│   └── deploy.js
├── coordinator.js
├── bankA.js
├── bankB.js
├── package.json
├── hardhat.config.js
└── .env
```

## 1 - Criar o Projeto

```sh
mkdir lab-2pc-blockchain
cd lab-2pc-blockchain
npm init -y
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
npm install ethers dotenv
npx hardhat init
```

## 2 - Smart Contract

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
PRIVATE_KEY=SUA_PRIVATE_KEY_SEM_0x
CONTRACT_ADDRESS=
```

## 4 - Hardhat config

Edite `hardhat.config.js`:

```js
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: "0.8.24",
  networks: {
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL,
      accounts: [process.env.PRIVATE_KEY],
      chainId: 11155111,
    },
  },
};
```

## 5 - Deploy do contrato:
Crie `scripts/deploy.js`:

```js
const hre = require("hardhat");

async function main() {
  const CommitLog = await hre.ethers.getContractFactory("CommitLog");
  const commitLog = await CommitLog.deploy();

  await commitLog.waitForDeployment();

  console.log("CommitLog deployed to:", await commitLog.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

### 5.1 - Execute:

```sh
npx hardhat compile
npx hardhat run scripts/deploy.js --network sepolia
```

### 5.2 Copie o endereço do contrato para o .env:

```env 
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/SUA_CHAVE
PRIVATE_KEY=SUA_PRIVATE_KEY_SEM_0x
CONTRACT_ADDRESS=COLE_O_ENDEREÇO_AQUI
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

### Saída esperada:

```sh
Iniciando transação tx-...
Transferência: Banco A -> Banco B | Valor: 50
[Coordenador] Voto de Banco A: YES
[Coordenador] Voto de Banco B: YES
[Coordenador] Decisão final: COMMIT
[Coordenador] Registrando decisão na Sepolia...
Hash da transação: 0x...
```

### O que aconteceu?

1. O coordenador iniciou uma transação distribuída.
1. Banco A verificou se tinha saldo.
1. Banco B confirmou que poderia receber.
1. Todos votaram YES.
1. O coordenador decidiu COMMIT.
1. A blockchain registrou a decisão final.


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