import os
import socket
import sys
import threading
import time

import webview
from waitress import serve

from app import app

HOST = "127.0.0.1"
PORT = 5000


def wait_for_server(host: str, port: int, timeout: float = 15.0) -> bool:
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.2)

    return False


def run_server():
    serve(app, host=HOST, port=PORT, threads=4)


def hard_exit():
    os._exit(0)


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    if not wait_for_server(HOST, PORT):
        raise RuntimeError(f"Servidor não iniciou em http://{HOST}:{PORT}")

    window = webview.create_window(
        title="D2R Marketplace",
        url=f"http://{HOST}:{PORT}",
        width=1280,
        height=850,
        resizable=True,
    )

    window.events.closed += hard_exit

    webview.start()