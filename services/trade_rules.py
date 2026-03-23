def normalize_text(value) -> str:
    if not value:
        return ""
    return str(value).strip().lower()


def get_item_category(item: dict) -> str:
    item_base_type = normalize_text(item.get("type"))

    if item_base_type == "rune":
        return "rune"

    return "blocked"


def is_tradeable_item(item: dict) -> bool:
    return get_item_category(item) == "rune"