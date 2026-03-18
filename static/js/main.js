function updateBalanceDisplay(newBalance) {
    const balanceDisplay = document.getElementById("balance-display");
    if (balanceDisplay) {
        balanceDisplay.textContent = newBalance;
    }

    const headerBalance = document.getElementById("balance-value");
    if (headerBalance) {
        headerBalance.textContent = newBalance;
    }
}

function showMessage(text, type = "success") {
    const area = document.getElementById("message-area");
    if (!area) return;

    area.innerHTML = `<div class="message ${type}">${text}</div>`;

    setTimeout(() => {
        area.innerHTML = "";
    }, 3500);
}

async function postJson(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });

    const text = await response.text();

    let data;
    try {
        data = JSON.parse(text);
    } catch (error) {
        throw new Error(`Resposta inválida do servidor: ${text}`);
    }

    if (!response.ok) {
        throw new Error(data.error || `Erro HTTP ${response.status}`);
    }

    return data;
}

async function buyItem(itemName, itemType, tokenPrice) {
    const activeButton = document.activeElement;
    const originalText = activeButton && activeButton.tagName === "BUTTON"
        ? activeButton.innerText
        : null;

    try {
        if (activeButton && activeButton.tagName === "BUTTON") {
            activeButton.disabled = true;
            activeButton.innerText = "Comprando...";
        }

        const result = await postJson("/api/buy_item", {
            item_name: itemName,
            item_type: itemType,
            token_price: tokenPrice
        });

        if (result.success) {
            updateBalanceDisplay(result.new_balance);
            showMessage(`Compra realizada: ${itemName}`, "success");

            setTimeout(() => {
                window.location.reload();
            }, 700);
            return;
        }

        showMessage("Erro: " + result.error, "error");
    } catch (error) {
        showMessage("Erro ao comprar item: " + error.message, "error");
        console.error(error);
    } finally {
        if (activeButton && activeButton.tagName === "BUTTON") {
            activeButton.disabled = false;
            activeButton.innerText = originalText || "Comprar";
        }
    }
}

async function sellItem(itemId) {
    const activeButton = document.activeElement;
    const originalText = activeButton?.innerText;

    try {
        if (activeButton) {
            activeButton.disabled = true;
            activeButton.innerText = "Vendendo...";
        }

        const result = await postJson("/api/sell_item", {
            item_id: itemId
        });

        if (result.success) {
            updateBalanceDisplay(result.new_balance);
            showMessage("Item vendido com sucesso!", "success");

            setTimeout(() => {
                window.location.reload();
            }, 600);

            return;
        }

        showMessage("Erro: " + result.error, "error");

    } catch (error) {
        console.error(error);
        showMessage("Erro ao vender item", "error");
    } finally {
        if (activeButton) {
            activeButton.disabled = false;
            activeButton.innerText = originalText || "Vender";
        }
    }
}

async function updateSaveFolder() {
    const input = document.getElementById("save_folder");
    if (!input) {
        showMessage("Campo da pasta não encontrado.", "error");
        return;
    }

    try {
        const result = await postJson("/api/update_save_folder", {
            save_folder: input.value
        });

        if (result.success) {
            showMessage("Pasta atualizada com sucesso!", "success");
            return;
        }

        showMessage("Erro: " + result.error, "error");
    } catch (error) {
        showMessage("Erro ao atualizar pasta: " + error.message, "error");
        console.error(error);
    }
}

function filterCatalogCards() {
    const searchInput = document.getElementById("catalog-search");
    const filterSelect = document.getElementById("catalog-filter");
    const cards = document.querySelectorAll(".catalog-card");

    if (!searchInput || !filterSelect) return;

    const search = searchInput.value.toLowerCase().trim();
    const filter = filterSelect.value;

    cards.forEach(card => {
        const name = card.dataset.name || "";
        const type = card.dataset.type || "";

        const matchesSearch = name.includes(search);
        const matchesFilter = filter === "all" || type === filter;

        card.style.display = (matchesSearch && matchesFilter) ? "block" : "none";
    });
}

function filterMarketplaceCards() {
    const searchInput = document.getElementById("marketplace-search");
    const filterSelect = document.getElementById("marketplace-filter");
    const cards = document.querySelectorAll(".marketplace-card");

    if (!searchInput || !filterSelect) return;

    const search = searchInput.value.toLowerCase().trim();
    const filter = filterSelect.value;

    cards.forEach(card => {
        const name = card.dataset.name || "";
        const quality = card.dataset.quality || "";

        const matchesSearch = name.includes(search);
        const matchesFilter = filter === "all" || quality === filter;

        card.style.display = (matchesSearch && matchesFilter) ? "block" : "none";
    });
}