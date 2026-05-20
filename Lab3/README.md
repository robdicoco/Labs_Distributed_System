# Lab 3 — TCP vs UDP vs QUIC (velocidade de comunicação)

Compara o **tempo de ida e volta (RTT)** do mesmo par de mensagens `PING` / `ACK` em três protocolos no localhost:

| Protocolo | Porta | Transporte |
|-----------|-------|------------|
| TCP | 5000 | Ligação persistente |
| UDP | 5001 | Datagramas |
| QUIC | 5002 | UDP + TLS 1.3 (via [aioquic](https://github.com/aiortc/aioquic)) |

## Objetivo

- Medir latência média, mediana, mínima e máxima por protocolo.
- Comparar qual foi mais rápido neste cenário (mensagens pequenas, loopback).

## Requisitos

- Python **3.10+**
- [uv](https://docs.astral.sh/uv/)
- **OpenSSL** (`openssl` no PATH) — para gerar certificados TLS do QUIC

## Configuração

```bash
cd Lab3
uv sync
uv run python scripts/generate_certs.py
```

Isto cria `certs/cert.pem` e `certs/key.pem` (autoassinados, com **subjectAltName** — obrigatório para QUIC).

Se já tinha certificados antigos e o QUIC falha com `subjectAltName`, regenere:

```bash
rm -f certs/cert.pem certs/key.pem
uv run python scripts/generate_certs.py
```

## Como executar

Abra **quatro terminais** em `Lab3/`:

**1 — TCP**

```bash
uv run python tcp_server.py
```

**2 — UDP**

```bash
uv run python udp_server.py
```

**3 — QUIC**

```bash
uv run python quic_server.py
```

**4 — Cliente**

```bash
uv run python client.py
```

Opções:

```bash
uv run python client.py --rounds 5000
uv run python client.py --quic-port 5002 --skip-quic
```

Parar servidores com `Ctrl+C`.

## Estrutura

| Ficheiro | Função |
|----------|--------|
| `tcp_server.py` | Servidor TCP |
| `udp_server.py` | Servidor UDP |
| `quic_server.py` | Servidor QUIC (TLS) |
| `quic_common.py` | Certificados e configuração QUIC partilhada |
| `client.py` | Benchmark TCP → UDP → QUIC |
| `scripts/generate_certs.py` | Gera certificados autoassinados |

## Interpretação

- **TCP**: uma ligação, muitas mensagens (handshake TCP uma vez).
- **UDP**: sem ligação; cada ronda é um datagrama.
- **QUIC**: uma sessão QUIC (handshake criptográfico uma vez), mensagens num stream; overhead de TLS, mas multiplexação moderna sobre UDP.
- Em **localhost**, as diferenças são pequenas; QUIC pode ser mais lento que TCP/UDP por causa do TLS.

## Docker (opcional)

```bash
SERVER_HOST=server uv run python client.py
```
