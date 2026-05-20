"""2PC protocol over TCP (no blockchain — signing happens in the browser)."""

from __future__ import annotations

import json
import socket
import time

PARTICIPANTS = [
    {"name": "Banco A", "host": "127.0.0.1", "port": 5001},
    {"name": "Banco B", "host": "127.0.0.1", "port": 5002},
]

DEFAULT_AMOUNT = 50


def send_message(participant: dict, message: dict) -> dict:
    with socket.create_connection(
        (participant["host"], participant["port"]), timeout=10
    ) as sock:
        sock.sendall(json.dumps(message).encode())
        raw = sock.recv(65536).decode()
    return json.loads(raw)


def run_2pc(amount: int = DEFAULT_AMOUNT) -> dict:
    transaction_id = f"tx-{int(time.time() * 1000)}"

    votes: list[dict] = []
    for participant in PARTICIPANTS:
        response = send_message(
            participant,
            {"type": "PREPARE", "transactionId": transaction_id, "amount": amount},
        )
        votes.append(
            {
                "name": participant["name"],
                "vote": response["vote"],
            }
        )

    decision = "COMMIT" if all(v["vote"] == "YES" for v in votes) else "ABORT"

    for participant in PARTICIPANTS:
        send_message(
            participant,
            {
                "type": decision,
                "transactionId": transaction_id,
                "amount": amount,
            },
        )

    return {
        "transactionId": transaction_id,
        "amount": amount,
        "votes": votes,
        "decision": decision,
        "blockchainDecision": 1 if decision == "COMMIT" else 2,
    }
