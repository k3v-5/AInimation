#!/usr/bin/env python3
"""Root alias for scripts/verify_pipeline.py."""
import sys
from pathlib import Path

# Add project root and invoke scripts/verify_pipeline
scripts_verify = Path(__file__).resolve().parent / "scripts" / "verify_pipeline.py"
if scripts_verify.exists():
    with open(scripts_verify, "r", encoding="utf-8") as f:
        code = f.read()
    exec(compile(code, str(scripts_verify), "exec"))
else:
    sys.exit(1)
