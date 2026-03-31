# D2R Marketplace (Offline Auction House)

Simula uma Auction House para Diablo II: Resurrected em modo single player.

O projeto permite listar itens do shared stash, definir preços e vendê-los automaticamente ao longo do tempo, criando a sensação de um mercado ativo.

---

## ✨ Funcionalidades

- Leitura do shared stash (.d2i)
- Suporte a itens stackables:
  - Runas
  - Gemas
  - Poções de rejuvenation
- Sistema de venda estilo Auction House
- Economia baseada em tokens
- Preço dinâmico baseado em mercado
- Venda automática com tempo variável
- Cancelamento de anúncios
- Histórico de transações

---

## 🚀 Como rodar

```bash
pip install -r requirements.txt
python app.py

http://localhost:5000
