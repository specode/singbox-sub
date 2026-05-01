#!/usr/bin/env python3
import runpy
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
runpy.run_path(str(REPO_ROOT / "scripts" / "generate_config.py"), run_name="__main__")
