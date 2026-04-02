import json
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARSER_DIR = os.path.join(BASE_DIR, "tools", "d2r_parser")
READER_FILE = os.path.join(PARSER_DIR, "read_shared_stash.cjs")
NODE_CMD = "node"


def read_shared_stash(stash_path: str) -> dict:
    if not os.path.isfile(stash_path):
        raise FileNotFoundError(f"Shared stash not found: {stash_path}")

    if not os.path.isfile(READER_FILE):
        raise FileNotFoundError(f"Node reader not found: {READER_FILE}")

    result = subprocess.run(
        [NODE_CMD, READER_FILE, stash_path],
        cwd=PARSER_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Failed to read shared stash.\n"
            f"stdout={result.stdout}\n"
            f"stderr={result.stderr}"
        )

    payload = json.loads(result.stdout)

    if not payload.get("success"):
        raise RuntimeError(f"Reader returned an error: {payload}")

    return payload