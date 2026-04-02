import os

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

ITEM_CODE_MAP = {
    # Runes
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

    # Gemas - chipped
    "gcv": {"name": "Chipped Amethyst", "icon": "/static/img/items/chipped_amethyst.webp", "kind": "gem"},
    "gcw": {"name": "Chipped Diamond", "icon": "/static/img/items/chipped_diamond.webp", "kind": "gem"},
    "gcg": {"name": "Chipped Emerald", "icon": "/static/img/items/chipped_emerald.webp", "kind": "gem"},
    "gcr": {"name": "Chipped Ruby", "icon": "/static/img/items/chipped_ruby.webp", "kind": "gem"},
    "gcb": {"name": "Chipped Sapphire", "icon": "/static/img/items/chipped_sapphire.webp", "kind": "gem"},
    "gcy": {"name": "Chipped Topaz", "icon": "/static/img/items/chipped_topaz.webp", "kind": "gem"},
    "skc": {"name": "Chipped Skull", "icon": "/static/img/items/chipped_skull.webp", "kind": "gem"},

    # Gemas - flawed
    "gfv": {"name": "Flawed Amethyst", "icon": "/static/img/items/flawed_amethyst.webp", "kind": "gem"},
    "gfw": {"name": "Flawed Diamond", "icon": "/static/img/items/flawed_diamond.webp", "kind": "gem"},
    "gfg": {"name": "Flawed Emerald", "icon": "/static/img/items/flawed_emerald.webp", "kind": "gem"},
    "gfr": {"name": "Flawed Ruby", "icon": "/static/img/items/flawed_ruby.webp", "kind": "gem"},
    "gfb": {"name": "Flawed Sapphire", "icon": "/static/img/items/flawed_sapphire.webp", "kind": "gem"},
    "gfy": {"name": "Flawed Topaz", "icon": "/static/img/items/flawed_topaz.webp", "kind": "gem"},
    "skf": {"name": "Flawed Skull", "icon": "/static/img/items/flawed_skull.webp", "kind": "gem"},

    # Gemas - standard
    "gsv": {"name": "Amethyst", "icon": "/static/img/items/amethyst.webp", "kind": "gem"},
    "gsw": {"name": "Diamond", "icon": "/static/img/items/diamond.webp", "kind": "gem"},
    "gsg": {"name": "Emerald", "icon": "/static/img/items/emerald.webp", "kind": "gem"},
    "gsr": {"name": "Ruby", "icon": "/static/img/items/ruby.webp", "kind": "gem"},
    "gsb": {"name": "Sapphire", "icon": "/static/img/items/sapphire.webp", "kind": "gem"},
    "gsy": {"name": "Topaz", "icon": "/static/img/items/topaz.webp", "kind": "gem"},
    "sku": {"name": "Skull", "icon": "/static/img/items/skull.webp", "kind": "gem"},

    # Gemas - flawless
    "gzv": {"name": "Flawless Amethyst", "icon": "/static/img/items/flawless_amethyst.webp", "kind": "gem"},
    "glw": {"name": "Flawless Diamond", "icon": "/static/img/items/flawless_diamond.webp", "kind": "gem"},
    "glg": {"name": "Flawless Emerald", "icon": "/static/img/items/flawless_emerald.webp", "kind": "gem"},
    "glr": {"name": "Flawless Ruby", "icon": "/static/img/items/flawless_ruby.webp", "kind": "gem"},
    "glb": {"name": "Flawless Sapphire", "icon": "/static/img/items/flawless_sapphire.webp", "kind": "gem"},
    "gly": {"name": "Flawless Topaz", "icon": "/static/img/items/flawless_topaz.webp", "kind": "gem"},
    "skl": {"name": "Flawless Skull", "icon": "/static/img/items/flawless_skull.webp", "kind": "gem"},

    # Gemas - perfect
    "gpv": {"name": "Perfect Amethyst", "icon": "/static/img/items/perfect_amethyst.webp", "kind": "gem"},
    "gpw": {"name": "Perfect Diamond", "icon": "/static/img/items/perfect_diamond.webp", "kind": "gem"},
    "gpg": {"name": "Perfect Emerald", "icon": "/static/img/items/perfect_emerald.webp", "kind": "gem"},
    "gpr": {"name": "Perfect Ruby", "icon": "/static/img/items/perfect_ruby.webp", "kind": "gem"},
    "gpb": {"name": "Perfect Sapphire", "icon": "/static/img/items/perfect_sapphire.webp", "kind": "gem"},
    "gpy": {"name": "Perfect Topaz", "icon": "/static/img/items/perfect_topaz.webp", "kind": "gem"},
    "skz": {"name": "Perfect Skull", "icon": "/static/img/items/perfect_skull.webp", "kind": "gem"},

    # Poções
    "rvs": {"name": "Rejuvenation Potion", "icon": "/static/img/items/rejuvenation_potion.webp", "kind": "potion"},
    "rvl": {"name": "Full Rejuvenation Potion", "icon": "/static/img/items/full_rejuvenation_potion.webp", "kind": "potion"},
}

DEFAULT_ICON = "/static/img/items/default_item.webp"


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


def _normalize_quality(item: dict) -> str:
    item_type = str(item.get("type") or "").lower()
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


def _resolve_item_meta(item: dict) -> dict:
    item_type = str(item.get("type") or "").lower()
    mapped = ITEM_CODE_MAP.get(item_type)

    if mapped:
        return mapped

    raw_name = item.get("name")
    if raw_name:
        return {
            "name": raw_name,
            "icon": DEFAULT_ICON,
            "kind": "unknown",
        }

    return {
        "name": item_type or "Unknown Item",
        "icon": DEFAULT_ICON,
        "kind": "unknown",
    }


def _build_tooltip_lines(item: dict, resolved_name: str) -> list:
    lines = [resolved_name]

    amount = int(item.get("amount") or 1)
    if amount > 1:
        lines.append(f"Amount: {amount}")

    item_type = item.get("type")
    if item_type:
        lines.append(f"Code: {item_type}")

    categories = item.get("categories") or []
    if categories:
        lines.append("Categories: " + ", ".join(categories))

    return lines


def _convert_stackable_item(item: dict) -> dict:
    meta = _resolve_item_meta(item)
    item_name = meta["name"]

    return {
        "itemName": item_name,
        "quality": _normalize_quality(item),
        "quantity": int(item.get("amount") or 1),
        "tooltip_lines": _build_tooltip_lines(item, item_name),
        "code": item.get("type"),
        "icon": meta["icon"],
        "kind": meta["kind"],
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
        items = [_convert_stackable_item(item) for item in stackables]

        return {
            "stash_name": "Shared Stash",
            "stash_file": stash_path,
            "item_count": len(items),
            "read_status": "Successfully read via JS reader",
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