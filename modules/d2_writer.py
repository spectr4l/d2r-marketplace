import os
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARSER_DIR = os.path.join(BASE_DIR, "tools", "d2r_parser")
PATCHER_FILE = os.path.join(PARSER_DIR, "patch_stackable.cjs")
NODE_CMD = "node"

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

    # Gemas
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

    # Poções
    "rejuvenation potion": "rvs",
    "full rejuvenation potion": "rvl",
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

    resolved_item_code = resolve_item_code(item_name=item_name, item_code=item_code)

    temp_output = stash_path + ".tmp"

    command = [
        NODE_CMD,
        PATCHER_FILE,
        stash_path,
        temp_output,
        resolved_item_code,
        str(amount)
    ]

    if amount > 0:
        command.append("--create")

    try:
        subprocess.run(command, check=True)
        os.replace(temp_output, stash_path)
    except subprocess.CalledProcessError as e:
        if os.path.exists(temp_output):
            os.remove(temp_output)
        raise RuntimeError(f"Error modifying stash: {e}")