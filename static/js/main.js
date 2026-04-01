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
        const type = card.dataset.type || "";

        const matchesSearch = name.includes(search);
        const matchesFilter = filter === "all" || type === filter;

        card.style.display = (matchesSearch && matchesFilter) ? "block" : "none";
    });
}

function positionFloatingTooltip(tooltipEl, mouseX, mouseY) {
    if (!tooltipEl) return;

    const gap = 14;
    const viewportPadding = 12;

    tooltipEl.style.visibility = "hidden";
    tooltipEl.style.display = "block";
    tooltipEl.classList.add("is-visible");

    const rect = tooltipEl.getBoundingClientRect();

    let left = mouseX + gap;
    let top = mouseY + gap;

    if (left + rect.width > window.innerWidth - viewportPadding) {
        left = mouseX - rect.width - gap;
    }

    if (left < viewportPadding) {
        left = viewportPadding;
    }

    if (top + rect.height > window.innerHeight - viewportPadding) {
        top = mouseY - rect.height - gap;
    }

    if (top < viewportPadding) {
        top = viewportPadding;
    }

    tooltipEl.style.left = `${Math.round(left)}px`;
    tooltipEl.style.top = `${Math.round(top)}px`;
    tooltipEl.style.visibility = "visible";
}

function hideFloatingTooltip(tooltipEl) {
    if (!tooltipEl) return;

    tooltipEl.classList.remove("is-visible");
    tooltipEl.style.display = "";
    tooltipEl.style.visibility = "";
    tooltipEl.style.left = "";
    tooltipEl.style.top = "";
}

function bindFloatingTooltips(triggerSelector, tooltipSelector) {
    const triggers = document.querySelectorAll(triggerSelector);

    triggers.forEach((trigger) => {
        const tooltip = trigger.querySelector(tooltipSelector);
        if (!tooltip) return;

        trigger.addEventListener("mouseenter", (event) => {
            positionFloatingTooltip(tooltip, event.clientX, event.clientY);
        });

        trigger.addEventListener("mousemove", (event) => {
            positionFloatingTooltip(tooltip, event.clientX, event.clientY);
        });

        trigger.addEventListener("mouseleave", () => {
            hideFloatingTooltip(tooltip);
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    bindFloatingTooltips(".catalog-card", ".tooltip-panel");
    bindFloatingTooltips(".stash-item", ".item-tooltip");
});

function openSellModal(item) {
    if (!item) {
        showMessage("Item inválido.", "error");
        return;
    }

    selectedSellItem = item;

    const modal = document.getElementById("sell-modal");
    if (!modal) {
        showMessage("Modal de venda não encontrado.", "error");
        return;
    }

    const availableQty = Number(item.quantity || 1);

    document.getElementById("sell-item-name").textContent = item.itemName;
    document.getElementById("sell-item-available").textContent = availableQty;

    const qtyInput = document.getElementById("sell-quantity");
    qtyInput.value = 1;
    qtyInput.max = availableQty;

    document.getElementById("sell-unit-price").value = 1;

    modal.classList.add("is-open");
    document.body.classList.add("modal-open");
}

function closeSellModal() {
    selectedSellItem = null;

    const modal = document.getElementById("sell-modal");
    if (modal) {
        modal.classList.remove("is-open");
    }

    document.body.classList.remove("modal-open");
}

async function submitSellListing() {
    if (!selectedSellItem) {
        showMessage("Nenhum item selecionado.", "error");
        return;
    }

    const quantity = Number(document.getElementById("sell-quantity")?.value || 0);
    const unitPrice = Number(document.getElementById("sell-unit-price")?.value || 0);
    const availableQty = Number(selectedSellItem.quantity || 1);

    if (!Number.isInteger(quantity) || quantity < 1) {
        showMessage("Quantidade inválida.", "error");
        return;
    }

    if (quantity > availableQty) {
        showMessage("Quantidade maior que a disponível.", "error");
        return;
    }

    if (!Number.isInteger(unitPrice) || unitPrice < 1) {
        showMessage("Preço unitário inválido.", "error");
        return;
    }

    try {
        const res = await postJson("/api/list_item", {
            item: selectedSellItem,
            quantity,
            unit_price: unitPrice,
            stash_file: window.INVENTORY_STASH_FILE || null
        });

        if (!res || res.error) {
            showMessage(res?.error || "Erro ao anunciar item.", "error");
            return;
        }

        showMessage("Item anunciado com sucesso!", "success");
        closeSellModal();
        setTimeout(() => window.location.reload(), 700);

    } catch (err) {
        showMessage(err?.message || "Erro ao anunciar item.", "error");
        console.error("submitSellListing error:", err);
    }
}

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        closeSellModal();
    }
});

async function cancelListing(listingId) {
    if (!listingId) {
        showMessage("Listing inválido.", "error");
        return;
    }

    try {
        const res = await postJson("/api/cancel_listing", {
            listing_id: listingId
        });

        if (!res || res.error) {
            showMessage(res?.error || "Erro ao cancelar anúncio.", "error");
            return;
        }

        showMessage("Anúncio cancelado com sucesso.", "success");
        setTimeout(() => window.location.reload(), 700);
    } catch (err) {
        showMessage(err?.message || "Erro ao cancelar anúncio.", "error");
        console.error("cancelListing error:", err);
    }
}

function positionFloatingTooltip(tooltipEl, mouseX, mouseY) {
  if (!tooltipEl) return;

  const gap = 18;
  const viewportPadding = 12;

  tooltipEl.style.left = "0px";
  tooltipEl.style.top = "0px";
  tooltipEl.classList.add("is-visible");

  const rect = tooltipEl.getBoundingClientRect();

  let left = mouseX + gap;
  let top = mouseY + gap;

  if (left + rect.width > window.innerWidth - viewportPadding) {
    left = mouseX - rect.width - gap;
  }

  if (left < viewportPadding) {
    left = viewportPadding;
  }

  if (top + rect.height > window.innerHeight - viewportPadding) {
    top = window.innerHeight - rect.height - viewportPadding;
  }

  if (top < viewportPadding) {
    top = viewportPadding;
  }

  tooltipEl.style.left = `${left}px`;
  tooltipEl.style.top = `${top}px`;
}

function bindFloatingTooltips(triggerSelector, tooltipSelector) {
  const triggers = document.querySelectorAll(triggerSelector);

  triggers.forEach(trigger => {
    const tooltip = trigger.querySelector(tooltipSelector);
    if (!tooltip) return;

    trigger.addEventListener("mouseenter", (event) => {
      tooltip.classList.add("is-visible");
      positionFloatingTooltip(tooltip, event.clientX, event.clientY);
    });

    trigger.addEventListener("mousemove", (event) => {
      positionFloatingTooltip(tooltip, event.clientX, event.clientY);
    });

    trigger.addEventListener("mouseleave", () => {
      tooltip.classList.remove("is-visible");
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  bindFloatingTooltips(".catalog-card", ".tooltip-panel");
  bindFloatingTooltips(".stash-item", ".item-tooltip");
});