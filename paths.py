import os
import sys
import shutil

APP_NAME = "D2RMarketplace"


def get_resource_base_dir():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_path(*parts):
    return os.path.join(get_resource_base_dir(), *parts)


def get_user_data_dir():
    local_appdata = os.environ.get("LOCALAPPDATA")
    if not local_appdata:
        local_appdata = os.path.expanduser(r"~\AppData\Local")

    path = os.path.join(local_appdata, APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def get_user_data_path(*parts):
    path = os.path.join(get_user_data_dir(), *parts)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    return path


def ensure_default_file(relative_path: str):
    source = get_resource_path(*relative_path.split("/"))
    target = get_user_data_path(*relative_path.split("/"))

    if not os.path.exists(target):
        if not os.path.exists(source):
            raise FileNotFoundError(f"Default resource not found: {source}")
        shutil.copy2(source, target)

    return target