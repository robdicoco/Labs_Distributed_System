# Laboratório 8 - OCRA

## Inicializar o projeto

```sh
mkdir demo-ocra-dinamo
cd demo-ocra-dinamo
npm init -y
npm i express dotenv @dinamonetworks/hsm-dinamo
```
No `package.json` adicione:

```json
{
  "type": "module",
  "scripts": {
    "start": "node server.js"
  }
}
```

## Configure arquivo `.env`

```env
HSM_HOST=127.0.0.1
HSM_USER=master
HSM_PASSWORD=12345678
OCRA_KEY_NAME=aulaOcraHmacSha1
PORT=3000
```

## Crie arquivo `server.js`

```js
import express from "express";
import dotenv from "dotenv";
import { hsm } from "@dinamonetworks/hsm-dinamo";

dotenv.config();

const app = express();
app.use(express.json());

const OCRA_SUITE = "OCRA-1:HOTP-SHA1-6:QA08-T1S";
const OTP_SIZE = 6;

const options = {
  host: process.env.HSM_HOST,
  authUsernamePassword: {
    username: process.env.HSM_USER,
    password: process.env.HSM_PASSWORD,
  },
};

function stringToHex(text) {
  return Buffer.from(text, "utf8").toString("hex");
}

async function withHsm(callback) {
  const conn = await hsm.connect(options);

  try {
    return await callback(conn);
  } finally {
    await conn.disconnect();
  }
}

app.post("/setup", async (req, res) => {
  try {
    const keyName = process.env.OCRA_KEY_NAME;

    const result = await withHsm(async (conn) => {
      return await conn.key.create(
        keyName,
        hsm.enums.HMAC_KEYS.ALG_HMAC_SHA1,
        true,
        false
      );
    });

    res.json({
      message: "Chave HMAC-SHA1 criada no HSM",
      keyName,
      result,
    });
  } catch (error) {
    res.status(500).json({
      error: "Erro ao criar chave no HSM",
      detail: error.message,
    });
  }
});

app.post("/challenge", async (req, res) => {
  const transactionId = `TX-${Date.now()}`;
  const amount = req.body.amount ?? "100.00";
  const account = req.body.account ?? "12345-6";

  const challenge = `transactionId=${transactionId};amount=${amount};account=${account}`;

  res.json({
    explanation: "Este challenge representa os dados da transação que serão protegidos pelo OCRA.",
    challenge,
  });
});

app.post("/ocra/generate", async (req, res) => {
  try {
    const { challenge } = req.body;

    if (!challenge) {
      return res.status(400).json({ error: "Informe o campo challenge" });
    }

    const q = stringToHex(challenge);
    const ts = BigInt(Math.floor(Date.now() / 1000).toString());

    const otp = await withHsm(async (conn) => {
      return await conn.ocra.ocraGen(
        process.env.OCRA_KEY_NAME,
        q,
        OCRA_SUITE,
        OTP_SIZE,
        undefined,
        undefined,
        undefined,
        ts
      );
    });

    res.json({
      challenge,
      q,
      suite: OCRA_SUITE,
      timestamp: ts.toString(),
      otp,
    });
  } catch (error) {
    res.status(500).json({
      error: "Erro ao gerar OCRA",
      detail: error.message,
    });
  }
});

app.post("/ocra/verify", async (req, res) => {
  try {
    const { challenge, otp, timestamp } = req.body;

    if (!challenge || !otp || !timestamp) {
      return res.status(400).json({
        error: "Informe challenge, otp e timestamp",
      });
    }

    const q = stringToHex(challenge);
    const ts = BigInt(timestamp);

    const expectedOtp = await withHsm(async (conn) => {
      return await conn.ocra.ocraGen(
        process.env.OCRA_KEY_NAME,
        q,
        OCRA_SUITE,
        OTP_SIZE,
        undefined,
        undefined,
        undefined,
        ts
      );
    });

    res.json({
      challenge,
      otpInformado: otp,
      otpEsperado: expectedOtp,
      valido: String(otp) === String(expectedOtp),
    });
  } catch (error) {
    res.status(500).json({
      error: "Erro ao validar OCRA",
      detail: error.message,
    });
  }
});

app.listen(process.env.PORT || 3000, () => {
  console.log(`Demo OCRA DINAMO rodando em http://localhost:${process.env.PORT || 3000}`);
});
```

## Inicialize a aplicação:

```sh
npm start
```

## Crie uma chave no HSM

```sh
curl -X POST http://localhost:3000/setup
```

## Gerar um challenge

```sh
curl -X POST http://localhost:3000/challenge \
  -H "Content-Type: application/json" \
  -d '{"amount":"250.00","account":"98765-4"}'
```

## Gerar o OCRA

```sh
curl -X POST http://localhost:3000/ocra/generate \
  -H "Content-Type: application/json" \
  -d '{"challenge":"transactionId=TX-123;amount=250.00;account=98765-4"}'
```

## Validar o OCRA

Use o `otp` e o `timestamp` retornados:

```sh
curl -X POST http://localhost:3000/ocra/verify \
  -H "Content-Type: application/json" \
  -d '{
    "challenge":"transactionId=TX-123;amount=250.00;account=98765-4",
    "otp":"123456",
    "timestamp":"1760000000"
  }'
```

## RESUMO:

O OCRA funciona como um OTP vinculado ao contexto da transação. Diferente de um OTP simples baseado apenas em tempo, aqui o código depende também do challenge, por exemplo:

`transactionId=TX-123;amount=250.00;account=98765-4`

Assim, se alguém alterar o valor, a conta ou o identificador da transação, o OTP gerado será diferente. O HSM protege a chave HMAC usada no cálculo, evitando que a aplicação tenha acesso direto ao segredo criptográfico.