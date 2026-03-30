import os
import subprocess
import tempfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARSER_DIR = os.path.join(BASE_DIR, "tools", "d2r_parser")
PATCHER_FILE = os.path.join(PARSER_DIR, "patch_stackable.cjs")
NODE_CMD = "node"

RUNE_NAME_TO_CODE = {
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
}

def _normalize_item_name(item_name: str) -> str:
    return str(item_name or "").strip().lower().replace(" rune", "").strip()

def resolve_rune_code(item_name: str) -> str:
    normalized = _normalize_item_name(item_name)

    if normalized in RUNE_NAME_TO_CODE:
        return RUNE_NAME_TO_CODE[normalized]

    raise ValueError(f"Rune não suportada para escrita automática: {item_name}")

def write_item_to_shared_stash(stash_path: str, item_name: str, amount: int = 1) -> None:
    if amount == 0:
        raise ValueError("amount não pode ser zero")

    item_code = resolve_rune_code(item_name)

    temp_output = stash_path + ".tmp"

    command = [
        NODE_CMD,
        PATCHER_FILE,
        stash_path,
        temp_output,
        item_code,
        str(amount)
    ]

    # só cria item se for positivo
    if amount > 0:
        command.append("--create")

    try:
        subprocess.run(command, check=True)
        os.replace(temp_output, stash_path)
    except subprocess.CalledProcessError as e:
        if os.path.exists(temp_output):
            os.remove(temp_output)
        raise RuntimeError(f"Erro ao modificar stash: {e}")