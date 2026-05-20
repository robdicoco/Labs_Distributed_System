#!/usr/bin/env python3
"""Compare round-trip latency: TCP vs UDP vs QUIC."""

from __future__ import annotations

import argparse
import asyncio
import os
import socket
import statistics
import time

from aioquic.asyncio import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.events import StreamDataReceived

from quic_common import PAYLOAD, REPLY, client_configuration

HOST_DEFAULT = os.environ.get("SERVER_HOST", "127.0.0.1")
TCP_PORT_DEFAULT = 5000
UDP_PORT_DEFAULT = 5001
QUIC_PORT_DEFAULT = 5002


def bench_tcp(host: str, port: int, rounds: int) -> list[float]:
    latencies: list[float] = []

    with socket.create_connection((host, port), timeout=10) as sock:
        for _ in range(rounds):
            t0 = time.perf_counter()
            sock.sendall(PAYLOAD)
            reply = sock.recv(1024)
            latencies.append(time.perf_counter() - t0)
            if reply != REPLY:
                raise RuntimeError(f"TCP: unexpected reply {reply!r}")
        sock.sendall(b"BYE")

    return latencies


def bench_udp(host: str, port: int, rounds: int) -> list[float]:
    latencies: list[float] = []

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(10)
        server_addr = (host, port)

        for _ in range(rounds):
            t0 = time.perf_counter()
            sock.sendto(PAYLOAD, server_addr)
            reply, _ = sock.recvfrom(1024)
            latencies.append(time.perf_counter() - t0)
            if reply != REPLY:
                raise RuntimeError(f"UDP: unexpected reply {reply!r}")

        sock.sendto(b"BYE", server_addr)
        sock.recvfrom(1024)

    return latencies


class QuicBenchProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._responses: asyncio.Queue[bytes] = asyncio.Queue()

    def quic_event_received(self, event) -> None:
        if isinstance(event, StreamDataReceived):
            self._responses.put_nowait(event.data)


async def _bench_quic_async(host: str, port: int, rounds: int) -> list[float]:
    configuration = client_configuration()
    latencies: list[float] = []

    async with connect(
        host,
        port,
        configuration=configuration,
        create_protocol=QuicBenchProtocol,
    ) as protocol:
        stream_id = protocol._quic.get_next_available_stream_id(is_unidirectional=False)

        for _ in range(rounds):
            t0 = time.perf_counter()
            protocol._quic.send_stream_data(stream_id, PAYLOAD)
            reply = await asyncio.wait_for(protocol._responses.get(), timeout=10.0)
            latencies.append(time.perf_counter() - t0)
            if reply != REPLY:
                raise RuntimeError(f"QUIC: unexpected reply {reply!r}")

        protocol._quic.send_stream_data(stream_id, b"BYE")
        await asyncio.wait_for(protocol._responses.get(), timeout=10.0)

    return latencies


def bench_quic(host: str, port: int, rounds: int) -> list[float]:
    return asyncio.run(_bench_quic_async(host, port, rounds))


def summarize(name: str, latencies: list[float]) -> dict:
    return {
        "name": name,
        "rounds": len(latencies),
        "total_s": sum(latencies),
        "avg_ms": statistics.mean(latencies) * 1000,
        "min_ms": min(latencies) * 1000,
        "max_ms": max(latencies) * 1000,
        "median_ms": statistics.median(latencies) * 1000,
    }


def print_report(rows: list[dict]) -> None:
    print()
    print(
        f"{'Protocolo':<8} {'Rounds':>8} {'Total (s)':>12} "
        f"{'Média (ms)':>12} {'Mediana':>10} {'Min':>10} {'Max':>10}"
    )
    print("-" * 72)
    for row in rows:
        print(
            f"{row['name']:<8} {row['rounds']:>8} {row['total_s']:>12.4f} "
            f"{row['avg_ms']:>12.3f} {row['median_ms']:>10.3f} "
            f"{row['min_ms']:>10.3f} {row['max_ms']:>10.3f}"
        )
    print()
    fastest = min(rows, key=lambda r: r["avg_ms"])
    others = [r for r in rows if r is not fastest]
    for other in others:
        ratio = other["avg_ms"] / fastest["avg_ms"]
        print(
            f"{fastest['name']} vs {other['name']}: "
            f"{fastest['avg_ms']:.3f} ms vs {other['avg_ms']:.3f} ms ({ratio:.2f}×)"
        )
    print(f"\nMais rápido em média (RTT): {fastest['name']}")
    print("(Loopback local; QUIC usa TLS 1.3 + UDP. Resultados variam com carga e rounds.)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare TCP vs UDP vs QUIC round-trip time"
    )
    parser.add_argument("--host", default=HOST_DEFAULT, help="Server host")
    parser.add_argument("--tcp-port", type=int, default=TCP_PORT_DEFAULT)
    parser.add_argument("--udp-port", type=int, default=UDP_PORT_DEFAULT)
    parser.add_argument("--quic-port", type=int, default=QUIC_PORT_DEFAULT)
    parser.add_argument(
        "--rounds",
        type=int,
        default=1000,
        help="Number of PING/ACK exchanges per protocol",
    )
    parser.add_argument(
        "--skip-quic",
        action="store_true",
        help="Skip QUIC (if certs or server unavailable)",
    )
    args = parser.parse_args()

    if args.rounds < 1:
        raise SystemExit("--rounds must be >= 1")

    print(f"Host: {args.host} | Rounds: {args.rounds}")
    print("Start tcp_server.py, udp_server.py and quic_server.py before running.\n")

    rows: list[dict] = []

    print("[Cliente] TCP benchmark…")
    rows.append(summarize("TCP", bench_tcp(args.host, args.tcp_port, args.rounds)))

    print("[Cliente] UDP benchmark…")
    rows.append(summarize("UDP", bench_udp(args.host, args.udp_port, args.rounds)))

    if not args.skip_quic:
        print("[Cliente] QUIC benchmark…")
        try:
            rows.append(
                summarize("QUIC", bench_quic(args.host, args.quic_port, args.rounds))
            )
        except FileNotFoundError as exc:
            print(f"[Cliente] QUIC skipped: {exc}")
        except Exception as exc:
            print(f"[Cliente] QUIC failed: {exc}")
            raise

    print_report(rows)


if __name__ == "__main__":
    main()
