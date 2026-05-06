# Action Plan: Lab 2PC + Sepolia (Foundry / Forge)

This document mirrors [Hands On Sepolia.md](./Task/Hands%20On%20Sepolia.md) and maps each step to **Foundry (`forge`)** instead of **Hardhat + npm**. The 2PC **coordinator and bank processes** are implemented with **Python** (stdlib `socket` + **`web3.py`**), not JavaScript. Forge only replaces contract compile/deploy.

**Why Python instead of Node:** The lab’s banks and coordinator are plain TCP + JSON-RPC. Any language with sockets and an Ethereum client works. Common choices: **Python** (`web3.py`), **Rust** (`ethers-rs` / `alloy`), **Go** (`go-ethereum`). This plan uses **Python** to avoid `node`/npm in the 2PC layer.

**Repository status:** Phase A is implemented under `lab-2pc-blockchain/` (Forge project + `CommitLog`). Phases B–D are still **unchecked** until you deploy and add the Python layer.

---

## Review: Hardhat → Forge equivalence

| Lab section (Hardhat) | Forge equivalent |
|------------------------|------------------|
| `mkdir` + `npm init` + `npx hardhat init` | `mkdir lab-2pc-blockchain && cd lab-2pc-blockchain && forge init --no-git` (add `--force` if directory non-empty) |
| `contracts/CommitLog.sol` | `src/CommitLog.sol` (Foundry default layout) |
| `hardhat.config.js` (Solidity 0.8.24, Sepolia) | `foundry.toml`: `solc = "0.8.24"` and `[rpc_endpoints] sepolia = "${SEPOLIA_RPC_URL}"` |
| `npx hardhat compile` | `forge build` |
| `scripts/deploy.js` + `hardhat run --network sepolia` | `forge create src/CommitLog.sol:CommitLog --rpc-url sepolia --broadcast` **or** a `forge script` under `script/Deploy.s.sol` with `vm.startBroadcast()` |
| `package.json` + `ethers` for coordinator | **Python:** `pip install web3 python-dotenv` (venv recommended). Use `Web3(Web3.HTTPProvider(...))` and `w3.eth.contract(address=..., abi=...)` to call `recordDecision` / `getDecision`. |
| ABI for `ethers.Contract` | After `forge build`: `out/CommitLog.sol/CommitLog.json` → `json.load` the file and pass `artifact["abi"]` into `w3.eth.contract`. |

**Environment variables:** Keep the same `.env` idea (`SEPOLIA_RPC_URL`, `PRIVATE_KEY`, `CONTRACT_ADDRESS`). Forge resolves `${VAR}` in `foundry.toml` for RPC endpoints when you pass `--rpc-url sepolia` if `sepolia` is defined there, or use `forge ... --rpc-url "$SEPOLIA_RPC_URL"` directly.

**Coordinator ABI / enum values:** On-chain, `Decision` is `UNKNOWN=0`, `COMMIT=1`, `ABORT=2` (same as the JS lab). Either use the full ABI from `out/.../CommitLog.json` or a minimal ABI fragment; `web3.py` encodes `recordDecision(transactionId, decision)` the same way as ethers.

---

## Phase A — Foundry project and contract

- [x] Create project directory (e.g. `lab-2pc-blockchain`) and `cd` into it.
- [x] Run `forge init` (use `--no-git` if you manage git at a parent repo).
- [x] Remove default `src/Counter.sol` (and related tests/scripts) if you want a minimal tree, or leave and add `CommitLog` alongside—your choice.
- [x] Add `src/CommitLog.sol` with the **same** contract code as in Hands On Sepolia (pragma `^0.8.24`, enum `Decision`, `recordDecision`, `getDecision`, events).
- [x] Add `foundry.toml`: set `solc` / `solc_version` to **0.8.24** (match lab).
- [x] Configure Sepolia RPC in `foundry.toml` under `[rpc_endpoints]` as `sepolia = "${SEPOLIA_RPC_URL}"` (or rely on shell env only).

## Phase B — Secrets and deploy

- [ ] Create `.env` with `SEPOLIA_RPC_URL`, `PRIVATE_KEY` (no `0x` prefix is common for Foundry; if yours has `0x`, be consistent with tooling), and empty `CONTRACT_ADDRESS` until deployed.
- [ ] Load env in shell (`set -a && source .env && set +a`) or use a wrapper before `forge` commands.
- [ ] Run `forge build` and fix any compiler errors.
- [ ] Deploy to Sepolia: either `forge create ... --rpc-url sepolia --account` / `--private-key` per Foundry docs, **or** implement `script/Deploy.s.sol` and run `forge script ... --rpc-url sepolia --broadcast`.
- [ ] Copy the deployed contract address into `.env` as `CONTRACT_ADDRESS`.

## Phase C — Python 2PC layer (same protocol as the lab, no Node)

- [ ] Create a venv (recommended): `python -m venv .venv && source .venv/bin/activate`.
- [ ] Install deps: `pip install web3 python-dotenv` (pin versions in `requirements.txt` if you like).
- [ ] Add `bank_a.py`, `bank_b.py`: `socketserver` or `socket` listening on **5001** / **5002**; on receive, `json.loads`, handle `PREPARE` / `COMMIT` / `ABORT` like the JS lab (balances 100 and 20, amount check on A).
- [ ] Add `coordinator.py`: `dotenv` → `.env`; `send_message` using `socket.create_connection((host, port))` + JSON `str`/`bytes`; after 2PC, build/send `recordDecision` via **web3.py** (`build_transaction` → `sign_transaction` → `send_raw_transaction` → `wait_for_transaction_receipt`). Use **`COMMIT` → 1**, **`ABORT` → 2** for the uint8 argument.
- [ ] Load ABI from `out/CommitLog.sol/CommitLog.json` (`json.load` → `artifact["abi"]`) relative to your Forge project, or duplicate a minimal ABI list in Python.

## Phase D — Run and verify

- [ ] Terminal 1: `python bank_a.py` (from venv if used).
- [ ] Terminal 2: `python bank_b.py`
- [ ] Terminal 3: `python coordinator.py`
- [ ] Confirm logs: YES/YES → COMMIT and transaction hash on Sepolia.
- [ ] Run **ABORT test**: set `amount = 150` in `coordinator.py`, rerun; expect NO from Bank A, ABORT, and on-chain record still written with ABORT enum value.

---

## Quick reference commands (Forge)

After `.env` is loaded:

```bash
forge build
forge create src/CommitLog.sol:CommitLog --rpc-url sepolia --broadcast --private-key "$PRIVATE_KEY"
```

(Exact flags may vary by Foundry version; use `forge create --help` if your CLI uses different option names.)

---

## Legend

- `[x]` — done (mark yourself when completed).
- `[ ]` — not done.

When you finish a row, change `[ ]` to `[x]` in this file.
