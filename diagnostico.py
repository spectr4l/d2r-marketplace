import os
import json

print("="*50)
print("DIAGNÓSTICO DO ARQUIVO DE PREÇOS")
print("="*50)

# Caminho do arquivo
file_path = os.path.join('data', 'item_prices.json')
print(f"Caminho absoluto: {os.path.abspath(file_path)}")

# Verificar se existe
if os.path.exists(file_path):
    print(" Arquivo existe")
    
    # Tamanho
    size = os.path.getsize(file_path)
    print(f" Tamanho: {size} bytes")
    
    # Ler conteúdo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f" Primeiros 100 caracteres:\n{content[:100]}")
        
        # Tentar parsear JSON
        try:
            data = json.loads(content)
            print(" JSON válido!")
            
            # Verificar estrutura
            if 'runes' in data:
                print(f" Encontradas {len(data['runes'])} runas")
                print("Primeiras 5 runas:")
                for i, (runa, preco) in enumerate(list(data['runes'].items())[:5]):
                    print(f"   {runa}: {preco} tokens")
            else:
                print(" Campo 'runes' não encontrado")
                
        except json.JSONDecodeError as e:
            print(f" Erro no JSON: {e}")
            print(f"   Linha: {e.lineno}, Coluna: {e.colno}")
            print(f"   Mensagem: {e.msg}")
else:
    print(" Arquivo NÃO existe")
    
    # Verificar se a pasta existe
    if os.path.exists('data'):
        print(" Pasta 'data' existe")
        print("Arquivos na pasta data:")
        for f in os.listdir('data'):
            print(f"   - {f}")
    else:
        print(" Pasta 'data' não existe")
print("="*50)
