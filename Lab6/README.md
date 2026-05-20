# Lab 6 — Two-Phase Commit (2PC) + blockchain Sepolia

Simula uma **transferência bancária distribuída** (Banco A → Banco B) com protocolo **2PC** (PREPARE → votos → COMMIT/ABORT) e registo imutável da decisão no contrato **`CommitLog`** na rede **Sepolia**.

| Camada | Tecnologia |
|--------|------------|
| Contrato | Foundry / Solidity |
| Deploy | MetaMask (`deploy/index.html`) |
| Participantes 2PC | Python (`bank_a.py`, `bank_b.py`) |
| Coordenador | Python HTTP + MetaMask (`coordinator.py` + UI) |
| Verificação | `cast` |

## Documentação detalhada

Toda a implementação e comandos passo a passo estão no projeto:

**→ [lab-2pc-blockchain/README.md](lab-2pc-blockchain/README.md)**

## Planeamento e enunciado

| Documento | Conteúdo |
|-----------|----------|
| [ActionPlan.MD](ActionPlan.MD) | Checklist das fases (Foundry, deploy, 2PC, `cast`) |
| [Task/Hands On Sepolia v2.md](Task/Hands%20On%20Sepolia%20v2.md) | Enunciado oficial (Foundry + `cast`) |
| [Task/Hands On Sepolia.md](Task/Hands%20On%20Sepolia.md) | Versão anterior (Hardhat) — referência |

## Início rápido

```bash
cd lab-2pc-blockchain
uv sync
forge build && python3 scripts/sync_deploy_artifact.py
```

1. Deploy: `./deploy/serve.sh` → http://127.0.0.1:8787 (MetaMask)  
2. Banks: `uv run python bank_a.py` e `uv run python bank_b.py`  
3. Coordenador: `uv run python coordinator.py` → http://127.0.0.1:8788 (MetaMask)

Screenshots de exemplo: pasta `lab-2pc-blockchain/results/`.
