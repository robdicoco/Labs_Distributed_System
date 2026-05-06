# Action Plan: Lab 2PC + Sepolia (Foundry / Forge)

This document mirrors [Hands On Sepolia.md](./Hands%20On%20Sepolia.md) and maps each step to **Foundry (`forge`)** instead of **Hardhat + npm**. The 2PC **coordinator and bank processes** stay as **Node.js** TCP servers/clients (Forge does not replace that layer; it replaces contract tooling and deployment).

**Repository status:** Lab6 currently contains only the task markdown. All Forge-related implementation checks below are **unchecked** until you create files and run commands locally.

---

## Review: Hardhat → Forge equivalence

| Lab section (Hardhat) | Forge equivalent |
|------------------------|------------------|
| `mkdir` + `npm init` + `npx hardhat init` | `mkdir lab-2pc-blockchain && cd lab-2pc-blockchain && forge init --no-git` (add `--force` if directory non-empty) |
| `contracts/CommitLog.sol` | `src/CommitLog.sol` (Foundry default layout) |
| `hardhat.config.js` (Solidity 0.8.24, Sepolia) | `foundry.toml`: `solc = "0.8.24"` and `[rpc_endpoints] sepolia = "${SEPOLIA_RPC_URL}"` |
| `npx hardhat compile` | `forge build` |
| `scripts/deploy.js` + `hardhat run --network sepolia` | `forge create src/CommitLog.sol:CommitLog --rpc-url sepolia --broadcast` **or** a `forge script` under `script/Deploy.s.sol` with `vm.startBroadcast()` |
| `package.json` + `ethers` for coordinator | Still use `npm init -y`, `npm install ethers dotenv` in project root (or a `coordinator/` subfolder) for `coordinator.js` only; no Hardhat dependency required |
| ABI for `ethers.Contract` | After `forge build`: `out/CommitLog.sol/CommitLog.json` → use the `abi` field, or paste minimal ABI as in the lab |

**Environment variables:** Keep the same `.env` idea (`SEPOLIA_RPC_URL`, `PRIVATE_KEY`, `CONTRACT_ADDRESS`). Forge resolves `${VAR}` in `foundry.toml` for RPC endpoints when you pass `--rpc-url sepolia` if `sepolia` is defined there, or use `forge ... --rpc-url "$SEPOLIA_RPC_URL"` directly.

**Coordinator ABI:** The lab uses `uint8` for `recordDecision` / `getDecision` to match enum wire encoding. With Forge-generated types, enum is still encoded as `uint8`; your existing `coordinator.js` ABI strings remain valid.

---

## Phase A — Foundry project and contract

- [ ] Create project directory (e.g. `lab-2pc-blockchain`) and `cd` into it.
- [ ] Run `forge init` (use `--no-git` if you manage git at a parent repo).
- [ ] Remove default `src/Counter.sol` (and related tests/scripts) if you want a minimal tree, or leave and add `CommitLog` alongside—your choice.
- [ ] Add `src/CommitLog.sol` with the **same** contract code as in Hands On Sepolia (pragma `^0.8.24`, enum `Decision`, `recordDecision`, `getDecision`, events).
- [ ] Add `foundry.toml`: set `solc` / `solc_version` to **0.8.24** (match lab).
- [ ] Configure Sepolia RPC in `foundry.toml` under `[rpc_endpoints]` as `sepolia = "${SEPOLIA_RPC_URL}"` (or rely on shell env only).

## Phase B — Secrets and deploy

- [ ] Create `.env` with `SEPOLIA_RPC_URL`, `PRIVATE_KEY` (no `0x` prefix is common for Foundry; if yours has `0x`, be consistent with tooling), and empty `CONTRACT_ADDRESS` until deployed.
- [ ] Load env in shell (`set -a && source .env && set +a`) or use a wrapper before `forge` commands.
- [ ] Run `forge build` and fix any compiler errors.
- [ ] Deploy to Sepolia: either `forge create ... --rpc-url sepolia --account` / `--private-key` per Foundry docs, **or** implement `script/Deploy.s.sol` and run `forge script ... --rpc-url sepolia --broadcast`.
- [ ] Copy the deployed contract address into `.env` as `CONTRACT_ADDRESS`.

## Phase C — Node.js 2PC layer (unchanged logic, no Hardhat)

- [ ] `npm init -y` and `npm install ethers dotenv` (omit Hardhat packages).
- [ ] Add `bankA.js`, `bankB.js` as in the lab (TCP ports 5001 / 5002)—no change required for Forge.
- [ ] Add `coordinator.js` as in the lab, ensuring `CONTRACT_ADDRESS` and `SEPOLIA_RPC_URL` / wallet match your Forge deployment.
- [ ] Optional: load ABI from `out/CommitLog.sol/CommitLog.json` with `JSON.parse(fs.readFileSync(...))` instead of inline `abi` array.

## Phase D — Run and verify

- [ ] Terminal 1: `node bankA.js`
- [ ] Terminal 2: `node bankB.js`
- [ ] Terminal 3: `node coordinator.js`
- [ ] Confirm logs: YES/YES → COMMIT and transaction hash on Sepolia.
- [ ] Run **ABORT test**: set `amount = 150` in `coordinator.js`, rerun; expect NO from Bank A, ABORT, and on-chain record still written with ABORT enum value.

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
