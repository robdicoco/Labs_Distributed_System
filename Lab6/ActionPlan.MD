# Action Plan: Lab 2PC + Sepolia (Foundry / Forge)

This document mirrors **[Hands On Sepolia v2.md](./Task/Hands%20On%20Sepolia%20v2.md)** (canonical lab). The older [Hands On Sepolia.md](./Task/Hands%20On%20Sepolia.md) used **Hardhat**; v2 is **Foundry-only** for contracts and adds **`cast`** read-back on Sepolia.

The 2PC **coordinator and bank processes** are implemented with **Python** (stdlib `socket` + **`web3.py`**), not the JavaScript in the lab handout. Forge + `cast` match v2; only the TCP/JSON-RPC layer differs from `bankA.js` / `coordinator.js`.

**Why Python instead of Node:** The lab’s banks and coordinator are plain TCP + JSON-RPC. Any language with sockets and an Ethereum client works. This plan uses **Python** to avoid `node`/npm in the 2PC layer.

**Repository status:** Phase A + B scaffolding is in `lab-2pc-blockchain/` (contract, deploy script, `.env.example`, `load_dotenv`). You still need a **real Sepolia deploy** and **`CONTRACT_ADDRESS` in `.env`** before Phase C–D.

> **Folder name:** v2 names the project `lab-2pc-foundry/`; this repo uses **`lab-2pc-blockchain/`** (same layout: `src/`, `script/`, `foundry.toml`).

---

## What changed from v1 → v2 (lab handout)

| Topic | v1 (`Hands On Sepolia.md`) | v2 (`Hands On Sepolia v2.md`) |
|--------|---------------------------|-------------------------------|
| Toolchain | Hardhat (`hardhat.config.js`, `scripts/deploy.js`) | Foundry (`foundry.toml`, `forge build`, `forge script`) |
| Contract path | `contracts/CommitLog.sol` | `src/CommitLog.sol` |
| Deploy | `npx hardhat run scripts/deploy.js --network sepolia` | `forge script script/DeployCommitLog.s.sol:DeployCommitLog ... --broadcast` |
| Project bootstrap | `npm` + `npx hardhat init` | `foundryup`, `forge init`, `npm` only for `ethers`/`dotenv` if using JS |
| On-chain reads | Not in handout | `cast call` for `getDecision` and `records` |
| `.env` private key hint | `SEM_0x` (without `0x`) | `COM_0x` (with `0x`) |
| Extra concepts | — | Enum `0/1/2`, 2PC vs blockchain roles, note to save `tx-…` id |

Contract logic, bank balances, ports **5001/5002**, and coordinator 2PC flow are **unchanged** between v1 and v2.

---

## Review: Lab v2 → this repository

| Lab v2 step | This repo |
|-------------|-----------|
| Install Foundry (`curl … \| bash`, `foundryup`) | Prerequisite on your machine (not in repo) |
| `mkdir lab-2pc-foundry && forge init` | `lab-2pc-blockchain/` already initialized with `forge init` |
| `src/CommitLog.sol` | `lab-2pc-blockchain/src/CommitLog.sol` |
| `foundry.toml` (`solc_version`, `[rpc_endpoints] sepolia`) | `lab-2pc-blockchain/foundry.toml` (+ `load_dotenv = true`) |
| `forge script` + `--private-key` (v2 handout) | **`deploy/index.html` + MetaMask** (this repo; no key in CLI) |
| `forge build` | Same + `python3 scripts/sync_deploy_artifact.py` |
| `bankA.js` / `bankB.js` / `coordinator.js` | **`bank_a.py` / `bank_b.py` / `coordinator.py`** (planned) |
| `cast call` … `getDecision` / `records` | Same commands from shell after coordinator run |

**Coordinator ABI / enum values:** On-chain, `Decision` is `UNKNOWN=0`, `COMMIT=1`, `ABORT=2`. `web3.py` encodes `recordDecision(transactionId, decision)` the same way as ethers in the handout.

---

## Phase A — Foundry toolchain and contract

- [x] Install Foundry if needed: `curl -L https://foundry.paradigm.xyz | bash` then `foundryup` (per v2 §1).
- [x] Project directory `lab-2pc-blockchain/` exists with `forge init` layout.
- [x] Add `src/CommitLog.sol` (same contract as v2: pragma `^0.8.24`, enum `Decision`, `recordDecision`, `getDecision`, events).
- [x] `foundry.toml`: `solc_version = "0.8.24"`, `[rpc_endpoints] sepolia = "${SEPOLIA_RPC_URL}"`.
- [x] Optional (v2 §4): add `optimizer = true` and `optimizer_runs = 200` under `[profile.default]` if you want to match the handout exactly.

## Phase B — Secrets and deploy (MetaMask)

- [x] `.env.example` → copy to `.env` with `SEPOLIA_RPC_URL`, empty `CONTRACT_ADDRESS` (no `PRIVATE_KEY` for deploy).
- [x] `forge build` then `python3 scripts/sync_deploy_artifact.py` → `deploy/artifact.json`.
- [x] MetaMask deploy UI: `deploy/index.html` + `./deploy/serve.sh` → open **http://127.0.0.1:8787**.
- [ ] Connect MetaMask, switch to **Sepolia**, deploy **CommitLog**, confirm in wallet popup.
- [ ] Copy deployed address into `.env` as `CONTRACT_ADDRESS`.
- [x] `script/Deploy.s.sol` kept for Anvil/CI only (not Sepolia + private key).

## Phase C — Python 2PC layer (same protocol as v2 §6–8, no Node)

- [ ] Venv: `python -m venv .venv && source .venv/bin/activate`.
- [ ] `pip install web3 python-dotenv` (optional `requirements.txt`).
- [ ] `bank_a.py` / `bank_b.py`: TCP **5001** / **5002**; JSON `PREPARE` / `COMMIT` / `ABORT`; balances **100** / **20**; Bank A votes NO if `balance < amount`.
- [ ] `coordinator.py`: 2PC loop then `recordDecision` on Sepolia; **`COMMIT` → 1**, **`ABORT` → 2**; log **`transactionId`** (`tx-…`) and tx hash (v2 §9: do not lose the `tx-` id).
- [ ] ABI from `out/CommitLog.sol/CommitLog.json` or minimal ABI fragment.

## Phase D — Run, verify on-chain, ABORT test

- [ ] Terminal 1: `python bank_a.py`
- [ ] Terminal 2: `python bank_b.py`
- [ ] Terminal 3: `python coordinator.py`
- [ ] Logs: YES/YES → COMMIT; Sepolia tx hash printed.
- [ ] **Read decision with `cast`** (v2 §10), after `source .env`, using the real `tx-…` from the coordinator:

```bash
cast call "$CONTRACT_ADDRESS" \
  "getDecision(string)(uint8)" \
  "tx-REPLACE_ME" \
  --rpc-url "$SEPOLIA_RPC_URL"
```

Expected after COMMIT: `1` (`0` = UNKNOWN, `1` = COMMIT, `2` = ABORT).

- [ ] **Read full record with `cast`** (v2 §11):

```bash
cast call "$CONTRACT_ADDRESS" \
  "records(string)(string,uint8,uint256,address)" \
  "tx-REPLACE_ME" \
  --rpc-url "$SEPOLIA_RPC_URL"
```

Optional UTC timestamp: `date -d @<unix_timestamp_from_record>`.

- [ ] **ABORT test** (v2 §10): set `amount = 150` in `coordinator.py`; expect Bank A **NO**, decision **ABORT**, on-chain `getDecision` returns **`2`**, balances unchanged.

---

## Quick reference — deploy (MetaMask)

From `lab-2pc-blockchain/`:

```bash
forge build
python3 scripts/sync_deploy_artifact.py
./deploy/serve.sh 8787
# Browser → http://127.0.0.1:8787 → Connect → Deploy → copy address to .env
```

## Quick reference — `cast` / coordinator

After `CONTRACT_ADDRESS` is set:

```bash
set -a && source .env && set +a
cast call "$CONTRACT_ADDRESS" "getDecision(string)(uint8)" "tx-…" --rpc-url "$SEPOLIA_RPC_URL"
```

---

## Legend

- `[x]` — done.
- `[ ]` — not done.

When you finish a row, change `[ ]` to `[x]` in this file.
