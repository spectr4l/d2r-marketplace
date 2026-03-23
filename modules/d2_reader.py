import json
import os
import re
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARSER_DIR = os.path.join(BASE_DIR, "tools", "d2r_parser")
JAVA_CMD = "java"


def inspect_d2s_header(save_file):
    try:
        with open(save_file, "rb") as f:
            header = f.read(16)

        if len(header) < 16:
            return {
                "valid_header": False,
                "error": "Arquivo muito pequeno para conter cabeçalho válido.",
            }

        return {
            "valid_header": True,
            "raw_header_hex": header.hex(" "),
            "header_size": len(header),
        }
    except Exception as e:
        return {
            "valid_header": False,
            "error": repr(e),
        }

SKILL_ID_TO_NAME = {
    115: "Vigor",
    # adicione mais conforme for encontrando
}


def _extract_values(prop_text):
    match = re.search(r"values=\[([^\]]*)\]", prop_text)
    if not match:
        return []

    values = []
    for raw in match.group(1).split(","):
        raw = raw.strip()
        if not raw:
            continue
        try:
            values.append(int(raw))
        except ValueError:
            pass

    return values


def _extract_name(prop_text):
    match = re.search(r"name=([^,]+)", prop_text)
    return match.group(1).strip() if match else ""


def format_property(prop):
    text = str(prop)
    name = _extract_name(text)
    values = _extract_values(text)

    if name == "item_fastermovevelocity" and values:
        return f"{values[0]}% Faster Run/Walk"

    if name == "manadrainmindam" and values:
        return f"{values[0]}% Mana Stolen per Hit"

    if name == "lifedrainmindam" and values:
        return f"{values[0]}% Life Stolen per Hit"

    if name == "armorclass" and values:
        return f"+{values[0]} Defense"

    if name == "item_armor_percent" and values:
        return f"+{values[0]}% Enhanced Defense"

    if name == "strength" and values:
        return f"+{values[0]} to Strength"

    if name == "dexterity" and values:
        return f"+{values[0]} to Dexterity"

    if name == "energy" and values:
        return f"+{values[0]} to Energy"

    if name == "vitality" and values:
        return f"+{values[0]} to Vitality"

    if name == "fireresist" and values:
        return f"Fire Resist +{values[0]}%"

    if name == "lightresist" and values:
        return f"Lightning Resist +{values[0]}%"

    if name == "coldresist" and values:
        return f"Cold Resist +{values[0]}%"

    if name == "poisonresist" and values:
        return f"Poison Resist +{values[0]}%"

    if name == "damageresist" and values:
        return f"Damage Reduced by {values[0]}"

    if name == "magicresist" and values:
        return f"Magic Resist +{values[0]}%"

    if name == "item_lightradius" and values:
        return f"+{values[0]} to Light Radius"

    if name == "item_crushingblow" and values:
        return f"{values[0]}% Chance of Crushing Blow"

    if name == "item_deadlystrike" and values:
        return f"{values[0]}% Deadly Strike"

    if name == "item_openwounds" and values:
        return f"{values[0]}% Chance of Open Wounds"

    if name == "item_preventheal":
        return "Prevent Monster Heal"

    if name == "item_undeaddamage_percent" and values:
        return f"+{values[0]}% Damage to Undead"

    if name == "maxdurability" and values:
        return f"Increase Maximum Durability {values[0]}%"

    if name == "mindamage" and values:
        return f"+{values[0]} to Minimum Damage"

    if name == "maxdamage" and values:
        return f"+{values[0]} to Maximum Damage"

    if name == "item_mindamage_percent" and values:
        return f"+{values[0]}% Enhanced Damage"

    if name == "item_maxdamage_percent" and values:
        return f"+{values[0]}% Enhanced Damage"

    if name == "item_addclassskills" and len(values) >= 2:
        return f"+{values[1]} to Class Skills"

    if name == "item_singleskill" and len(values) >= 2:
        skill_id = values[0]
        skill_bonus = values[1]
        skill_name = SKILL_ID_TO_NAME.get(skill_id, f"Skill {skill_id}")
        return f"[RAW] {text}"

    return text


def build_tooltip(item):
    lines = []

    name = item.get("itemName") or item.get("name") or "Unknown Item"
    lines.append(name)

    quality = (item.get("quality") or "").upper()
    if quality not in ("", "NONE", "NORMAL"):
        lines.append(quality.title())

    if item.get("isRuneword"):
        lines.append("Runeword")

    if item.get("isEthereal"):
        lines.append("Ethereal")

    base_def = int(item.get("baseDefense", 0) or 0)
    if base_def > 0:
        lines.append(f"Defense: {base_def}")

    durability = int(item.get("durability", 0) or 0)
    max_durability = int(item.get("maxDurability", 0) or 0)
    if max_durability > 0:
        lines.append(f"Durability: {durability} of {max_durability}")

    sockets = int(item.get("cntSockets", 0) or 0)
    if sockets > 0:
        lines.append(f"Sockets: {sockets}")

    req_str = int(item.get("reqStr", 0) or 0)
    req_dex = int(item.get("reqDex", 0) or 0)
    req_lvl = int(item.get("reqLvl", 0) or 0)

    if req_str > 0:
        lines.append(f"Required Strength: {req_str}")
    if req_dex > 0:
        lines.append(f"Required Dexterity: {req_dex}")
    if req_lvl > 0:
        lines.append(f"Required Level: {req_lvl}")

    enhanced_damage_added = False

    for prop in item.get("properties", []):
        prop_name = _extract_name(str(prop))
        line = format_property(prop)

        if prop_name in ("item_mindamage_percent", "item_maxdamage_percent"):
            if enhanced_damage_added:
                continue
            enhanced_damage_added = True

        lines.append(line)

    return lines


def try_read_items_with_d2lib(save_file):
    command = [
        JAVA_CMD,
        "-cp",
        ".;lib/*",
        "Main",
        save_file,
    ]

    result = subprocess.run(
        command,
        cwd=PARSER_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if result.returncode != 0:
        raise Exception(
            f"Falha ao executar parser Java. stdout={result.stdout!r} stderr={result.stderr!r}"
        )

    output = result.stdout.strip()
    if not output:
        raise Exception("Parser Java não retornou nenhuma saída.")

    lines = [line.strip() for line in output.splitlines() if line.strip()]
    json_line = None

    for line in reversed(lines):
        if line.startswith("{") and line.endswith("}"):
            json_line = line
            break

    if not json_line:
        raise Exception(f"Saída inválida do parser Java: {output!r}")

    try:
        data = json.loads(json_line)
    except json.JSONDecodeError as e:
        raise Exception(f"JSON inválido do parser Java: {json_line!r}") from e

    if "error" in data:
        raise Exception(data["error"])

    items = []
    for item in data.get("items", []):
        quantity = int(item.get("stacks", 0) or 0)
        if quantity <= 0:
            quantity = 1

        parsed_item = {
            "name": str(item.get("name", "Item desconhecido")),
            "itemName": str(item.get("itemName", item.get("name", "Item desconhecido"))),
            "item_type": str(item.get("itemType", item.get("type", "unknown"))),
            "type": str(item.get("type", "unknown")),
            "quality": str(item.get("quality", "unknown")).lower(),
            "quantity": quantity,
            "stacks": int(item.get("stacks", 0) or 0),
            "maxStacks": int(item.get("maxStacks", 0) or 0),
            "code": str(item.get("code", "")),
            "baseDefense": int(item.get("baseDefense", 0) or 0),
            "durability": int(item.get("durability", 0) or 0),
            "maxDurability": int(item.get("maxDurability", 0) or 0),
            "reqStr": int(item.get("reqStr", 0) or 0),
            "reqDex": int(item.get("reqDex", 0) or 0),
            "reqLvl": int(item.get("reqLvl", 0) or 0),
            "cntSockets": int(item.get("cntSockets", 0) or 0),
            "cntFilledSockets": int(item.get("cntFilledSockets", 0) or 0),
            "isEthereal": bool(item.get("isEthereal", False)),
            "isRuneword": bool(item.get("isRuneword", False)),
            "isIdentified": bool(item.get("isIdentified", False)),
            "invWidth": int(item.get("invWidth", 1) or 1),
            "invHeight": int(item.get("invHeight", 1) or 1),
            "x": int(item.get("x", 0) or 0),
            "y": int(item.get("y", 0) or 0),
            "properties": item.get("properties", []),
            "socketedItems": item.get("socketedItems", []),
        }

        parsed_item["tooltip_lines"] = build_tooltip(parsed_item)
        items.append(parsed_item)

    return items