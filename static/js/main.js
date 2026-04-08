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
    showToast(text, type);
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
        throw new Error(`Invalid server response: ${text}`);
    }

    if (!response.ok) {
        throw new Error(data.error || `HTTP error ${response.status}`);
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
            activeButton.innerText = "Buying...";
        }

        const result = await postJson("/api/buy_item", {
            item_name: itemName,
            item_type: itemType,
            token_price: tokenPrice
        });

        if (result.success) {
            updateBalanceDisplay(result.new_balance);
            showMessage(`Purchase successful: ${itemName}`, "success");

            setTimeout(() => {
                window.location.reload();
            }, 700);
            return;
        }

        showMessage("Error: " + result.error, "error");
    } catch (error) {
        showMessage("Error purchasing item: " + error.message, "error");
        console.error(error);
    } finally {
        if (activeButton && activeButton.tagName === "BUTTON") {
            activeButton.disabled = false;
            activeButton.innerText = originalText || "Buy";
        }
    }
}

async function sellItem(itemId) {
    const activeButton = document.activeElement;
    const originalText = activeButton?.innerText;

    try {
        if (activeButton) {
            activeButton.disabled = true;
            activeButton.innerText = "Selling...";
        }

        const result = await postJson("/api/sell_item", {
            item_id: itemId
        });

        if (result.success) {
            updateBalanceDisplay(result.new_balance);
            showMessage("Item sold successfully!", "success");

            setTimeout(() => {
                window.location.reload();
            }, 600);

            return;
        }

        showMessage("Error: " + result.error, "error");

    } catch (error) {
        console.error(error);
        showMessage("Error selling item", "error");
    } finally {
        if (activeButton) {
            activeButton.disabled = false;
            activeButton.innerText = originalText || "Sell";
        }
    }
}

async function updateSaveFolder() {
    const input = document.getElementById("save_folder");
    if (!input) {
        showMessage("Save folder input not found.", "error");
        return;
    }

    try {
        const result = await postJson("/api/update_save_folder", {
            save_folder: input.value
        });

        if (result.success) {
            showMessage("Folder updated successfully!", "success");
            return;
        }

        showMessage("Error: " + result.error, "error");
    } catch (error) {
        showMessage("Error updating folder: " + error.message, "error");
        console.error(error);
    }
}

async function createStashBackup() {
  try {
    const res = await fetch("/api/create_stash_backup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      }
    });

    const data = await res.json();

    if (!res.ok) {
      showToast(data.error || "Failed to create backup.", "error");
      return;
    }

    if (data.backup_count > 0) {
      showToast(
        `Backup created (${data.backup_count} file${data.backup_count > 1 ? "s" : ""})`,
        "success"
      );
    } else {
      showToast("No stash files found to back up.", "error");
    }

  } catch (err) {
    console.error("createStashBackup error:", err);
    showToast("Unexpected error while creating backup.", "error");
  }
}

function showToast(message, type = "success", duration = 3000) {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;

  container.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.add("show");
  });

  setTimeout(() => {
    toast.classList.remove("show");

    setTimeout(() => {
      toast.remove();
    }, 250);
  }, duration);
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

function hideFloatingTooltip(tooltipEl) {
    if (!tooltipEl) return;

    tooltipEl.classList.remove("is-visible");
    tooltipEl.style.display = "";
    tooltipEl.style.visibility = "";
    tooltipEl.style.left = "";
    tooltipEl.style.top = "";
}

function formatTokenPrice(value) {
  const number = Number(value || 0);
  return number.toLocaleString("pt-BR");
}

async function loadSellPriceSuggestion(item) {
  const priceInput = document.getElementById("sell-unit-price");
  if (!priceInput) return;

  // fallback inicial
  priceInput.value = 1;

  try {
    const res = await postJson("/api/sell_price_suggestion", { item });

    if (!res || res.error || !res.success) {
      return;
    }

    if (Number(res.suggested_price) > 0) {
      priceInput.value = Number(res.suggested_price);
    }

  } catch (err) {
    console.error("loadSellPriceSuggestion error:", err);
  }
}

function openSellModal(item) {
    if (!item) {
        showMessage("Invalid item.", "error");
        return;
    }

    selectedSellItem = item;

    const modal = document.getElementById("sell-modal");
    if (!modal) {
        showMessage("Sell modal not found.", "error");
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

    loadSellPriceSuggestion(item);
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
        showMessage("No item selected.", "error");
        return;
    }

    const quantity = Number(document.getElementById("sell-quantity")?.value || 0);
    const unitPrice = Number(document.getElementById("sell-unit-price")?.value || 0);
    const availableQty = Number(selectedSellItem.quantity || 1);

    if (!Number.isInteger(quantity) || quantity < 1) {
        showMessage("Invalid quantity.", "error");
        return;
    }

    if (quantity > availableQty) {
        showMessage("Quantity exceeds available amount.", "error");
        return;
    }

    if (!Number.isInteger(unitPrice) || unitPrice < 1) {
        showMessage("Invalid unit price.", "error");
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
            showMessage(res?.error || "Error listing item.", "error");
            return;
        }

        showMessage("Item listed successfully!", "success");
        closeSellModal();
        setTimeout(() => window.location.reload(), 700);

    } catch (err) {
        showMessage(err?.message || "Error listing item.", "error");
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
        showMessage("Invalid listing.", "error");
        return;
    }

    try {
        const res = await postJson("/api/cancel_listing", {
            listing_id: listingId
        });

        if (!res || res.error) {
            showMessage(res?.error || "Error canceling listing.", "error");
            return;
        }

        showMessage("Listing canceled successfully.", "success");
        setTimeout(() => window.location.reload(), 700);
    } catch (err) {
        showMessage(err?.message || "Error canceling listing.", "error");
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