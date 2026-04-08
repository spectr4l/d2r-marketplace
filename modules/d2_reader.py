import json
import os
import subprocess
import sys


def get_resource_base_dir():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_node_cmd():
    base_dir = get_resource_base_dir()

    if getattr(sys, "frozen", False):
        return os.path.join(base_dir, "tools", "node", "node.exe")

    return "node"


def get_parser_dir():
    base_dir = get_resource_base_dir()
    return os.path.join(base_dir, "tools", "d2r_parser")


def get_reader_file():
    return os.path.join(get_parser_dir(), "read_shared_stash.cjs")


def read_shared_stash(stash_path: str) -> dict:
    node_cmd = get_node_cmd()
    parser_dir = get_parser_dir()
    reader_file = get_reader_file()

    if not os.path.isfile(stash_path):
        raise FileNotFoundError(f"Shared stash not found: {stash_path}")

    if getattr(sys, "frozen", False) and not os.path.isfile(node_cmd):
        raise FileNotFoundError(f"Embedded Node not found: {node_cmd}")

    if not os.path.isdir(parser_dir):
        raise FileNotFoundError(f"Parser directory not found: {parser_dir}")

    if not os.path.isfile(reader_file):
        raise FileNotFoundError(f"Node reader not found: {reader_file}")

    startupinfo = None
    creationflags = 0

    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        creationflags = subprocess.CREATE_NO_WINDOW

    result = subprocess.run(
        [node_cmd, reader_file, stash_path],
        cwd=parser_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        startupinfo=startupinfo,
        creationflags=creationflags,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Failed to read shared stash.\n"
            f"NODE_CMD={node_cmd}\n"
            f"READER_FILE={reader_file}\n"
            f"PARSER_DIR={parser_dir}\n"
            f"stdout={result.stdout}\n"
            f"stderr={result.stderr}"
        )

    payload = json.loads(result.stdout)

    if not payload.get("success"):
        raise RuntimeError(f"Reader returned an error: {payload}")

    return payload