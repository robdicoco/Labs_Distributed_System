#!/usr/bin/env python3
"""2PC coordinator: PREPARE / COMMIT|ABORT over TCP, then recordDecision on Sepolia."""

from __future__ import annotations

import json
import os
import socket
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from eth_account import Account
from web3 import Web3

# Change to 150 for the ABORT lab test (Banco A balance is 100).
AMOUNT = 50

PARTICIPANTS = [
    {"name": "Banco A", "host": "127.0.0.1", "port": 5001},
    {"name": "Banco B", "host": "127.0.0.1", "port": 5002},
]

ROOT = Path(__file__).resolve().parent
ABI_PATH = ROOT / "out" / "CommitLog.sol" / "CommitLog.json"
SEPOLIA_CHAIN_ID = 11155111


def send_message(participant: dict, message: dict) -> dict:
    with socket.create_connection(
        (participant["host"], participant["port"]), timeout=10
    ) as sock:
        sock.sendall(json.dumps(message).encode())
        raw = sock.recv(65536).decode()
    return json.loads(raw)


def load_contract_abi() -> list:
    if not ABI_PATH.is_file():
        print("Run `forge build` first. Missing:", ABI_PATH, file=sys.stderr)
        sys.exit(1)
    artifact = json.loads(ABI_PATH.read_text(encoding="utf-8"))
    return artifact["abi"]


def normalize_private_key(key: str) -> str:
    key = key.strip()
    return key if key.startswith("0x") else f"0x{key}"


def build_web3_contract():
    load_dotenv(ROOT / ".env")

    rpc_url = os.getenv("SEPOLIA_RPC_URL")
    contract_address = os.getenv("CONTRACT_ADDRESS")
    private_key = os.getenv("PRIVATE_KEY")

    missing = [
        name
        for name, val in [
            ("SEPOLIA_RPC_URL", rpc_url),
            ("CONTRACT_ADDRESS", contract_address),
            ("PRIVATE_KEY", private_key),
        ]
        if not val
    ]
    if missing:
        print(
            "Set in .env:",
            ", ".join(missing),
            file=sys.stderr,
        )
        print(
            "PRIVATE_KEY is the coordinator signer (Sepolia test wallet). "
            "Deploy uses MetaMask; recording decisions uses this key.",
            file=sys.stderr,
        )
        sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print("Cannot connect to SEPOLIA_RPC_URL", file=sys.stderr)
        sys.exit(1)

    account = Account.from_key(normalize_private_key(private_key))
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(contract_address),
        abi=load_contract_abi(),
    )
    return w3, account, contract


def record_on_chain(
    w3: Web3, account: Account, contract, transaction_id: str, decision: str
) -> str:
    blockchain_decision = 1 if decision == "COMMIT" else 2

    fn = contract.functions.recordDecision(transaction_id, blockchain_decision)
    nonce = w3.eth.get_transaction_count(account.address)
    gas_estimate = fn.estimate_gas({"from": account.address})

    tx = fn.build_transaction(
        {
            "from": account.address,
            "nonce": nonce,
            "chainId": SEPOLIA_CHAIN_ID,
            "gas": int(gas_estimate * 1.2),
        }
    )

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt["status"] != 1:
        raise RuntimeError(f"Transaction failed: {tx_hash.hex()}")

    return tx_hash.hex()


def run_2pc() -> None:
    transaction_id = f"tx-{int(time.time() * 1000)}"

    print(f"\nIniciando transação {transaction_id}")
    print(f"Transferência: Banco A -> Banco B | Valor: {AMOUNT}")

    votes: list[str] = []
    for participant in PARTICIPANTS:
        response = send_message(
            participant,
            {"type": "PREPARE", "transactionId": transaction_id, "amount": AMOUNT},
        )
        vote = response["vote"]
        print(f"[Coordenador] Voto de {participant['name']}: {vote}")
        votes.append(vote)

    decision = "COMMIT" if all(v == "YES" for v in votes) else "ABORT"
    print(f"[Coordenador] Decisão final: {decision}")

    for participant in PARTICIPANTS:
        send_message(
            participant,
            {
                "type": decision,
                "transactionId": transaction_id,
                "amount": AMOUNT,
            },
        )

    print("[Coordenador] Registrando decisão na Sepolia...")
    w3, account, contract = build_web3_contract()
    tx_hash = record_on_chain(w3, account, contract, transaction_id, decision)

    print("[Coordenador] Decisão registrada na blockchain.")
    print("Hash da transação:", tx_hash)
    print("transactionId (use with cast):", transaction_id)


def main() -> None:
    try:
        run_2pc()
    except Exception as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
