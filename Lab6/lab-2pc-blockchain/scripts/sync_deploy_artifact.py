#!/usr/bin/env python3
"""Copy CommitLog ABI + creation bytecode from Forge output into deploy/artifact.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "out" / "CommitLog.sol" / "CommitLog.json"
DEST = ROOT / "deploy" / "artifact.json"


def main() -> int:
    if not SOURCE.is_file():
        print("Run `forge build` first. Missing:", SOURCE, file=sys.stderr)
        return 1

    artifact = json.loads(SOURCE.read_text(encoding="utf-8"))
    bytecode = artifact.get("bytecode", {}).get("object")
    if not bytecode or bytecode == "0x":
        print("No creation bytecode in artifact. Run `forge build`.", file=sys.stderr)
        return 1

    DEST.parent.mkdir(parents=True, exist_ok=True)
    payload = {"abi": artifact["abi"], "bytecode": bytecode}
    DEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("Wrote", DEST)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
