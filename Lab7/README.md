# Lab 7 — Criptografia pós-quântica (ML-KEM) e HSM

Dois blocos: **Python + uv** (KEM pós-quântico e RSA/AES) e **scripts shell/Node** (assinatura de código com HSM Dinamo, opcional).

## Requisitos

### Python (obrigatório para PQC)

- Python **3.10+**
- [uv](https://docs.astral.sh/uv/)

### HSM (opcional — Parte 2)

- HSM **Dinamo** acessível (`libtacndp11.so`, token configurado)
- `pkcs11-tool`, OpenSSL com engine PKCS#11
- Para `ocra.js`: Node.js + `npm install @dinamonetworks/hsm-dinamo`

---

## Configuração Python

```bash
cd Lab7
uv sync
```

Dependências: `pqcrypto` (ML-KEM-512, antigo Kyber-512) e `cryptography`.

> **Nota:** Em `pqcrypto>=0.4` o módulo é `pqcrypto.kem.ml_kem_512` (padrão ML-KEM), não `kyber512`.

---

## Parte 1 — KEM pós-quântico (ML-KEM)

### Demo rápida

```bash
uv run python pqc_encrypt.py
uv run python pqc_decrypt.py
```

Valida que o segredo partilhado após encapsular/decapsular é igual (`Match: True`).

### Kyber + AES-GCM (fluxo completo)

```bash
uv run python kyber.py
```

1. Gera par de chaves ML-KEM (servidor).
2. Cliente encapsula → segredo partilhado.
3. Servidor decapsula → mesmo segredo.
4. Deriva chave AES-256 dos primeiros 32 bytes do segredo.
5. Cifra e decifra mensagem com **AES-GCM**.

### RSA clássico (fragmentos)

Ficheiros didáticos (executar numa sessão interativa ou juntar num script):

| Ficheiro | Conteúdo |
|----------|----------|
| `gen_key.py` | Gera par RSA 2048 |
| `encrypt.py` | Cifra com OAEP (precisa de `public_key`) |
| `decrypt.py` | Decifra com OAEP (precisa de `private_key` + `ciphertext`) |

---

## Parte 2 — Assinatura de código com HSM (opcional)

Pipeline para assinar `1app.py` com chave no HSM e verificar offline.

| Script | Passo |
|--------|-------|
| `1app.py` | Aplicação exemplo (`Hello, There!`) |
| `2pkcs11.sh` | Gera par RSA no HSM (ajuste PIN/token) |
| `3hash.sh` | `sha256sum app.py > app.py.sha256` |
| `4sign.sh` | Assina `app.py` → `app.py.sig` (OpenSSL + PKCS#11) |
| `5export_pub_key.sh` | Exporta chave pública do HSM → `public_key.der` |
| `6pem.sh` | Converte DER → `public_key.pem` |
| `7verify.sh` | Verifica assinatura |

Ordem sugerida (com HSM ligado e paths corretos):

```bash
chmod +x *.sh
./2pkcs11.sh      # uma vez, se a chave ainda não existir
./3hash.sh
./4sign.sh
./5export_pub_key.sh
./6pem.sh
./7verify.sh
```

Ajuste `--module`, `--pin` e `--token-label` nos scripts ao seu ambiente Dinamo.

### OCRA (Node.js)

```bash
npm install @dinamonetworks/hsm-dinamo
node ocra.js
```

Gera OTP/OCRA via chave HMAC no HSM (requer conexão ao appliance).

---

## Estrutura

```
Lab7/
├── pqc_encrypt.py / pqc_decrypt.py   # ML-KEM mínimo
├── kyber.py                          # ML-KEM + AES-GCM
├── gen_key.py / encrypt.py / decrypt.py
├── 1app.py … 7verify.sh              # HSM (shell)
├── ocra.js                           # HSM (Node)
├── pyproject.toml
├── uv.lock
└── README.md
```

## Segurança (lab)

- Não commitar `*.pem`, `*.der`, `*.sig` — já listados em `.gitignore`.
- PINs nos scripts `.sh` são exemplos; use variáveis de ambiente em produção.
- ML-KEM fornece confidencialidade do segredo; AES-GCM protege a mensagem com nonce único (`os.urandom(12)`).
