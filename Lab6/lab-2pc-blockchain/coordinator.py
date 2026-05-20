#!/usr/bin/env python3
"""Coordinator HTTP server: runs 2PC via API; Sepolia signing in coordinator/index.html + MetaMask."""

from __future__ import annotations

import json
import mimetypes
import os
import signal
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

from coordinator_core import DEFAULT_AMOUNT, run_2pc

ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "coordinator"
ABI_PATH = ROOT / "out" / "CommitLog.sol" / "CommitLog.json"
HOST = "127.0.0.1"
PORT = 8788

_server: ThreadingHTTPServer | None = None


def load_env_config() -> dict:
    load_dotenv(ROOT / ".env")
    contract_address = os.getenv("CONTRACT_ADDRESS", "").strip()
    if not contract_address:
        raise ValueError("CONTRACT_ADDRESS is not set in .env")
    return {"contractAddress": contract_address}


def load_abi() -> list:
    if not ABI_PATH.is_file():
        raise FileNotFoundError(
            f"Missing {ABI_PATH}. Run: forge build"
        )
    artifact = json.loads(ABI_PATH.read_text(encoding="utf-8"))
    return artifact["abi"]


class CoordinatorHandler(BaseHTTPRequestHandler):
    server_version = "CoordinatorHTTP/1.0"

    def log_message(self, fmt: str, *args) -> None:
        print(f"[Coordenador] {self.address_string()} - {fmt % args}")

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, status: int, message: str) -> None:
        self._send_json(status, {"error": message})

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/api/config":
            try:
                self._send_json(200, load_env_config())
            except (ValueError, FileNotFoundError) as exc:
                self._send_error_json(500, str(exc))
            return

        if path == "/api/abi":
            try:
                self._send_json(200, {"abi": load_abi()})
            except FileNotFoundError as exc:
                self._send_error_json(500, str(exc))
            return

        if path == "/":
            path = "/index.html"

        file_path = (WEB_DIR / path.lstrip("/")).resolve()
        if not str(file_path).startswith(str(WEB_DIR.resolve())) or not file_path.is_file():
            self.send_error(404)
            return

        content = file_path.read_bytes()
        mime, _ = mimetypes.guess_type(str(file_path))
        self.send_response(200)
        self.send_header("Content-Type", mime or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        if path != "/api/2pc":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode() if length else "{}"
        try:
            body = json.loads(raw) if raw else {}
            amount = int(body.get("amount", DEFAULT_AMOUNT))
        except (json.JSONDecodeError, TypeError, ValueError):
            self._send_error_json(400, "Invalid JSON body; expected { \"amount\": number }")
            return

        try:
            result = run_2pc(amount)
            print(
                f"[Coordenador] 2PC {result['transactionId']}: "
                f"{result['decision']} (amount={amount})"
            )
            self._send_json(200, result)
        except OSError as exc:
            self._send_error_json(
                503,
                f"Cannot reach banks. Start bank_a.py and bank_b.py. ({exc})",
            )
        except Exception as exc:
            self._send_error_json(500, str(exc))


def _shutdown(*_args: object) -> None:
    global _server
    if _server:
        print("\n[Coordenador] A encerrar…")
        _server.shutdown()
    sys.exit(0)


def main() -> None:
    global _server

    if not WEB_DIR.is_dir():
        print("Missing coordinator/ web directory", file=sys.stderr)
        sys.exit(1)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    _server = ThreadingHTTPServer((HOST, PORT), CoordinatorHandler)
    print(f"[Coordenador] Abra http://{HOST}:{PORT}")
    print("[Coordenador] Ligue bank_a.py e bank_b.py antes de correr o 2PC.")
    try:
        _server.serve_forever()
    except KeyboardInterrupt:
        _shutdown()


if __name__ == "__main__":
    main()
