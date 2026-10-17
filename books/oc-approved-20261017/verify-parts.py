#!/usr/bin/env python3
"""Read-only identity verification. Does not regenerate declarations or expected hashes."""
from pathlib import Path
import subprocess, sys
root=Path(__file__).resolve().parents[2]
sys.exit(subprocess.call(['npm','run','asset:check','--','--root',str(root)],cwd=root))
