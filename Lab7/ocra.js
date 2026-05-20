// Importa o cliente Dinamo HSM
import { hsm } from "@dinamonetworks/hsm-dinamo";

// Define os parâmetros de conexão com o HSM
const options = {
  host: "127.0.0.1",
  authUsernamePassword: {
    username: "master",
    password: "12345678",
  },
};

async function ocraGen() {
  // 1. Connecta ao HSM
  const conn = await hsm.connect(options);

  // 2. Nome da chave
  const keyName = "myHmacSha1Key";

  // 2.1 Cria uma chave simétrica HMAC SHA1
  const created = await conn.key.create(
    keyName, // Nome da chave
    hsm.enums.HMAC_KEYS.ALG_HMAC_SHA1, // Algoritmo da chave
    true, // Se é exportável
    true // Se é temporária
  );

  // 3. Prepara os parâmetros para execução do ocra

  // 3.1 Challenger (q)
  function stringToHex(text) {
    let hexString = "";
    for (let i = 0; i < text.length; i++) {
      let hex = text.charCodeAt(i).toString(16);
      hexString += hex.padStart(2, "0");
    }
    return hexString;
  }

  const dataToChallenger = "Dados do meu negócio";
  const q = stringToHex(dataToChallenger);

  // 3.2. Recuperando timestamp em timestep de segundos (ts)
  const ts = BigInt(Math.floor(Date.now() / 1000).toString());

  // 4. Executando a função OCRA
  const otp = await conn.ocra.ocraGen(
    keyName, // Id da chave
    q, // Challenger (q)
    "OCRA-1:HOTP-SHA1-6:QA08-T1S", // Suite: Ocra versão 1 com a função HMAC-SHA1 truncado em 6 dígitos usando um challenger superior a 8 caracteres e timestamp em número de segundos
    6, // Tamanho do OTP
    undefined, // contador: não obrigatório
    undefined, // pin hash: não obrigatório
    undefined, // session: Não obrigatório
    ts // Timestamp (ts): não obrigatório
  );

  // 5. Retornando OTP
  console.log(otp);

  // Desconecta do HSM
  await conn.disconnect();
}

// Executando a função ocraGen
ocraGen();