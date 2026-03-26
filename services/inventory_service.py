import os
from modules.d2_reader import read_shared_stash


RUNE_QUALITY_MAP = {
    "r01": "normal",
    "r02": "normal",
    "r03": "normal",
    "r04": "normal",
    "r05": "normal",
    "r06": "normal",
    "r07": "normal",
    "r08": "normal",
    "r09": "normal",
    "r10": "normal",
    "r11": "normal",
    "r12": "normal",
    "r13": "normal",
    "r14": "normal",
    "r15": "normal",
    "r16": "normal",
    "r17": "normal",
    "r18": "normal",
    "r19": "normal",
    "r20": "normal",
    "r21": "normal",
    "r22": "normal",
    "r23": "normal",
    "r24": "normal",
    "r25": "normal",
    "r26": "normal",
    "r27": "normal",
    "r28": "normal",
    "r29": "normal",
    "r30": "normal",
    "r31": "normal",
    "r32": "normal",
    "r33": "normal",
}


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

    # caso venha numérico
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


def _build_tooltip_lines(item: dict) -> list:
    lines = []

    name = item.get("name") or item.get("type") or "Unknown Item"
    lines.append(name)

    amount = int(item.get("amount") or 1)
    if amount > 1:
        lines.append(f"Quantidade: {amount}")

    item_type = item.get("type")
    if item_type:
        lines.append(f"Código: {item_type}")

    categories = item.get("categories") or []
    if categories:
        lines.append("Categorias: " + ", ".join(categories))

    return lines


def _convert_stackable_item(item: dict) -> dict:
    return {
        "itemName": item.get("name") or item.get("type") or "Unknown Item",
        "quality": _normalize_quality(item),
        "quantity": int(item.get("amount") or 1),
        "tooltip_lines": _build_tooltip_lines(item),
        "code": item.get("type"),
        "raw": item,
    }


def load_inventory_stash(save_folder: str) -> dict:
    stash_path = find_shared_stash_file(save_folder)

    if not stash_path:
        return {
            "stash_name": "Shared Stash",
            "stash_file": None,
            "item_count": 0,
            "read_status": "Arquivo shared stash não encontrado",
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
            "read_status": "Leitura realizada com sucesso via reader JS",
            "items": items,
            "raw_error": None,
        }

    except Exception as e:
        return {
            "stash_name": "Shared Stash",
            "stash_file": stash_path,
            "item_count": 0,
            "read_status": "Erro ao ler o shared stash",
            "items": [],
            "raw_error": str(e),
        }