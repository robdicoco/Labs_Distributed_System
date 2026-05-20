#!/usr/bin/env python3
"""Banco B — participant on port 5002 (initial balance 20)."""

from __future__ import annotations

from bank_common import run_bank_server

HOST = "127.0.0.1"
PORT = 5002
INITIAL_BALANCE = 20


def handle_message(balance: int, msg: dict) -> tuple[int, dict]:
    msg_type = msg.get("type")

    if msg_type == "PREPARE":
        print("[Banco B] PREPARE recebido")
        return balance, {"vote": "YES"}

    if msg_type == "COMMIT":
        amount = int(msg["amount"])
        balance += amount
        print(f"[Banco B] COMMIT. Novo saldo: {balance}")
        return balance, {"status": "OK"}

    if msg_type == "ABORT":
        print("[Banco B] ABORT. Nenhuma alteração feita.")
        return balance, {"status": "OK"}

    raise ValueError(f"Unknown message type: {msg_type!r}")


def main() -> None:
    run_bank_server(HOST, PORT, "Banco B", INITIAL_BALANCE, handle_message)


if __name__ == "__main__":
    main()
