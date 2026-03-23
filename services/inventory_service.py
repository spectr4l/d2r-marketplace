import os

from modules.d2_reader import try_read_items_with_d2lib


def find_shared_stash_file(save_folder):
    if not save_folder or not os.path.isdir(save_folder):
        return None

    candidates = [
        "SharedStashSoftCoreV2.d2i",
        "ModernSharedStashSoftCoreV2.d2i",
    ]

    for file_name in candidates:
        full_path = os.path.join(save_folder, file_name)
        if os.path.isfile(full_path):
            return full_path

    return None


def build_readable_status(error_text):
    if "Unsupported version" in error_text:
        return "A versão do Shared Stash não é suportada pelo parser atual."

    if "Java não encontrado" in error_text:
        return "Java não encontrado no sistema."

    if "MODDED_ITEMS_DETECTED" in error_text:
        return "O stash possui itens modded/incompatíveis. Eles não são suportados nesta versão do sistema."

    if "IndexOutOfBoundsException" in error_text:
        return "O stash possui itens modded/incompatíveis. Eles não são suportados nesta versão do sistema."

    return f"Leitura ainda não disponível neste formato: {error_text}"


def get_shared_stash_data(save_folder):
    stash_file = find_shared_stash_file(save_folder)

    if not stash_file:
        return {
            "stash_name": "Shared Stash Softcore",
            "stash_file": None,
            "items": [],
            "item_count": 0,
            "read_status": "Arquivo SharedStashSoftCoreV2.d2i não encontrado.",
            "raw_error": None,
        }

    try:
        items = try_read_items_with_d2lib(stash_file)

        return {
            "stash_name": "Shared Stash Softcore",
            "stash_file": stash_file,
            "items": items,
            "item_count": len(items),
            "read_status": "Itens carregados com sucesso",
            "raw_error": None,
        }

    except Exception as e:
        error_text = repr(e)

        return {
            "stash_name": "Shared Stash Softcore",
            "stash_file": stash_file,
            "items": [],
            "item_count": 0,
            "read_status": build_readable_status(error_text),
            "raw_error": error_text,
        }