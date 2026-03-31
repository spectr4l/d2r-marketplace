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
    get_connection,
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
        "weapon": "+50 para Attack Rating, +1 de raio de luz",
        "armor": "+15 de defesa, +1 de raio de luz",
        "shield": "+1 de raio de luz"
    },
    "Eld": {
        "weapon": "+75% dano contra mortos-vivos, +50 Attack Rating contra mortos-vivos",
        "armor": "15% stamina drenada mais lentamente",
        "shield": "7% maior chance de bloqueio"
    },
    "Tir": {
        "weapon": "+2 mana após cada abate",
        "armor": "+2 mana após cada abate",
        "shield": "+2 mana após cada abate"
    },
    "Nef": {
        "weapon": "Knockback",
        "armor": "+30 defesa contra projéteis",
        "shield": "+30 defesa contra projéteis"
    },
    "Eth": {
        "weapon": "-25% defesa do alvo",
        "armor": "Regenera mana em 15%",
        "shield": "Regenera mana em 15%"
    },
    "Ith": {
        "weapon": "+9 de dano máximo",
        "armor": "15% do dano recebido vai para mana",
        "shield": "15% do dano recebido vai para mana"
    },
    "Tal": {
        "weapon": "+75 dano de veneno por 5 segundos",
        "armor": "+30% resistência a veneno",
        "shield": "+35% resistência a veneno"
    },
    "Ral": {
        "weapon": "Adiciona 5-30 de dano de fogo",
        "armor": "+30% resistência a fogo",
        "shield": "+35% resistência a fogo"
    },
    "Ort": {
        "weapon": "Adiciona 1-50 de dano elétrico",
        "armor": "+30% resistência a raio",
        "shield": "+35% resistência a raio"
    },
    "Thul": {
        "weapon": "Adiciona 3-14 de dano de gelo",
        "armor": "+30% resistência a gelo",
        "shield": "+35% resistência a gelo"
    },
    "Amn": {
        "weapon": "7% life stolen per hit",
        "armor": "Atacante sofre 14 de dano",
        "shield": "Atacante sofre 14 de dano"
    },
    "Sol": {
        "weapon": "+9 de dano mínimo",
        "armor": "Reduz dano em 7",
        "shield": "Reduz dano em 7"
    },
    "Shael": {
        "weapon": "20% increased attack speed",
        "armor": "20% faster hit recovery",
        "shield": "20% faster block rate"
    },
    "Dol": {
        "weapon": "Hit causes monster to flee 25%",
        "armor": "Replenish life +7",
        "shield": "Replenish life +7"
    },
    "Hel": {
        "weapon": "Requisitos -20%",
        "armor": "Requisitos -15%",
        "shield": "Requisitos -15%"
    },
    "Io": {
        "weapon": "+10 vitalidade",
        "armor": "+10 vitalidade",
        "shield": "+10 vitalidade"
    },
    "Lum": {
        "weapon": "+10 energia",
        "armor": "+10 energia",
        "shield": "+10 energia"
    },
    "Ko": {
        "weapon": "+10 destreza",
        "armor": "+10 destreza",
        "shield": "+10 destreza"
    },
    "Fal": {
        "weapon": "+10 força",
        "armor": "+10 força",
        "shield": "+10 força"
    },
    "Lem": {
        "weapon": "75% gold extra de monstros",
        "armor": "50% gold extra de monstros",
        "shield": "50% gold extra de monstros"
    },
    "Pul": {
        "weapon": "+75% dano contra demônios, +100 AR contra demônios",
        "armor": "+30% defesa aprimorada",
        "shield": "+30% defesa aprimorada"
    },
    "Um": {
        "weapon": "25% chance de feridas abertas",
        "armor": "+15% todas as resistências",
        "shield": "+22% todas as resistências"
    },
    "Mal": {
        "weapon": "Prevent Monster Heal",
        "armor": "Magic Damage Reduced by 7",
        "shield": "Magic Damage Reduced by 7"
    },
    "Ist": {
        "weapon": "30% melhor chance de itens mágicos",
        "armor": "25% melhor chance de itens mágicos",
        "shield": "25% melhor chance de itens mágicos"
    },
    "Gul": {
        "weapon": "20% bônus para attack rating",
        "armor": "+5% maximum poison resist",
        "shield": "+5% maximum poison resist"
    },
    "Vex": {
        "weapon": "7% mana stolen per hit",
        "armor": "+5% maximum fire resist",
        "shield": "+5% maximum fire resist"
    },
    "Ohm": {
        "weapon": "+50% enhanced damage",
        "armor": "+5% maximum cold resist",
        "shield": "+5% maximum cold resist"
    },
    "Lo": {
        "weapon": "20% deadly strike",
        "armor": "+5% maximum lightning resist",
        "shield": "+5% maximum lightning resist"
    },
    "Sur": {
        "weapon": "Hit blinds target",
        "armor": "Aumenta mana máxima em 5%",
        "shield": "+50 mana"
    },
    "Ber": {
        "weapon": "20% crushing blow",
        "armor": "Reduz dano em 8%",
        "shield": "Reduz dano em 8%"
    },
    "Jah": {
        "weapon": "Ignora defesa do alvo",
        "armor": "Aumenta vida máxima em 5%",
        "shield": "+50 vida"
    },
    "Cham": {
        "weapon": "Freeze target +3",
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
    return rune_data.get(slot, "Sem informação")

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
    if os.path.exists(TOKEN_PRICES_FILE):
        with open(TOKEN_PRICES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    default_prices = {
        "runes": {
            "El": 1, "Eld": 2, "Tir": 3, "Nef": 4, "Eth": 5,
            "Ith": 6, "Tal": 7, "Ral": 8, "Ort": 9, "Thul": 10,
            "Amn": 15, "Sol": 20, "Shael": 25, "Dol": 30,
            "Hel": 40, "Io": 45, "Lum": 50, "Ko": 60,
            "Fal": 70, "Lem": 80, "Pul": 90, "Um": 100,
            "Mal": 120, "Ist": 150, "Gul": 180, "Vex": 210,
            "Ohm": 250, "Lo": 300, "Sur": 350, "Ber": 400,
            "Jah": 450, "Cham": 500, "Zod": 600
        },
        "uniques": {
            "Harlequin Crest": 300,
            "The Grandfather": 250,
            "Windforce": 350
        }
    }

    os.makedirs(DATA_DIR, exist_ok=True)

    with open(TOKEN_PRICES_FILE, "w", encoding="utf-8") as f:
        json.dump(default_prices, f, indent=2, ensure_ascii=False)

    return default_prices


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


@app.route("/api/export_item", methods=["POST"])
def export_item():
    try:
        data = request.get_json()
        item = data.get("item")
        character_file = data.get("character_file")

        if not item:
            return jsonify({"success": False, "error": "Item não enviado"}), 400

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
            return jsonify({"error": "listing_id não informado"}), 400

        item = get_listed_item_by_id(listing_id)
        if not item:
            return jsonify({"error": "Anúncio não encontrado"}), 404

        if item["status"] != "listed":
            return jsonify({"error": "Anúncio não está mais ativo"}), 400

        # devolve o item ao shared stash
        save_folder = load_app_config().get("save_folder", "")
        stash_file = find_shared_stash_file(save_folder)

        if not stash_file:
            return jsonify({"error": "Shared stash não encontrado"}), 404

        write_item_to_shared_stash(
            stash_file,
            item_name=item["name"],
            item_code=item.get("item_code"),
            amount=item["quantity"]
        )

        ok = mark_listing_cancelled(listing_id)
        if not ok:
            return jsonify({"error": "Não foi possível cancelar o anúncio"}), 400

        return jsonify({"success": True})

    except Exception as e:
        print("ERRO /api/cancel_listing:", repr(e))
        return jsonify({"error": str(e)}), 500 

@app.route("/api/update_save_folder", methods=["POST"])
def update_save_folder():
    global SAVE_FOLDER

    try:
        data = request.get_json()
        new_folder = data.get("save_folder")

        if not new_folder:
            return jsonify({"success": False, "error": "Pasta não informada"}), 400

        if os.path.exists(new_folder):
            SAVE_FOLDER = new_folder
            save_app_config({
                "save_folder": SAVE_FOLDER
            })
            return jsonify({"success": True})

        return jsonify({"success": False, "error": "Pasta não encontrada"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
        
@app.route("/api/list_item", methods=["POST"])
def list_item():
    data = request.get_json()

    item = data.get("item")
    quantity = int(data.get("quantity", 0))
    unit_price = int(data.get("unit_price", 0))
    stash_file = data.get("stash_file")

    if not item or quantity < 1 or unit_price < 1:
        return jsonify({"error": "Dados inválidos"}), 400

    item_name = item.get("itemName")
    item_code = item.get("code")
    item_kind = item.get("kind")

    if not item_name or not item_code:
        return jsonify({"error": "Item inválido"}), 400

    try:
        # 🧨 1. REMOVE DO .d2i
        write_item_to_shared_stash(
            stash_file,
            item_name=item_name,
            item_code=item_code,
            amount=-quantity
        )

        # ⏱️ 2. DEFINE TEMPO DE VENDA (5–10s)
        sell_after = random.randint(5, 10)

        # 💾 3. SALVA NO BANCO
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