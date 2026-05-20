#!/usr/bin/env python3
"""Banco A — participant on port 5001 (initial balance 100)."""

from __future__ import annotations

from bank_common import run_bank_server

HOST = "127.0.0.1"
PORT = 5001
INITIAL_BALANCE = 100


def handle_message(balance: int, msg: dict) -> tuple[int, dict]:
    msg_type = msg.get("type")

    if msg_type == "PREPARE":
        print("[Banco A] PREPARE recebido")
        amount = int(msg["amount"])
        vote = "YES" if balance >= amount else "NO"
        return balance, {"vote": vote}

    if msg_type == "COMMIT":
        amount = int(msg["amount"])
        balance -= amount
        print(f"[Banco A] COMMIT. Novo saldo: {balance}")
        return balance, {"status": "OK"}

    if msg_type == "ABORT":
        print("[Banco A] ABORT. Nenhuma alteração feita.")
        return balance, {"status": "OK"}

    raise ValueError(f"Unknown message type: {msg_type!r}")


def main() -> None:
    run_bank_server(HOST, PORT, "Banco A", INITIAL_BALANCE, handle_message)


if __name__ == "__main__":
    main()
