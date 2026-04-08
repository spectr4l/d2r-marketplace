import csv
import os
from functools import lru_cache

from modules.d2_reader import read_shared_stash

RUNE_QUALITY_MAP = {
    "r01": "normal", "r02": "normal", "r03": "normal", "r04": "normal",
    "r05": "normal", "r06": "normal", "r07": "normal", "r08": "normal",
    "r09": "normal", "r10": "normal", "r11": "normal", "r12": "normal",
    "r13": "normal", "r14": "normal", "r15": "normal", "r16": "normal",
    "r17": "normal", "r18": "normal", "r19": "normal", "r20": "normal",
    "r21": "normal", "r22": "normal", "r23": "normal", "r24": "normal",
    "r25": "normal", "r26": "normal", "r27": "normal", "r28": "normal",
    "r29": "normal", "r30": "normal", "r31": "normal", "r32": "normal",
    "r33": "normal",
}

DEFAULT_ICON = "/static/img/items/default_item.webp"

ITEM_CODE_MAP = {
    # =========================
    # RUNES
    # =========================
    "r01": {"name": "El Rune", "icon": "/static/img/runes/el.webp", "kind": "rune"},
    "r02": {"name": "Eld Rune", "icon": "/static/img/runes/eld.webp", "kind": "rune"},
    "r03": {"name": "Tir Rune", "icon": "/static/img/runes/tir.webp", "kind": "rune"},
    "r04": {"name": "Nef Rune", "icon": "/static/img/runes/nef.webp", "kind": "rune"},
    "r05": {"name": "Eth Rune", "icon": "/static/img/runes/eth.webp", "kind": "rune"},
    "r06": {"name": "Ith Rune", "icon": "/static/img/runes/ith.webp", "kind": "rune"},
    "r07": {"name": "Tal Rune", "icon": "/static/img/runes/tal.webp", "kind": "rune"},
    "r08": {"name": "Ral Rune", "icon": "/static/img/runes/ral.webp", "kind": "rune"},
    "r09": {"name": "Ort Rune", "icon": "/static/img/runes/ort.webp", "kind": "rune"},
    "r10": {"name": "Thul Rune", "icon": "/static/img/runes/thul.webp", "kind": "rune"},
    "r11": {"name": "Amn Rune", "icon": "/static/img/runes/amn.webp", "kind": "rune"},
    "r12": {"name": "Sol Rune", "icon": "/static/img/runes/sol.webp", "kind": "rune"},
    "r13": {"name": "Shael Rune", "icon": "/static/img/runes/shael.webp", "kind": "rune"},
    "r14": {"name": "Dol Rune", "icon": "/static/img/runes/dol.webp", "kind": "rune"},
    "r15": {"name": "Hel Rune", "icon": "/static/img/runes/hel.webp", "kind": "rune"},
    "r16": {"name": "Io Rune", "icon": "/static/img/runes/io.webp", "kind": "rune"},
    "r17": {"name": "Lum Rune", "icon": "/static/img/runes/lum.webp", "kind": "rune"},
    "r18": {"name": "Ko Rune", "icon": "/static/img/runes/ko.webp", "kind": "rune"},
    "r19": {"name": "Fal Rune", "icon": "/static/img/runes/fal.webp", "kind": "rune"},
    "r20": {"name": "Lem Rune", "icon": "/static/img/runes/lem.webp", "kind": "rune"},
    "r21": {"name": "Pul Rune", "icon": "/static/img/runes/pul.webp", "kind": "rune"},
    "r22": {"name": "Um Rune", "icon": "/static/img/runes/um.webp", "kind": "rune"},
    "r23": {"name": "Mal Rune", "icon": "/static/img/runes/mal.webp", "kind": "rune"},
    "r24": {"name": "Ist Rune", "icon": "/static/img/runes/ist.webp", "kind": "rune"},
    "r25": {"name": "Gul Rune", "icon": "/static/img/runes/gul.webp", "kind": "rune"},
    "r26": {"name": "Vex Rune", "icon": "/static/img/runes/vex.webp", "kind": "rune"},
    "r27": {"name": "Ohm Rune", "icon": "/static/img/runes/ohm.webp", "kind": "rune"},
    "r28": {"name": "Lo Rune", "icon": "/static/img/runes/lo.webp", "kind": "rune"},
    "r29": {"name": "Sur Rune", "icon": "/static/img/runes/sur.webp", "kind": "rune"},
    "r30": {"name": "Ber Rune", "icon": "/static/img/runes/ber.webp", "kind": "rune"},
    "r31": {"name": "Jah Rune", "icon": "/static/img/runes/jah.webp", "kind": "rune"},
    "r32": {"name": "Cham Rune", "icon": "/static/img/runes/cham.webp", "kind": "rune"},
    "r33": {"name": "Zod Rune", "icon": "/static/img/runes/zod.webp", "kind": "rune"},

    # =========================
    # GEMS
    # =========================
    # chipped
    "gcv": {"name": "Chipped Amethyst", "icon": "/static/img/items/chipped_amethyst.webp", "kind": "gem"},
    "gcw": {"name": "Chipped Diamond", "icon": "/static/img/items/chipped_diamond.webp", "kind": "gem"},
    "gcg": {"name": "Chipped Emerald", "icon": "/static/img/items/chipped_emerald.webp", "kind": "gem"},
    "gcr": {"name": "Chipped Ruby", "icon": "/static/img/items/chipped_ruby.webp", "kind": "gem"},
    "gcb": {"name": "Chipped Sapphire", "icon": "/static/img/items/chipped_sapphire.webp", "kind": "gem"},
    "gcy": {"name": "Chipped Topaz", "icon": "/static/img/items/chipped_topaz.webp", "kind": "gem"},
    "skc": {"name": "Chipped Skull", "icon": "/static/img/items/chipped_skull.webp", "kind": "gem"},

    # flawed
    "gfv": {"name": "Flawed Amethyst", "icon": "/static/img/items/flawed_amethyst.webp", "kind": "gem"},
    "gfw": {"name": "Flawed Diamond", "icon": "/static/img/items/flawed_diamond.webp", "kind": "gem"},
    "gfg": {"name": "Flawed Emerald", "icon": "/static/img/items/flawed_emerald.webp", "kind": "gem"},
    "gfr": {"name": "Flawed Ruby", "icon": "/static/img/items/flawed_ruby.webp", "kind": "gem"},
    "gfb": {"name": "Flawed Sapphire", "icon": "/static/img/items/flawed_sapphire.webp", "kind": "gem"},
    "gfy": {"name": "Flawed Topaz", "icon": "/static/img/items/flawed_topaz.webp", "kind": "gem"},
    "skf": {"name": "Flawed Skull", "icon": "/static/img/items/flawed_skull.webp", "kind": "gem"},

    # standard
    "gsv": {"name": "Amethyst", "icon": "/static/img/items/amethyst.webp", "kind": "gem"},
    "gsw": {"name": "Diamond", "icon": "/static/img/items/diamond.webp", "kind": "gem"},
    "gsg": {"name": "Emerald", "icon": "/static/img/items/emerald.webp", "kind": "gem"},
    "gsr": {"name": "Ruby", "icon": "/static/img/items/ruby.webp", "kind": "gem"},
    "gsb": {"name": "Sapphire", "icon": "/static/img/items/sapphire.webp", "kind": "gem"},
    "gsy": {"name": "Topaz", "icon": "/static/img/items/topaz.webp", "kind": "gem"},
    "sku": {"name": "Skull", "icon": "/static/img/items/skull.webp", "kind": "gem"},

    # flawless
    "gzv": {"name": "Flawless Amethyst", "icon": "/static/img/items/flawless_amethyst.webp", "kind": "gem"},
    "glw": {"name": "Flawless Diamond", "icon": "/static/img/items/flawless_diamond.webp", "kind": "gem"},
    "glg": {"name": "Flawless Emerald", "icon": "/static/img/items/flawless_emerald.webp", "kind": "gem"},
    "glr": {"name": "Flawless Ruby", "icon": "/static/img/items/flawless_ruby.webp", "kind": "gem"},
    "glb": {"name": "Flawless Sapphire", "icon": "/static/img/items/flawless_sapphire.webp", "kind": "gem"},
    "gly": {"name": "Flawless Topaz", "icon": "/static/img/items/flawless_topaz.webp", "kind": "gem"},
    "skl": {"name": "Flawless Skull", "icon": "/static/img/items/flawless_skull.webp", "kind": "gem"},

    # perfect
    "gpv": {"name": "Perfect Amethyst", "icon": "/static/img/items/perfect_amethyst.webp", "kind": "gem"},
    "gpw": {"name": "Perfect Diamond", "icon": "/static/img/items/perfect_diamond.webp", "kind": "gem"},
    "gpg": {"name": "Perfect Emerald", "icon": "/static/img/items/perfect_emerald.webp", "kind": "gem"},
    "gpr": {"name": "Perfect Ruby", "icon": "/static/img/items/perfect_ruby.webp", "kind": "gem"},
    "gpb": {"name": "Perfect Sapphire", "icon": "/static/img/items/perfect_sapphire.webp", "kind": "gem"},
    "gpy": {"name": "Perfect Topaz", "icon": "/static/img/items/perfect_topaz.webp", "kind": "gem"},
    "skz": {"name": "Perfect Skull", "icon": "/static/img/items/perfect_skull.webp", "kind": "gem"},

    # =========================
    # POTIONS
    # =========================
    "rvs": {"name": "Rejuvenation Potion", "icon": "/static/img/items/rejuvenation_potion.webp", "kind": "potion"},
    "rvl": {"name": "Full Rejuvenation Potion", "icon": "/static/img/items/full_rejuvenation_potion.webp", "kind": "potion"},

    # =========================
    # UBER KEYS
    # =========================
    "pk1": {"icon": "/static/img/items/key_of_terror.webp", "kind": "key"},
    "pk2": {"icon": "/static/img/items/key_of_hate.webp", "kind": "key"},
    "pk3": {"icon": "/static/img/items/key_of_destruction.webp", "kind": "key"},

    # =========================
    # TOKEN
    # =========================
    "toa": {"icon": "/static/img/items/token_of_absolution.webp", "kind": "token"},

    # =========================
    # ESSENCES
    # =========================
    "tes": {"icon": "/static/img/items/twisted_essence.webp", "kind": "essence"},
    "ceh": {"icon": "/static/img/items/charged_essence.webp", "kind": "essence"},
    "bet": {"icon": "/static/img/items/burning_essence.webp", "kind": "essence"},
    "fed": {"icon": "/static/img/items/festering_essence.webp", "kind": "essence"},

    # =========================
    # SHARDS
    # =========================
    "xa1": {"icon": "/static/img/items/xa1.webp", "kind": "shard"},
    "xa2": {"icon": "/static/img/items/xa2.webp", "kind": "shard"},
    "xa3": {"icon": "/static/img/items/xa3.webp", "kind": "shard"},
    "xa4": {"icon": "/static/img/items/xa4.webp", "kind": "shard"},
    "xa5": {"icon": "/static/img/items/xa5.webp", "kind": "shard"},
}

VISIBLE_INVENTORY_CODES = set(ITEM_CODE_MAP.keys())

SPECIAL_MISC_CODES = set()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

MISC_CANDIDATE_PATHS = [
    os.path.join(BASE_DIR, "data", "misc.txt"),
    os.path.join(BASE_DIR, "misc.txt"),
]


def find_shared_stash_file(save_folder: str):
    if not save_folder or not os.path.isdir(save_folder):
        return None

    candidates = [
        "SharedStashSoftCoreV2.d2i",
        "ModernSharedStashSoftCoreV2.d2i",
        "SharedStashHardCoreV2.d2i",
        "ModernSharedStashHardCoreV2.d2i",
    ]

    for filename in candidates:
        full_path = os.path.join(save_folder, filename)
        if os.path.isfile(full_path):
            return full_path

    return None


def _find_misc_txt_path() -> str | None:
    for path in MISC_CANDIDATE_PATHS:
        if os.path.isfile(path):
            return path
    return None


def _normalize_quality(item: dict) -> str:
    item_type = str(item.get("type") or "").strip().lower()

    if item_type in RUNE_QUALITY_MAP:
        return RUNE_QUALITY_MAP[item_type]

    quality = item.get("quality")
    if quality is None:
        return "normal"

    if isinstance(quality, int):
        if quality == 7:
            return "unique"
        if quality == 6:
            return "rare"
        if quality == 5:
            return "set"
        if quality == 4:
            return "magic"
        return "normal"

    return str(quality).lower()


def _safe_int(value, default=0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _infer_kind(row: dict, code: str) -> str:
    code = (code or "").strip().lower()
    item_type = (row.get("type") or "").strip().lower()

    if code in {"pk1", "pk2", "pk3"}:
        return "key"
    if code in {"tes", "ceh", "bet", "fed"}:
        return "essence"
    if code == "toa":
        return "token"
    if code in {"xa1", "xa2", "xa3", "xa4", "xa5"}:
        return "shard"

    if item_type == "key":
        return "key"
    if item_type == "scro":
        return "scroll"
    if item_type == "book":
        return "tome"
    if item_type in {"bowq", "xboq"}:
        return "ammo"
    if item_type in {"hpot", "mpot", "rpot", "apot", "wpot", "spot", "elix"}:
        return "potion"
    if item_type in {"gema", "gemb", "gemd", "geme", "gemr", "gems", "gemt"}:
        return "gem"

    return "misc"


@lru_cache(maxsize=1)
def _load_misc_code_map() -> dict[str, dict]:
    misc_path = _find_misc_txt_path()
    if not misc_path:
        return {}

    result: dict[str, dict] = {}

    with open(misc_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            code = (row.get("code") or "").strip().lower()
            name = (row.get("name") or "").strip()

            if not code or not name:
                continue

            stackable_flag = str(row.get("stackable") or "").strip() == "1"

            if not stackable_flag and code not in SPECIAL_MISC_CODES and code not in VISIBLE_INVENTORY_CODES:
                continue

            result[code] = {
                "name": name,
                "icon": DEFAULT_ICON,
                "kind": _infer_kind(row, code),
                "stackable": stackable_flag or code in SPECIAL_MISC_CODES or code in VISIBLE_INVENTORY_CODES,
                "minstack": _safe_int(row.get("minstack")),
                "maxstack": _safe_int(row.get("maxstack")),
                "spawnstack": _safe_int(row.get("spawnstack")),
                "code": code,
            }

    return result


def _merge_manual_and_misc_meta(item_type: str, manual_meta: dict) -> dict:
    misc_map = _load_misc_code_map()
    misc_meta = misc_map.get(item_type, {})

    resolved = {}

    # nome: manual tem prioridade; se não tiver, usa misc.txt
    resolved["name"] = (
        manual_meta.get("name")
        or misc_meta.get("name")
        or item_type
    )

    # ícone e kind: manual tem prioridade
    resolved["icon"] = manual_meta.get("icon") or misc_meta.get("icon") or DEFAULT_ICON
    resolved["kind"] = manual_meta.get("kind") or misc_meta.get("kind") or "misc"
    resolved["code"] = item_type

    # dados auxiliares do misc
    resolved["stackable"] = misc_meta.get("stackable", True)
    resolved["minstack"] = misc_meta.get("minstack", 0)
    resolved["maxstack"] = misc_meta.get("maxstack", 0)
    resolved["spawnstack"] = misc_meta.get("spawnstack", 0)

    return resolved


def _resolve_item_meta(item: dict) -> dict:
    item_type = str(item.get("type") or "").strip().lower()

    # 1) prioridade total para os itens permitidos no inventário,
    # mas deixando o nome vir do misc.txt se não estiver setado manualmente
    if item_type in ITEM_CODE_MAP:
        return _merge_manual_and_misc_meta(item_type, ITEM_CODE_MAP[item_type])

    # 2) fallback pelo misc.txt
    misc_map = _load_misc_code_map()
    if item_type in misc_map:
        return misc_map[item_type]

    # 3) fallback com o nome bruto vindo do reader
    raw_name = str(item.get("name") or "").strip()
    if raw_name:
        return {
            "name": raw_name,
            "icon": DEFAULT_ICON,
            "kind": "unknown",
            "code": item_type,
        }

    # 4) último fallback
    return {
        "name": item_type or "Unknown Item",
        "icon": DEFAULT_ICON,
        "kind": "unknown",
        "code": item_type,
    }


def _build_tooltip_lines(item: dict, meta: dict | None = None) -> list:
    lines = []

    resolved = meta or _resolve_item_meta(item)

    name = resolved.get("name") or item.get("name") or item.get("type") or "Unknown Item"
    lines.append(name)

    amount = _safe_int(item.get("amount"), 1)
    if amount > 1:
        lines.append(f"Quantity: {amount}")

    item_code = str(item.get("type") or "").strip().lower()
    if item_code:
        lines.append(f"Code: {item_code}")

    kind = resolved.get("kind")
    if kind and kind != "unknown":
        lines.append(f"Type: {kind}")

    categories = item.get("categories") or []
    if categories:
        lines.append("Categories: " + ", ".join(categories))

    return lines


def _convert_stackable_item(item: dict) -> dict:
    meta = _resolve_item_meta(item)
    item_code = str(item.get("type") or "").strip().lower()

    return {
        "itemName": meta.get("name") or item.get("name") or item_code or "Unknown Item",
        "quality": _normalize_quality(item),
        "quantity": _safe_int(item.get("amount"), 1),
        "tooltip_lines": _build_tooltip_lines(item, meta),
        "code": item_code,
        "kind": meta.get("kind", "unknown"),
        "icon": meta.get("icon", DEFAULT_ICON),
        "raw": item,
    }


def load_inventory_stash(save_folder: str) -> dict:
    stash_path = find_shared_stash_file(save_folder)
    if not stash_path:
        return {
            "stash_name": "Shared Stash",
            "stash_file": None,
            "item_count": 0,
            "read_status": "Shared stash file not found",
            "items": [],
            "raw_error": None,
        }

    try:
        parsed = read_shared_stash(stash_path)
        stackables = parsed.get("stackables", [])

        filtered_stackables = [
            item
            for item in stackables
            if (
                str(item.get("type") or "").strip().lower() in VISIBLE_INVENTORY_CODES
                and _safe_int(item.get("amount"), 0) > 0
            )
        ]

        items = [_convert_stackable_item(item) for item in filtered_stackables]

        misc_path = _find_misc_txt_path()
        misc_status = misc_path if misc_path else "misc.txt not found"

        return {
            "stash_name": "Shared Stash",
            "stash_file": stash_path,
            "item_count": len(items),
            "read_status": "Stash successfully parsed via JS reader",
            "misc_file": misc_status,
            "items": items,
            "raw_error": None,
        }

    except Exception as e:
        return {
            "stash_name": "Shared Stash",
            "stash_file": stash_path,
            "item_count": 0,
            "read_status": "Error reading shared stash",
            "items": [],
            "raw_error": str(e),
        }
