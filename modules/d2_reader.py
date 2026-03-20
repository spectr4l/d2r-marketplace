import json
import os
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


def try_read_items_with_d2lib(save_file):
    command = [
        JAVA_CMD,
        "-cp",
        ".;lib/*",
        "Main",
        save_file
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
            f"Falha ao executar parser Java. "
            f"stdout={result.stdout!r} stderr={result.stderr!r}"
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
        items.append({
            "name": str(item.get("name", "Item desconhecido")),
            "item_type": str(item.get("type", "unknown")),
            "quality": str(item.get("quality", "unknown")).lower(),
            "quantity": int(item.get("quantity", 1)),
        })

    return items