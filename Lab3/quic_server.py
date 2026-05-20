#!/usr/bin/env python3
"""QUIC echo server (TLS 1.3) — PING/ACK on one stream until BYE."""

from __future__ import annotations

import asyncio
import signal

from aioquic.asyncio import QuicConnectionProtocol, serve
from aioquic.quic.events import StreamDataReceived

from quic_common import PAYLOAD, REPLY, server_configuration

HOST = "0.0.0.0"
PORT = 5002


class EchoProtocol(QuicConnectionProtocol):
    def quic_event_received(self, event) -> None:
        if not isinstance(event, StreamDataReceived):
            return

        if event.data == PAYLOAD:
            self._quic.send_stream_data(event.stream_id, REPLY)
        elif event.data == b"BYE":
            self._quic.send_stream_data(event.stream_id, b"OK")


async def main() -> None:
    configuration = server_configuration()
    await serve(
        HOST,
        PORT,
        configuration=configuration,
        create_protocol=EchoProtocol,
    )
    print(f"[QUIC] Escutando em {HOST}:{PORT} (TLS + QUIC)")
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)
    try:
        await stop.wait()
    finally:
        print(f"[QUIC] Porta {PORT} libertada.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
