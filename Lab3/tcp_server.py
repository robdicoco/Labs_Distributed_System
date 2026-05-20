#!/usr/bin/env python3
"""TCP echo server: one connection, many PING/ACK rounds until BYE."""

import signal
import socket
import sys

HOST = "0.0.0.0"
PORT = 5000

_running = True


def _stop(*_args: object) -> None:
    global _running
    _running = False


def main() -> None:
    global _running
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    server.settimeout(1.0)
    print(f"[TCP] Escutando em {HOST}:{PORT}")

    try:
        while _running:
            try:
                conn, addr = server.accept()
            except socket.timeout:
                continue
            except OSError:
                if not _running:
                    break
                raise

            print(f"[TCP] Ligação de {addr}")
            with conn:
                while _running:
                    data = conn.recv(1024)
                    if not data or data == b"BYE":
                        break
                    conn.sendall(b"ACK")
            print("[TCP] Ligação encerrada")
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        print(f"[TCP] Porta {PORT} libertada.")


if __name__ == "__main__":
    main()
