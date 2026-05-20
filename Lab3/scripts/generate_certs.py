#!/usr/bin/env python3
"""Generate self-signed TLS certificate for the QUIC lab server (with SAN)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CERTS = ROOT / "certs"
CERT = CERTS / "cert.pem"
KEY = CERTS / "key.pem"

# QUIC/TLS requires subjectAltName (not only CN).
# Do not use DNS:127.0.0.1 — IPs belong in IP: entries only.
SAN = "subjectAltName=DNS:localhost,DNS:server,IP:127.0.0.1,IP:0.0.0.0"


def main() -> int:
    CERTS.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "openssl",
            "req",
            "-new",
            "-x509",
            "-days",
            "365",
            "-nodes",
            "-out",
            str(CERT),
            "-keyout",
            str(KEY),
            "-subj",
            "/CN=localhost",
            "-addext",
            SAN,
        ],
        check=True,
    )
    print(f"Wrote {CERT} and {KEY}")
    print(f"SAN: {SAN}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FileNotFoundError:
        print("openssl not found. Install OpenSSL.", file=sys.stderr)
        raise SystemExit(1) from None
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from exc
