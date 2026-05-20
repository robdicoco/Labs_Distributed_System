# Lab 1 — TCP cliente/servidor

Introdução a **sockets TCP** em Python: um servidor aceita uma ligação, recebe uma mensagem e responde; o cliente liga-se, envia texto e imprime a resposta.

## Objetivo

- Criar um socket servidor (`bind` / `listen` / `accept` / `recv` / `send`).
- Criar um socket cliente (`connect` / `send` / `recv`).
- Observar o fluxo pedido → resposta numa única sessão.

## Estrutura

| Pasta / ficheiro | Função |
|------------------|--------|
| `server/server.py` | Servidor em `0.0.0.0:5000` |
| `client/client.py` | Cliente que envia `Ola servidor!` |

## Requisitos

- Python **3.10+**

## Como executar (local)

1. **Servidor** (terminal 1), na pasta do lab:

   ```bash
   cd Lab1
   python server/server.py
   ```

2. **Cliente** (terminal 2):

   ```bash
   python client/client.py
   ```

   Por defeito liga a `127.0.0.1`. Em Docker, use `SERVER_HOST=server python client/client.py`.

3. Parar o servidor com `Ctrl+C`.

## Saída esperada

- Servidor: `Conectado por …`, `Recebido: Ola servidor!`
- Cliente: `Resposta: Mensagem recebida com sucesso!`

## Notas

- O cliente inclui `time.sleep` entre passos para facilitar leitura dos logs.
- Em **Docker**, defina `SERVER_HOST=server` no cliente quando o serviço do servidor se chama `server` na rede.
