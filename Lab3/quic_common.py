"""Shared QUIC settings and TLS certificate paths for Lab 3."""

from __future__ import annotations

import ssl
from pathlib import Path

from aioquic.quic.configuration import QuicConfiguration

ROOT = Path(__file__).resolve().parent
CERTS_DIR = ROOT / "certs"
CERT_FILE = CERTS_DIR / "cert.pem"
KEY_FILE = CERTS_DIR / "key.pem"
ALPN = "lab3"

PAYLOAD = b"PING"
REPLY = b"ACK"


def ensure_certs() -> None:
    if CERT_FILE.is_file() and KEY_FILE.is_file():
        return
    raise FileNotFoundError(
        f"Missing TLS certs in {CERTS_DIR}. Run: uv run python scripts/generate_certs.py"
    )


def server_configuration() -> QuicConfiguration:
    ensure_certs()
    config = QuicConfiguration(
        alpn_protocols=[ALPN],
        is_client=False,
    )
    config.load_cert_chain(str(CERT_FILE), str(KEY_FILE))
    return config


def client_configuration() -> QuicConfiguration:
    ensure_certs()
    config = QuicConfiguration(
        alpn_protocols=[ALPN],
        is_client=True,
    )
    config.load_verify_locations(str(CERT_FILE))
    config.verify_mode = ssl.CERT_REQUIRED
    config.check_hostname = False
    return config
