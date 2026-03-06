#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "generate_blog_visuals.py"


def main() -> int:
    print("Deprecated: use scripts/generate_blog_visuals.py instead.")
    return subprocess.call([sys.executable, str(TARGET), *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())
