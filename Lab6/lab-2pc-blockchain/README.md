## Lab 2PC + Sepolia — `lab-2pc-blockchain`

Foundry project for **CommitLog** on Sepolia. Contract deployment is done in the browser with **MetaMask** (no private key in shell commands).

### Prerequisites

- [Foundry](https://book.getfoundry.sh/getting-started/installation) (`forge`, `cast`)
- [MetaMask](https://metamask.io/) with **Sepolia** network and test ETH
- Python 3 (artifact sync + later 2PC coordinator)

### Build

```shell
forge build
python3 scripts/sync_deploy_artifact.py
```

### Deploy with MetaMask

1. Serve the deploy UI (must be `http://`, not `file://`):

```shell
chmod +x deploy/serve.sh
./deploy/serve.sh 8787
```

2. Open **http://127.0.0.1:8787** in a browser where MetaMask is installed.

3. Click **Connect MetaMask** → approve connection → switch/add **Sepolia** if prompted.

4. Click **Deploy CommitLog** → confirm the transaction in MetaMask.

5. Copy the printed contract address into `.env`:

```shell
cp .env.example .env
# edit .env:
# CONTRACT_ADDRESS=0x...
```

`SEPOLIA_RPC_URL` is still needed for `cast` and the Python coordinator; it is not used by the deploy page (MetaMask uses its own RPC).

### Verify on Sepolia (`cast`)

```shell
set -a && source .env && set +a

cast call "$CONTRACT_ADDRESS" \
  "getDecision(string)(uint8)" \
  "tx-your-id" \
  --rpc-url "$SEPOLIA_RPC_URL"
```

### Local / CI only (`forge script`)

`script/Deploy.s.sol` remains for Anvil or scripted tests. Do **not** use `--private-key` for normal lab deploys.

```shell
# Example: local Anvil with unlocked account — not Sepolia + MetaMask
anvil &
forge script script/Deploy.s.sol:DeployScript --rpc-url http://127.0.0.1:8545 --broadcast --unlocked
```

### Other commands

```shell
forge test
forge fmt
```

Documentation: https://book.getfoundry.sh/
