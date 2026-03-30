# 🛒 D2R Marketplace (Offline Auction House)

Um marketplace local para **Diablo II: Resurrected**, onde você pode vender itens diretamente do seu stash (`.d2i`) e simular uma economia com tokens.

> ⚠️ Projeto em desenvolvimento — atualmente focado em runas (stackables)

---

## ✨ Funcionalidades atuais

### 📦 Inventário

* Leitura do `SharedStashSoftCoreV2.d2i`
* Exibição de itens com tooltip
* Detecção de runas automaticamente

### 💰 Sistema de venda

* Botão **Vender** por item
* Modal com:

  * quantidade
  * preço por unidade
* Remoção direta do item do `.d2i`

### 🏪 Auction House (/stash)

* Lista itens anunciados
* Mostra:

  * quantidade
  * preço unitário
  * total
* Botão **Cancelar anúncio**

### ⏱️ Venda automática

* Delay aleatório: **5–10 segundos**
* Após o tempo:

  * item é vendido automaticamente
  * removido da listagem
  * tokens creditados ao usuário

### 💳 Sistema de tokens

* Saldo persistido no banco SQLite
* Transações registradas:

  * vendas automáticas
  * outras operações futuras

---

## 🧠 Como funciona

### Fluxo completo

1. Usuário abre `/inventory`
2. Clica em **Vender**
3. Define quantidade + preço
4. Sistema:

   * remove item do `.d2i`
   * cria registro `listed` no banco
5. Item aparece em `/stash`
6. Após 5–10s:

   * item é marcado como `sold`
   * tokens são creditados

---

## ⚙️ Tecnologias

* Python (Flask)
* SQLite
* JavaScript (Vanilla)
* Node.js (patcher do stash)
* HTML + CSS

---

## 🚀 Como rodar

### 1. Clonar o projeto

```bash
git clone https://github.com/seu-repo/d2r-marketplace.git
cd d2r-marketplace
```

### 2. Instalar dependências Python

```bash
pip install flask
```

### 3. Garantir Node.js instalado

Necessário para o patcher do `.d2i`

```bash
node -v
```

### 4. Configurar saves

Coloque seu stash em:

```
/saves/SharedStashSoftCoreV2.d2i
```

### 5. Rodar o servidor

```bash
python app.py
```

### 6. Acessar

```
http://127.0.0.1:5000/inventory
```

---

## ⚠️ Limitações atuais

* Apenas **runas (stackables)** são suportadas
* Venda é **simulada (não multiplayer real)**
* Processamento de venda ocorre ao acessar `/stash`
* Não há autenticação de usuários

---

## 🔮 Próximos passos

* [ ] Suporte a itens não-stackáveis
* [ ] Contador visual de venda (tempo restante)
* [ ] Auto-refresh da stash
* [ ] Histórico de transações (UI)
* [ ] Filtros e busca na auction house
* [ ] Sistema real de compra entre usuários

---

## 🛠️ Observações técnicas

* O sistema usa patch em `.d2i` via Node para:

  * adicionar/remover runas
* Banco SQLite é atualizado em tempo real
* Datas usam UTC (`datetime.now(UTC)`)
* Sistema evita lock usando conexão única em operações críticas

---

## 💡 Ideia do projeto

Criar uma **economia offline simulada para D2R**, permitindo:

* testar valores de mercado
* simular trading
* explorar automação de stash

---

## 🧑‍💻 Autor

Desenvolvido como projeto experimental de integração entre:

* parsing de arquivos binários
* backend Flask
* frontend leve

---

## 📜 Licença

Uso livre para fins educacionais e experimentais.
