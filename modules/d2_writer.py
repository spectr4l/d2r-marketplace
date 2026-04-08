import os
import subprocess
import sys


def get_resource_base_dir():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_parser_dir():
    base_dir = get_resource_base_dir()
    return os.path.join(base_dir, "tools", "d2r_parser")


def get_patcher_file():
    return os.path.join(get_parser_dir(), "patch_stackable.cjs")


def get_node_cmd():
    if getattr(sys, "frozen", False):
        base_dir = get_resource_base_dir()
        return os.path.join(base_dir, "tools", "node", "node.exe")
    return "node"


ITEM_NAME_TO_CODE = {
    # Runes
    "el": "r01",
    "eld": "r02",
    "tir": "r03",
    "nef": "r04",
    "eth": "r05",
    "ith": "r06",
    "tal": "r07",
    "ral": "r08",
    "ort": "r09",
    "thul": "r10",
    "amn": "r11",
    "sol": "r12",
    "shael": "r13",
    "dol": "r14",
    "hel": "r15",
    "io": "r16",
    "lum": "r17",
    "ko": "r18",
    "fal": "r19",
    "lem": "r20",
    "pul": "r21",
    "um": "r22",
    "mal": "r23",
    "ist": "r24",
    "gul": "r25",
    "vex": "r26",
    "ohm": "r27",
    "lo": "r28",
    "sur": "r29",
    "ber": "r30",
    "jah": "r31",
    "cham": "r32",
    "zod": "r33",

    # Gems
    "chipped amethyst": "gcv",
    "chipped diamond": "gcw",
    "chipped emerald": "gcg",
    "chipped ruby": "gcr",
    "chipped sapphire": "gcb",
    "chipped topaz": "gcy",
    "chipped skull": "skc",

    "flawed amethyst": "gfv",
    "flawed diamond": "gfw",
    "flawed emerald": "gfg",
    "flawed ruby": "gfr",
    "flawed sapphire": "gfb",
    "flawed topaz": "gfy",
    "flawed skull": "skf",

    "amethyst": "gsv",
    "diamond": "gsw",
    "emerald": "gsg",
    "ruby": "gsr",
    "sapphire": "gsb",
    "topaz": "gsy",
    "skull": "sku",

    "flawless amethyst": "gzv",
    "flawless diamond": "glw",
    "flawless emerald": "glg",
    "flawless ruby": "glr",
    "flawless sapphire": "glb",
    "flawless topaz": "gly",
    "flawless skull": "skl",

    "perfect amethyst": "gpv",
    "perfect diamond": "gpw",
    "perfect emerald": "gpg",
    "perfect ruby": "gpr",
    "perfect sapphire": "gpb",
    "perfect topaz": "gpy",
    "perfect skull": "skz",

    # Potions
    "rejuvenation potion": "rvs",
    "full rejuvenation potion": "rvl",

    # Uber Keys
    "key of terror": "pk1",
    "key of hate": "pk2",
    "key of destruction": "pk3",

    # Token
    "token of absolution": "toa",

    # Essences
    "twisted essence of suffering": "tes",
    "charged essence of hatred": "ceh",
    "burning essence of terror": "bet",
    "festering essence of destruction": "fed",

    # Worldstone Shards
    "western worldstone shard": "xa1",
    "eastern worldstone shard": "xa2",
    "southern worldstone shard": "xa3",
    "deep worldstone shard": "xa4",
    "northern worldstone shard": "xa5",
}

SUPPORTED_ITEM_CODES = set(ITEM_NAME_TO_CODE.values())


def _normalize_item_name(item_name: str) -> str:
    return str(item_name or "").strip().lower().replace(" rune", "").strip()


def resolve_item_code(item_name: str = None, item_code: str = None) -> str:
    normalized_code = str(item_code or "").strip().lower()
    if normalized_code:
        if normalized_code in SUPPORTED_ITEM_CODES:
            return normalized_code
        raise ValueError(f"Item not supported for automatic writing: {item_code}")

    normalized_name = _normalize_item_name(item_name)
    if normalized_name in ITEM_NAME_TO_CODE:
        return ITEM_NAME_TO_CODE[normalized_name]

    raise ValueError(f"Item not supported for automatic writing: {item_name}")


def write_item_to_shared_stash(
    stash_path: str,
    item_name: str = None,
    amount: int = 1,
    item_code: str = None
) -> None:
    if amount == 0:
        raise ValueError("amount cannot be zero")

    node_cmd = get_node_cmd()
    parser_dir = get_parser_dir()
    patcher_file = get_patcher_file()

    if not os.path.isfile(stash_path):
        raise FileNotFoundError(f"Shared stash not found: {stash_path}")

    if getattr(sys, "frozen", False) and not os.path.isfile(node_cmd):
        raise FileNotFoundError(f"Embedded Node not found: {node_cmd}")

    if not os.path.isdir(parser_dir):
        raise FileNotFoundError(f"Parser directory not found: {parser_dir}")

    if not os.path.isfile(patcher_file):
        raise FileNotFoundError(f"Patcher file not found: {patcher_file}")

    resolved_item_code = resolve_item_code(item_name=item_name, item_code=item_code)
    temp_output = stash_path + ".tmp"

    command = [
        node_cmd,
        patcher_file,
        stash_path,
        temp_output,
        resolved_item_code,
        str(amount)
    ]

    if amount > 0:
        command.append("--create")

    startupinfo = None
    creationflags = 0

    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        creationflags = subprocess.CREATE_NO_WINDOW

    try:
        result = subprocess.run(
            command,
            check=True,
            cwd=parser_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            startupinfo=startupinfo,
            creationflags=creationflags,
        )
        os.replace(temp_output, stash_path)

    except subprocess.CalledProcessError as e:
        if os.path.exists(temp_output):
            os.remove(temp_output)

        raise RuntimeError(
            "Error modifying stash.\n"
            f"NODE_CMD={node_cmd}\n"
            f"PATCHER_FILE={patcher_file}\n"
            f"PARSER_DIR={parser_dir}\n"
            f"stdout={e.stdout}\n"
            f"stderr={e.stderr}"
        ) from e