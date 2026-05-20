# Lab 5 — Middleware de segurança (HMAC + anti-replay)

API HTTP com **middleware de autenticação**: cada pedido leva `X-Timestamp`, `X-Nonce` e `X-Signature` (HMAC-SHA256). O servidor valida janela temporal, **nonce único** (anti-replay) e assinatura.

## Objetivo

- Assinar pedidos com chave partilhada (`SECRET_KEY`).
- Rejeitar pedidos expirados, com assinatura errada ou **nonce reutilizado** (replay).
- Separar lógica de verificação (`server.py`) do serviço Flask (`middleware.py`).

## Requisitos

- Python **3.10+**
- [uv](https://docs.astral.sh/uv/)

## Configuração

```bash
cd Lab5
uv sync
```

## Estrutura

| Ficheiro | Função |
|----------|--------|
| `server.py` | Verificação HMAC + demo local (primeiro pedido OK, replay falha) |
| `middleware.py` | Servidor Flask — `POST /transfer` na porta **5000** |
| `client.py` | Gera cabeçalhos e corpo assinados para um transfer |

A `SECRET_KEY` deve ser a mesma nos três ficheiros (`super_chave_secreta_compartilhada` no código de exemplo).

## Como executar

### 1 — Demo offline (sem rede)

Testa `verify_request` e deteção de replay:

```bash
uv run python server.py
```

Saída esperada: primeiro `True OK`, segundo `False Replay detectado...`.

### 2 — API Flask + cliente

**Terminal 1 — servidor:**

```bash
uv run python middleware.py
```

**Terminal 2 — gerar pedido assinado:**

```bash
uv run python client.py
```

Copie os cabeçalhos `X-Timestamp`, `X-Nonce`, `X-Signature` e o JSON do body.

**Terminal 2 (ou 3) — enviar com curl:**

```bash
curl -s -X POST http://127.0.0.1:5000/transfer \
  -H "Content-Type: application/json" \
  -H "X-Timestamp: <valor>" \
  -H "X-Nonce: <valor>" \
  -H "X-Signature: <valor>" \
  -d '{"amount":100.0,"from_account":"123","to_account":"456"}'
```

Resposta esperada: `200` com `"status": "accepted"`.

Repita o **mesmo** `curl` (mesmo nonce): deve devolver `401` com erro de replay.

### 3 — Pedido inválido (opcional)

Altere um carácter em `X-Signature` no curl → `401 Invalid signature`.

Use timestamp antigo (> 30 s) → `401 Expired request`.

## String de assinatura

Ordem fixa (uma linha por campo, separador `\n`):

```
METHOD
PATH
TIMESTAMP
NONCE
CANONICAL_JSON_BODY
```

`CANONICAL_JSON_BODY` = JSON compacto com chaves ordenadas (`sort_keys=True`).

## Parâmetros de segurança

| Parâmetro | Valor no código |
|-----------|-----------------|
| Janela temporal | 30 segundos |
| TTL do nonce | 30 segundos |
| Algoritmo | HMAC-SHA256 (hex) |

## Notas

- Em produção, `SECRET_KEY` viria de variável de ambiente — não commitar chaves reais.
- `middleware.py` usa `debug=True` só para o lab; desative em produção.
- O cliente imprime o pedido; use `curl` ou outro HTTP client para chamar a API.
