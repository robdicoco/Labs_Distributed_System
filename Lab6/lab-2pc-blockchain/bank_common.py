"""TCP bank listener with graceful shutdown (releases port on Ctrl+C)."""

from __future__ import annotations

import json
import signal
import socket
from collections.abc import Callable

_shutdown = False


def _request_shutdown(*_args: object) -> None:
    global _shutdown
    _shutdown = True


def run_bank_server(
    host: str,
    port: int,
    bank_name: str,
    initial_balance: int,
    handle_message: Callable[[int, dict], tuple[int, dict]],
) -> None:
    global _shutdown
    _shutdown = False
    signal.signal(signal.SIGINT, _request_shutdown)
    signal.signal(signal.SIGTERM, _request_shutdown)

    balance = initial_balance
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    server.settimeout(1.0)

    print(f"[{bank_name}] Escutando na porta {port}")

    try:
        while not _shutdown:
            try:
                conn, _ = server.accept()
            except socket.timeout:
                continue
            except OSError:
                if _shutdown:
                    break
                raise

            with conn:
                try:
                    raw = conn.recv(65536).decode()
                    msg = json.loads(raw)
                    balance, reply = handle_message(balance, msg)
                    conn.sendall(json.dumps(reply).encode())
                except (ConnectionResetError, BrokenPipeError):
                    pass
    except KeyboardInterrupt:
        _request_shutdown()
    finally:
        try:
            server.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        server.close()
        print(f"[{bank_name}] Porta {port} libertada.")
