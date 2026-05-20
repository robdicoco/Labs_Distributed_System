# Lab 4 — Eleição de líder (Bully) e sincronização Berkeley

Dois exercícios de **sistemas distribuídos**: eleição de coordenador com o algoritmo **Bully** sobre TCP, e sincronização de relógios com o algoritmo de **Berkeley** (simulação local).

## Conteúdo

| Ficheiro | Tema |
|----------|------|
| `bully.py` | Algoritmo Bully — eleição do processo com **maior ID** |
| `berkeley.py` | Algoritmo de Berkeley — média de relógios com exclusão de **outliers** |

## Requisitos

- Python **3.10+**
- [uv](https://docs.astral.sh/uv/)

## Configuração

```bash
cd Lab4
uv sync
```

Sem dependências externas (apenas biblioteca padrão). O `uv.lock` fixa o ambiente para reprodutibilidade.

---

## Parte 1 — Bully (TCP)

Cada processo é um nó com ID numérico. O coordenador é o nó de **maior ID** entre os ativos. Se o coordenador falhar (não responde a `PING`), inicia-se nova eleição.

### Portas (5 nós por defeito)

Com `--base-port 5000` e `--nodes 5`:

| Nó | Porta |
|----|-------|
| P1 | 5001 |
| P2 | 5002 |
| P3 | 5003 |
| P4 | 5004 |
| P5 | 5005 |

### Como executar

Abra **um terminal por nó** (exemplo com 3 nós):

```bash
cd Lab4
uv run python bully.py --id 1 --nodes 3
uv run python bully.py --id 2 --nodes 3
uv run python bully.py --id 3 --nodes 3
```

Opções:

```bash
uv run python bully.py --id 4 --nodes 5 --base-port 5000
```

### Comandos interativos (em cada terminal)

| Comando | Ação |
|---------|------|
| `status` | Mostra coordenador atual e se há eleição em curso |
| `election` | Força uma eleição |
| `quit` | Encerra o processo |

### Mensagens do protocolo

- `PING` / `PONG` — monitorização do coordenador
- `ELECTION` / `OK` — fase de eleição (nós com ID maior respondem `OK`)
- `COORDINATOR` — anúncio do novo líder
- `STATUS` — consulta de estado

### Experiência sugerida

1. Suba P1, P2 e P3; observe P3 tornar-se coordenador (maior ID).
2. No terminal de P3, `quit` — P1 ou P2 deve detetar falha e eleger novo coordenador.
3. Use `election` manualmente para ver mensagens no log.

---

## Parte 2 — Berkeley (simulação)

Sincronização de relógios lógicos: o **mestre** recolhe tempos, calcula a **média** dos nós dentro do limite `outlier_limit` e aplica ajustes.

```bash
uv run python berkeley.py
```

Saída: relógios antes/depois, nós válidos, outliers ignorados e ajustes aplicados. O exemplo inclui um nó com desvio grande (`Nó 4`, 150s) excluído da média.

---

## Estrutura

```
Lab4/
├── bully.py       # Eleição Bully (rede)
├── berkeley.py    # Berkeley (local)
├── pyproject.toml
├── uv.lock
└── README.md
```

## Notas

- **Bully**: IDs maiores têm prioridade; vários processos no mesmo host usam portas diferentes.
- **Berkeley**: versão didática sem sockets; a coleta de tempos está simulada em memória.
- Liberte portas após testes: `fuser -k 5001/tcp 5002/tcp …` se necessário.
