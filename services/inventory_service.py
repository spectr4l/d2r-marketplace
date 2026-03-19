import os

from modules.d2_reader import try_read_items_with_d2lib, inspect_d2s_header


def find_save_files(save_folder):
    saves = []

    if not save_folder:
        return saves

    if os.path.isdir(save_folder):
        for file_name in os.listdir(save_folder):
            if file_name.lower().endswith(".d2s"):
                saves.append(os.path.join(save_folder, file_name))

    return sorted(saves)


def get_character_name_from_file(save_file):
    return os.path.splitext(os.path.basename(save_file))[0]


def build_readable_status(error_text):
    if "Invalid item header id" in error_text:
        return (
            "Save encontrado, mas o parser atual não conseguiu ler os itens "
            "(estrutura incompatível com a biblioteca atual)."
        )

    if "UnicodeDecodeError" in error_text and "ascii" in error_text:
        return (
            "Save encontrado, mas a biblioteca atual tentou interpretar bytes "
            "binários do arquivo como texto ASCII. Isso indica incompatibilidade "
            "do parser com o formato atual do save do D2R."
        )

    if "No module named" in error_text and "d2lib" in error_text:
        return "A biblioteca d2lib não está instalada no ambiente atual."

    return f"Leitura ainda não disponível neste formato: {error_text}"


def get_all_characters_and_items(save_folder):
    save_files = find_save_files(save_folder)
    characters = []

    for save_file in save_files:
        character_name = get_character_name_from_file(save_file)
        header_info = inspect_d2s_header(save_file)

        try:
            items = try_read_items_with_d2lib(save_file)

            print(f"Arquivo: {save_file}")
            print(f"Itens lidos: {len(items)}")

            characters.append({
                "character_name": character_name,
                "character_file": save_file,
                "items": items,
                "item_count": len(items),
                "read_status": "Itens carregados com sucesso",
                "raw_error": None,
                "header_info": header_info,
            })

        except ImportError as e:
            error_text = repr(e)

            print(f"Erro ao ler {save_file}: {error_text}")

            characters.append({
                "character_name": character_name,
                "character_file": save_file,
                "items": [],
                "item_count": 0,
                "read_status": f"Falha ao importar d2lib: {str(e)}",
                "raw_error": error_text,
                "header_info": header_info,
            })

        except Exception as e:
            error_text = repr(e)
            readable_status = build_readable_status(error_text)

            print(f"Erro ao ler {save_file}: {error_text}")

            characters.append({
                "character_name": character_name,
                "character_file": save_file,
                "items": [],
                "item_count": 0,
                "read_status": readable_status,
                "raw_error": error_text,
                "header_info": header_info,
            })

    return characters