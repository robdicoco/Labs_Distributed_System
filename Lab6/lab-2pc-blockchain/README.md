## Foundry

**Foundry is a blazing fast, portable and modular toolkit for Ethereum application development written in Rust.**

Foundry consists of:

-   **Forge**: Ethereum testing framework (like Truffle, Hardhat and DappTools).
-   **Cast**: Swiss army knife for interacting with EVM smart contracts, sending transactions and getting chain data.
-   **Anvil**: Local Ethereum node, akin to Ganache, Hardhat Network.
-   **Chisel**: Fast, utilitarian, and verbose solidity REPL.

## Documentation

https://book.getfoundry.sh/

## Usage

### Build

```shell
$ forge build
```

### Test

```shell
$ forge test
```

### Format

```shell
$ forge fmt
```

### Gas Snapshots

```shell
$ forge snapshot
```

### Anvil

```shell
$ anvil
```

### Sepolia: env and deploy

1. Copy `.env.example` to `.env` and set `SEPOLIA_RPC_URL` and `PRIVATE_KEY`. Leave `CONTRACT_ADDRESS` empty until after deploy. With `load_dotenv = true` in `foundry.toml`, Forge loads `.env` when resolving `foundry.toml` placeholders (for example **`--rpc-url sepolia`**). For **`--private-key`**, export variables in your shell first:

```shell
set -a && source .env && set +a
```

2. Build and deploy **CommitLog** (Sepolia chain id **11155111**):

```shell
forge build
forge script script/Deploy.s.sol:DeployScript --rpc-url sepolia --broadcast --private-key "$PRIVATE_KEY" --slow
```

Optional: add `--verify` and set `ETHERSCAN_API_KEY` for contract verification on Etherscan.

3. Copy the printed **`CommitLog deployed at:`** address into `.env` as `CONTRACT_ADDRESS=` for the Python coordinator (Phase C).

Alternative one-shot deploy:

```shell
set -a && source .env && set +a
forge create src/CommitLog.sol:CommitLog --rpc-url sepolia --broadcast --private-key "$PRIVATE_KEY"
```

### Cast

```shell
$ cast <subcommand>
```

### Help

```shell
$ forge --help
$ anvil --help
$ cast --help
```
