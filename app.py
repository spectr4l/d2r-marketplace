from flask import Flask, render_template, request, jsonify
import os
import json
import uuid
import random
from datetime import datetime, UTC

from database.db import (
    init_database,
    get_connection,
    get_token_balance,
    get_listed_items,
    get_listed_item_by_id,
    mark_listing_cancelled,
    process_due_listings,
)
from modules.d2_writer import write_item_to_shared_stash

from services.marketplace_service import (
    list_available_items,
    export_item_to_marketplace,
    sell_virtual_item,
    buy_catalog_item,
    import_virtual_item_to_game,
)
from services.inventory_service import load_inventory_stash, find_shared_stash_file

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-this")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

DATA_DIR = os.path.join(BASE_DIR, "data")
TOKEN_PRICES_FILE = os.path.join(DATA_DIR, "item_prices.json")

DEFAULT_SAVE_FOLDER = os.path.expanduser("~/Documents/Diablo II Resurrected/")

RUNE_TOOLTIPS = {
    "El": {
        "weapon": "+50 to Attack Rating, +1 to Light Radius",
        "armor": "+15 Defense, +1 to Light Radius",
        "shield": "+1 to Light Radius"
    },
    "Eld": {
        "weapon": "+75% Damage to Undead, +50 Attack Rating against Undead",
        "armor": "15% Slower Stamina Drain",
        "shield": "7% Increased Chance of Blocking"
    },
    "Tir": {
        "weapon": "+2 Mana After Each Kill",
        "armor": "+2 Mana After Each Kill",
        "shield": "+2 Mana After Each Kill"
    },
    "Nef": {
        "weapon": "Knockback",
        "armor": "+30 Defense vs. Missile",
        "shield": "+30 Defense vs. Missile"
    },
    "Eth": {
        "weapon": "-25% Target Defense",
        "armor": "Regenerate Mana 15%",
        "shield": "Regenerate Mana 15%"
    },
    "Ith": {
        "weapon": "+9 to Maximum Damage",
        "armor": "15% Damage Taken Goes To Mana",
        "shield": "15% Damage Taken Goes To Mana"
    },
    "Tal": {
        "weapon": "+75 Poison Damage Over 5 Seconds",
        "armor": "+30% Poison Resist",
        "shield": "+35% Poison Resist"
    },
    "Ral": {
        "weapon": "Adds 5-30 Fire Damage",
        "armor": "+30% Fire Resist",
        "shield": "+35% Fire Resist"
    },
    "Ort": {
        "weapon": "Adds 1-50 Lightning Damage",
        "armor": "+30% Lightning Resist",
        "shield": "+35% Lightning Resist"
    },
    "Thul": {
        "weapon": "Adds 3-14 Cold Damage",
        "armor": "+30% Cold Resist",
        "shield": "+35% Cold Resist"
    },
    "Amn": {
        "weapon": "7% Life Stolen Per Hit",
        "armor": "Attacker Takes Damage of 14",
        "shield": "Attacker Takes Damage of 14"
    },
    "Sol": {
        "weapon": "+9 to Minimum Damage",
        "armor": "Damage Reduced by 7",
        "shield": "Damage Reduced by 7"
    },
    "Shael": {
        "weapon": "20% Increased Attack Speed",
        "armor": "20% Faster Hit Recovery",
        "shield": "20% Faster Block Rate"
    },
    "Dol": {
        "weapon": "Hit Causes Monster to Flee 25%",
        "armor": "Replenish Life +7",
        "shield": "Replenish Life +7"
    },
    "Hel": {
        "weapon": "Requirements -20%",
        "armor": "Requirements -15%",
        "shield": "Requirements -15%"
    },
    "Io": {
        "weapon": "+10 Vitality",
        "armor": "+10 Vitality",
        "shield": "+10 Vitality"
    },
    "Lum": {
        "weapon": "+10 Energy",
        "armor": "+10 Energy",
        "shield": "+10 Energy"
    },
    "Ko": {
        "weapon": "+10 Dexterity",
        "armor": "+10 Dexterity",
        "shield": "+10 Dexterity"
    },
    "Fal": {
        "weapon": "+10 Strength",
        "armor": "+10 Strength",
        "shield": "+10 Strength"
    },
    "Lem": {
        "weapon": "75% Extra Gold from Monsters",
        "armor": "50% Extra Gold from Monsters",
        "shield": "50% Extra Gold from Monsters"
    },
    "Pul": {
        "weapon": "+75% Damage to Demons, +100 Attack Rating against Demons",
        "armor": "+30% Enhanced Defense",
        "shield": "+30% Enhanced Defense"
    },
    "Um": {
        "weapon": "25% Chance of Open Wounds",
        "armor": "+15% All Resistances",
        "shield": "+22% All Resistances"
    },
    "Mal": {
        "weapon": "Prevent Monster Heal",
        "armor": "Magic Damage Reduced by 7",
        "shield": "Magic Damage Reduced by 7"
    },
    "Ist": {
        "weapon": "30% Better Chance of Getting Magic Items",
        "armor": "25% Better Chance of Getting Magic Items",
        "shield": "25% Better Chance of Getting Magic Items"
    },
    "Gul": {
        "weapon": "+20% Bonus to Attack Rating",
        "armor": "+5% Maximum Poison Resist",
        "shield": "+5% Maximum Poison Resist"
    },
    "Vex": {
        "weapon": "7% Mana Stolen Per Hit",
        "armor": "+5% Maximum Fire Resist",
        "shield": "+5% Maximum Fire Resist"
    },
    "Ohm": {
        "weapon": "+50% Enhanced Damage",
        "armor": "+5% Maximum Cold Resist",
        "shield": "+5% Maximum Cold Resist"
    },
    "Lo": {
        "weapon": "20% Deadly Strike",
        "armor": "+5% Maximum Lightning Resist",
        "shield": "+5% Maximum Lightning Resist"
    },
    "Sur": {
        "weapon": "Hit Blinds Target",
        "armor": "Increase Maximum Mana 5%",
        "shield": "+50 Mana"
    },
    "Ber": {
        "weapon": "20% Crushing Blow",
        "armor": "Damage Reduced by 8%",
        "shield": "Damage Reduced by 8%"
    },
    "Jah": {
        "weapon": "Ignore Target's Defense",
        "armor": "Increase Maximum Life 5%",
        "shield": "+50 to Life"
    },
    "Cham": {
        "weapon": "Freeze Target +3",
        "armor": "Cannot Be Frozen",
        "shield": "Cannot Be Frozen"
    },
    "Zod": {
        "weapon": "Indestructible",
        "armor": "Indestructible",
        "shield": "Indestructible"
    }
}

def get_rune_tooltip(rune_name, slot):
    rune_data = RUNE_TOOLTIPS.get(rune_name, {})
    return rune_data.get(slot, "No information")

app.jinja_env.globals.update(get_rune_tooltip=get_rune_tooltip)

init_database()


def load_app_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "save_folder": data.get("save_folder") or DEFAULT_SAVE_FOLDER
                }
        except Exception:
            return {
                "save_folder": DEFAULT_SAVE_FOLDER
            }

    return {
        "save_folder": DEFAULT_SAVE_FOLDER
    }


def save_app_config(config_data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)


app_config = load_app_config()
SAVE_FOLDER = app_config["save_folder"]


@app.context_processor
def inject_global_data():
    return {
        "global_balance": get_token_balance()
    }


def load_token_prices():
    if not os.path.exists(TOKEN_PRICES_FILE):
        raise RuntimeError("item_prices.json file not found.")

    with open(TOKEN_PRICES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_market_reference_price(item_name: str, item_kind: str | None = None) -> int:
    prices = load_token_prices()

    normalized_name = str(item_name or "").strip()
    normalized_kind = str(item_kind or "").strip().lower()

    category_map = {
        "gem": "gems",
        "potion": "potions",
        "key": "keys",
        "essence": "essences",
        "token": "tokens",
        "shard": "shards",
        "unique": "uniques",
    }

    if normalized_kind == "rune" and normalized_name.endswith(" Rune"):
        rune_key = normalized_name.replace(" Rune", "")
        return int(prices.get("runes", {}).get(rune_key, 0))

    json_category = category_map.get(normalized_kind)
    if json_category:
        return int(prices.get(json_category, {}).get(normalized_name, 0))

    return 0

def get_sell_price_suggestion(item_name: str, item_kind: str | None = None) -> dict:
    base_price = get_market_reference_price(item_name=item_name, item_kind=item_kind)

    if base_price <= 0:
        return {
            "base_price": 0,
            "suggested_price": 0,
            "min_price": 0,
            "max_price": 0,
            "variation": 0,
            "has_reference": False,
        }

    # margem pequena de 4%
    variation = max(1, int(round(base_price * 0.04)))

    return {
        "base_price": base_price,
        "suggested_price": base_price,
        "min_price": base_price,
        "max_price": base_price + variation,
        "variation": variation,
        "has_reference": True,
    }

def calculate_sell_after_seconds(unit_price: int, reference_price: int, item_kind: str | None = None) -> int:
    if reference_price <= 0:
        base_seconds = random.randint(30 * 60, 90 * 60)  # 30–90 min
    else:
        ratio = unit_price / reference_price

        if ratio <= 0.80:
            base_seconds = random.randint(1 * 60, 10 * 60)
        elif ratio <= 0.95:
            base_seconds = random.randint(1 * 60, 25 * 60)
        elif ratio <= 1.05:
            base_seconds = random.randint(2 * 60, 30 * 60)
        elif ratio <= 1.25:
            base_seconds = random.randint(30 * 60, 3 * 60 * 60)
        elif ratio <= 1.60:
            base_seconds = random.randint(3 * 60 * 60, 8 * 60 * 60)
        else:
            base_seconds = random.randint(8 * 60 * 60, 24 * 60 * 60)

    kind = str(item_kind or "").strip().lower()

    if kind == "potion":
        return max(2 * 60, int(base_seconds * 0.45))

    if kind == "gem":
        return max(5 * 60, int(base_seconds * 0.75))

    return base_seconds

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/inventory")
def inventory():
    save_folder = load_app_config().get("save_folder", "")
    stash = load_inventory_stash(save_folder)
    return render_template("inventory.html", stash=stash)

@app.route("/stash")
def stash():
    sold_now = process_due_listings()
    listed_items = get_listed_items()

    return render_template(
        "stash.html",
        listed_items=listed_items,
        sold_now=sold_now,
    )


@app.route("/catalog")
def catalog():
    prices = load_token_prices()
    balance = get_token_balance()
    return render_template("catalog.html", prices=prices, balance=balance)


@app.route("/config")
def config():
    return render_template("config.html", save_folder=SAVE_FOLDER)

@app.route("/support")
def support():
    return render_template("support.html")

@app.route("/api/export_item", methods=["POST"])
def export_item():
    try:
        data = request.get_json()
        item = data.get("item")
        character_file = data.get("character_file")

        if not item:
            return jsonify({"success": False, "error": "Item not provided"}), 400

        item_id = export_item_to_marketplace(item, character_file)

        return jsonify({"success": True, "item_id": item_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/sell_item", methods=["POST"])
def sell_item():
    try:
        data = request.get_json()
        item_id = data.get("item_id")
        new_balance = sell_virtual_item(item_id)

        return jsonify({"success": True, "new_balance": new_balance})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/buy_item", methods=["POST"])
def buy_item():
    try:
        data = request.get_json()
        item_name = data.get("item_name")
        item_type = data.get("item_type")
        token_price = int(data.get("token_price"))
        qty = int(data.get("qty", 1))

        save_folder = load_app_config().get("save_folder", "")

        result = buy_catalog_item(
            item_name=item_name,
            item_type=item_type,
            token_price=token_price,
            save_folder=save_folder,
            qty=qty,
        )

        return jsonify({
            "success": True,
            "new_balance": result["new_balance"],
            "item_id": result["item_id"],
            "stash_path": result["stash_path"],
        })
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/import_item", methods=["POST"])
def import_item():
    try:
        data = request.get_json()
        item_id = data.get("item_id")

        save_folder = load_app_config().get("save_folder", "")
        import_virtual_item_to_game(item_id, save_folder)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
     
@app.route("/api/cancel_listing", methods=["POST"])
def cancel_listing():
    try:
        data = request.get_json() or {}
        listing_id = data.get("listing_id")

        if not listing_id:
            return jsonify({"error": "listing_id not provided"}), 400

        item = get_listed_item_by_id(listing_id)
        if not item:
            return jsonify({"error": "Listing not found"}), 404

        if item["status"] != "listed":
            return jsonify({"error": "Listing is no longer active"}), 400

        save_folder = load_app_config().get("save_folder", "")
        stash_file = find_shared_stash_file(save_folder)

        if not stash_file:
            return jsonify({"error": "Shared stash not found"}), 404

        write_item_to_shared_stash(
            stash_file,
            item_name=item["name"],
            item_code=item.get("item_code"),
            amount=item["quantity"]
        )

        ok = mark_listing_cancelled(listing_id)
        if not ok:
            return jsonify({"error": "Could not cancel listing"}), 400

        return jsonify({"success": True})

    except Exception as e:
        print("ERROR /api/cancel_listing:", repr(e))
        return jsonify({"error": str(e)}), 500 

@app.route("/api/update_save_folder", methods=["POST"])
def update_save_folder():
    global SAVE_FOLDER

    try:
        data = request.get_json()
        new_folder = data.get("save_folder")

        if not new_folder:
            return jsonify({"success": False, "error": "Folder not provided"}), 400

        if os.path.exists(new_folder):
            SAVE_FOLDER = new_folder
            save_app_config({
                "save_folder": SAVE_FOLDER
            })
            return jsonify({"success": True})

        return jsonify({"success": False, "error": "Folder not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@app.route("/api/sell_price_suggestion", methods=["POST"])
def sell_price_suggestion():
    data = request.get_json() or {}
    item = data.get("item") or {}

    item_name = item.get("itemName")
    item_kind = item.get("kind")

    if not item_name:
        return jsonify({"error": "Invalid item"}), 400

    pricing = get_sell_price_suggestion(
        item_name=item_name,
        item_kind=item_kind,
    )

    return jsonify({
        "success": True,
        **pricing,
    })    
        
@app.route("/api/list_item", methods=["POST"])
def list_item():
    data = request.get_json()

    item = data.get("item")
    quantity = int(data.get("quantity", 0))
    unit_price = int(data.get("unit_price", 0))
    stash_file = data.get("stash_file")

    if not item or quantity < 1 or unit_price < 1:
        return jsonify({"error": "Invalid data"}), 400

    item_name = item.get("itemName")
    item_code = item.get("code")
    item_kind = item.get("kind")

    if not item_name or not item_code:
        return jsonify({"error": "Invalid item"}), 400

    try:
        # validação real do stash
        inventory = load_inventory_stash(SAVE_FOLDER)
        real_item = next(
            (
                i for i in inventory.get("items", [])
                if str(i.get("code", "")).lower() == str(item_code).lower()
            ),
            None
        )

        real_qty = int(real_item.get("quantity", 0)) if real_item else 0
        if real_qty < quantity:
            return jsonify({
                "error": f"Quantidade insuficiente no stash para {item_name}. Atual={real_qty}, pedido={quantity}"
            }), 400

        write_item_to_shared_stash(
            stash_file,
            item_name=item_name,
            item_code=item_code,
            amount=-quantity
        )

        reference_price = get_market_reference_price(
            item_name=item_name,
            item_kind=item_kind,
        )

        sell_after = calculate_sell_after_seconds(
            unit_price=unit_price,
            reference_price=reference_price,
            item_kind=item_kind,
        )

        conn = get_connection()

        conn.execute("""
            INSERT INTO virtual_items
            (id, name, item_code, quantity, unit_price, status, listed_at, sell_after_seconds)
            VALUES (?, ?, ?, ?, ?, 'listed', ?, ?)
        """, (
            str(uuid.uuid4()),
            item_name,
            item_code,
            quantity,
            unit_price,
            datetime.now(UTC).isoformat(),
            sell_after
        ))

        conn.commit()

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500       


if __name__ == "__main__":
    app.run(debug=True, port=5000)
