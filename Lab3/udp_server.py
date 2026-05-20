#!/usr/bin/env python3
"""UDP echo server: PING/ACK datagrams until BYE."""

import signal
import socket
import sys

HOST = "0.0.0.0"
PORT = 5001

_running = True


def _stop(*_args: object) -> None:
    global _running
    _running = False


def main() -> None:
    global _running
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))
    server.settimeout(1.0)
    print(f"[UDP] Escutando em {HOST}:{PORT}")

    try:
        while _running:
            try:
                data, addr = server.recvfrom(1024)
            except socket.timeout:
                continue
            except OSError:
                if not _running:
                    break
                raise

            if data == b"BYE":
                server.sendto(b"OK", addr)
                print(f"[UDP] BYE de {addr}")
                break
            server.sendto(b"ACK", addr)
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        print(f"[UDP] Porta {PORT} libertada.")


if __name__ == "__main__":
    main()
