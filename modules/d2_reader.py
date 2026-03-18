import os


def find_save_files(save_folder):
    saves = []

    if not save_folder:
        return saves

    if os.path.exists(save_folder):
        for file in os.listdir(save_folder):
            if file.lower().endswith(".d2s"):
                saves.append(os.path.join(save_folder, file))

    return sorted(saves)


def get_character_name_from_file(save_file):
    return os.path.splitext(os.path.basename(save_file))[0]


def normalize_item(item):
    return {
        "name": str(getattr(item, "name", "Item desconhecido")),
        "item_type": str(getattr(item, "base_name", getattr(item, "type", "unknown"))),
        "quality": (
            "unique" if getattr(item, "is_unique", False)
            else "unknown"
        ),
    }


def try_read_items_with_d2lib(save_file):
    from d2lib.files import D2SFile

    d2s_file = D2SFile(save_file)
    raw_items = getattr(d2s_file, "items", []) or []

    return [normalize_item(item) for item in raw_items]


def get_all_characters_and_items(save_folder):
    save_files = find_save_files(save_folder)
    characters = []

    for save_file in save_files:
        character_name = get_character_name_from_file(save_file)

        try:
            items = try_read_items_with_d2lib(save_file)

            characters.append({
                "character_name": character_name,
                "character_file": save_file,
                "items": items,
                "item_count": len(items),
                "read_status": "Itens carregados com sucesso"
            })

        except ImportError as e:
            characters.append({
                "character_name": character_name,
                "character_file": save_file,
                "items": [],
                "item_count": 0,
                "read_status": f"Falha ao importar d2lib: {str(e)}"
            })

        except Exception as e:
            error_text = str(e)

            if "Invalid item header id" in error_text:
                readable_status = (
                    "Save encontrado, mas o parser atual não conseguiu ler os itens "
                    "(formato/estrutura do save incompatível com a biblioteca atual)"
                )
            else:
                readable_status = f"Leitura ainda não disponível neste formato: {error_text}"

            characters.append({
                "character_name": character_name,
                "character_file": save_file,
                "items": [],
                "item_count": 0,
                "read_status": readable_status
            })

    return characters