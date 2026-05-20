# Lab 2 — Sockets e threads

Pequeno exemplo de **TCP**, **threading** e **sincronização**: um servidor aceita conexões em `127.0.0.1:65432` e trata cada cliente numa thread; o cliente lança 10 threads que só começam a conectar depois de um `threading.Event` comum (“starter pistol”), para demonstrar partida sincronizada.

## Requisitos

- Python **3.10+**
- [uv](https://docs.astral.sh/uv/) (gestão de ambiente e dependências)

## Configuração

```bash
uv sync
```

Isto cria/atualiza `.venv` conforme `uv.lock`.

## Como executar

1. **Servidor** (deixar a correr):

   ```bash
   uv run python server.py
   ```

2. **Cliente** (noutro terminal):

   ```bash
   uv run python client.py
   ```

O servidor responde com uma mensagem curta a cada cliente; o cliente imprime quando cada thread envia dados. Parar o servidor com `Ctrl+C`.

## Estrutura

| Ficheiro    | Função |
|------------|--------|
| `server.py` | Servidor TCP multithread em `65432` |
| `client.py` | 10 threads cliente com arranque sincronizado |

Não há dependências externas — apenas a biblioteca padrão.
