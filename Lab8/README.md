# Lab 8 — OCRA com HSM Dinamo

OTP contextual para **autorizar transações**: o código depende do **challenge** (dados da operação) e do **tempo**, não só de um contador ou relógio isolado. A chave HMAC fica no **HSM** — a aplicação nunca vê o segredo em claro.

Relacionado ao conceito explorado em [Lab 7 — `ocra.js`](../Lab7/ocra.js) (script Node isolado); este lab monta um **serviço HTTP** completo em torno do mesmo fluxo.

## Objetivo

- Criar chave **HMAC-SHA1** no HSM Dinamo.
- Montar um **challenge** ligado à transação (`transactionId`, `amount`, `account`).
- Gerar e validar **OCRA** via API REST (`/setup`, `/challenge`, `/ocra/generate`, `/ocra/verify`).
- Perceber que alterar qualquer campo do challenge altera o OTP esperado.

## Documentação detalhada (implementação)

O passo a passo completo — projeto Node/Express, `.env`, `server.js` e comandos `curl` — está em:

**→ [OCRA.md](./OCRA.md)**

Siga esse ficheiro para montar a aplicação **fora deste repositório** (por exemplo `demo-ocra-dinamo/`). **Não há código Node commitado em `Lab8/`** — apenas documentação.

## Conceito (resumo)

| Ideia | Descrição |
|-------|-----------|
| **OCRA** | OTP atrelado a contexto + tempo (suite `OCRA-1:HOTP-SHA1-6:QA08-T1S` no enunciado) |
| **Challenge** | String com dados da transação, ex.: `transactionId=TX-123;amount=250.00;account=98765-4` |
| **HSM** | Gera o OTP com `conn.ocra.ocraGen(...)` usando chave protegida no appliance |
| **Segurança** | Mudar valor/conta/id → OTP diferente; chave não sai do HSM |

## Fluxo da API (referência)

```text
POST /setup              → cria chave HMAC no HSM
POST /challenge          → devolve challenge da transação
POST /ocra/generate      → gera OTP para um challenge
POST /ocra/verify        → compara OTP informado vs esperado (mesmo timestamp)
```

Servidor de exemplo: `http://localhost:3000` (ver `OCRA.md`).

## Pré-requisitos

- HSM **Dinamo** acessível na rede (`HSM_HOST`, credenciais em `.env`).
- **Node.js** e **npm** no ambiente onde for implementar o projeto (conforme `OCRA.md`).
- Pacote `@dinamonetworks/hsm-dinamo` (instalado no projeto local, não neste repo).

## Teste rápido (após seguir OCRA.md)

1. `npm start` na pasta do projeto criado.
2. `curl -X POST http://localhost:3000/setup`
3. `curl -X POST http://localhost:3000/challenge` com JSON `amount` / `account`.
4. `curl -X POST http://localhost:3000/ocra/generate` com o `challenge` devolvido.
5. `curl -X POST http://localhost:3000/ocra/verify` com `challenge`, `otp` e `timestamp` da resposta anterior → `"valido": "true"`.

## Estrutura desta pasta

| Ficheiro | Conteúdo |
|----------|----------|
| `README.md` | Visão geral e ligação ao lab (este ficheiro) |
| `OCRA.md` | Enunciado completo com código e comandos |

## Notas

- Não commitar `.env` com passwords reais do HSM.
- O OTP de 6 dígitos no exemplo é ilustrativo; em produção combine OCRA com políticas de risco e canal seguro para o challenge.
- Para criptografia pós-quântica e outros usos de HSM, ver [Lab 7](../Lab7/README.md).
