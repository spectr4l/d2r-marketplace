import json
import uuid

from database.db import (
    get_token_balance,
    update_token_balance,
    add_virtual_item,
    add_transaction,
    mark_item_as_sold,
    mark_item_as_imported,
    get_virtual_items,
)
from services.inventory_service import find_shared_stash_file
from modules.d2_writer import write_item_to_shared_stash


def list_available_items():
    return get_virtual_items("available")


def calculate_sell_price(token_price):
    return int(token_price * 0.7)


def export_item_to_marketplace(item, character_file):
    item_id = str(uuid.uuid4())

    add_virtual_item(
        item_id=item_id,
        name=item["name"],
        item_type=item.get("base_name", "unknown"),
        quality="unique" if item.get("is_unique") else "normal",
        attributes=json.dumps(item, ensure_ascii=False),
        source="exported",
        exported_from=character_file,
    )

    add_transaction(
        "export",
        item_id,
        0,
        f"Item exported from {character_file}: {item['name']}"
    )

    return item_id


def sell_virtual_item(item_id):
    items = get_virtual_items("available")
    item = next((i for i in items if i["id"] == item_id), None)

    if not item:
        raise ValueError("Item not found")

    token_price = item.get("token_price", 0)
    sell_price = calculate_sell_price(token_price)

    mark_item_as_sold(item_id)
    update_token_balance(sell_price)

    add_transaction(
        "sell",
        item_id,
        sell_price,
        f"Sold for {sell_price} tokens"
    )

    return get_token_balance()


def _normalize_item_type(item_type):
    value = str(item_type or "").strip().lower()
    aliases = {
        "rune": "rune",
        "runes": "rune",
        "runa": "rune",
        "runas": "rune",
    }
    return aliases.get(value, value)


def _looks_like_rune(item_name, item_type):
    normalized_type = _normalize_item_type(item_type)
    if normalized_type == "rune":
        return True

    name = str(item_name or "").strip().lower()
    return name.endswith(" rune")


def buy_catalog_item(item_name, item_type, token_price, save_folder, qty=1):
    if not isinstance(token_price, int):
        raise ValueError("token_price must be an integer")
    if token_price <= 0:
        raise ValueError("token_price must be greater than zero")

    qty = int(qty)

    if qty <= 0:
        raise ValueError("Invalid quantity")

    normalized_item_type = _normalize_item_type(item_type)

    if not _looks_like_rune(item_name, normalized_item_type):
        raise ValueError(
            f"Currently, only runes are supported for direct purchase into the save file. "
            f"Received: item_name={item_name!r}, item_type={item_type!r}"
        )

    total_price = token_price * qty
    balance = get_token_balance()
    if balance < total_price:
        raise ValueError("Insufficient balance")

    stash_path = find_shared_stash_file(save_folder)
    if not stash_path:
        raise FileNotFoundError("Shared stash not found in configured folder")

    write_item_to_shared_stash(
        stash_path=stash_path,
        item_name=item_name,
        amount=qty,
    )

    item_id = str(uuid.uuid4())
    add_virtual_item(
        item_id=item_id,
        name=item_name,
        item_type=normalized_item_type,
        quality="normal",
        attributes=json.dumps(
            {
                "name": item_name,
                "type": normalized_item_type,
                "quantity": qty,
                "delivered_to_stash": True,
            },
            ensure_ascii=False,
        ),
        source="purchased",
        token_price=total_price,
    )

    mark_item_as_imported(item_id)
    update_token_balance(-total_price)

    add_transaction(
        "buy_import",
        item_id,
        -total_price,
        f"Purchased and delivered to shared stash: {qty}x {item_name}"
    )

    return {
        "item_id": item_id,
        "new_balance": get_token_balance(),
        "stash_path": stash_path,
    }


def import_virtual_item_to_game(item_id, target_character):
    mark_item_as_imported(item_id)

    add_transaction(
        "import",
        item_id,
        0,
        f"Item prepared for import into {target_character}"
    )

    return True