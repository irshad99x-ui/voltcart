// VoltCart Interactive Cart & Wishlist System
document.addEventListener("DOMContentLoaded", function () {
  // 1. AJAX Add to Cart
  document.addEventListener("click", function (e) {
    const addBtn = e.target.closest(".btn-add-to-cart");
    if (addBtn) {
      e.preventDefault();
      const productId = addBtn.getAttribute("data-product-id");
      const qtyInput = document.getElementById("product-quantity");
      const quantity = qtyInput ? parseInt(qtyInput.value) || 1 : 1;

      addBtn.disabled = true;
      const originalHtml = addBtn.innerHTML;
      addBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Adding...';

      fetch("/api/cart/add", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ product_id: productId, quantity: quantity }),
      })
        .then((res) => res.json())
        .then((data) => {
          addBtn.disabled = false;
          addBtn.innerHTML = originalHtml;

          if (data.success) {
            // Update global cart badge
            const badge = document.getElementById("header-cart-badge");
            if (badge) {
              badge.textContent = data.cart_count;
              badge.style.display = data.cart_count > 0 ? "inline-block" : "none";
            }
            showToast(data.message, "success");
          } else {
            showToast(data.message || "Failed to add product.", "danger");
          }
        })
        .catch((err) => {
          addBtn.disabled = false;
          addBtn.innerHTML = originalHtml;
          console.error("Cart error:", err);
          showToast("Network error. Please try again.", "danger");
        });
    }
  });

  // 2. AJAX Wishlist Toggle
  document.addEventListener("click", function (e) {
    const wishBtn = e.target.closest(".btn-toggle-wishlist");
    if (wishBtn) {
      e.preventDefault();
      const productId = wishBtn.getAttribute("data-product-id");

      fetch(`/api/wishlist/toggle/${productId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      })
        .then((res) => {
          if (res.status === 401 || res.redirected) {
            window.location.href = "/login";
            return;
          }
          return res.json();
        })
        .then((data) => {
          if (!data) return;
          if (data.success) {
            wishBtn.classList.toggle("active", data.in_wishlist);
            const icon = wishBtn.querySelector("i");
            if (icon) {
              if (data.in_wishlist) {
                icon.classList.remove("fa-regular");
                icon.classList.add("fa-solid", "text-danger");
              } else {
                icon.classList.remove("fa-solid", "text-danger");
                icon.classList.add("fa-regular");
              }
            }
            // Update header wishlist badge
            const badge = document.getElementById("header-wishlist-badge");
            if (badge) {
              badge.textContent = data.count;
              badge.style.display = data.count > 0 ? "inline-block" : "none";
            }
            showToast(data.message, data.in_wishlist ? "success" : "primary");
          }
        })
        .catch((err) => console.error("Wishlist error:", err));
    }
  });

  // 3. Cart Page Quantity Increment / Decrement
  const cartTable = document.getElementById("cart-table-body");
  if (cartTable) {
    // Quantity change buttons
    cartTable.addEventListener("click", function (e) {
      const qtyBtn = e.target.closest(".cart-qty-btn");
      if (qtyBtn) {
        const itemId = qtyBtn.getAttribute("data-item-id");
        const action = qtyBtn.getAttribute("data-action");
        const inputEl = document.getElementById(`cart-qty-${itemId}`);
        let currentVal = parseInt(inputEl.value) || 1;

        if (action === "increase") {
          currentVal += 1;
        } else if (action === "decrease") {
          currentVal = Math.max(1, currentVal - 1);
        }

        inputEl.value = currentVal;
        updateCartItem(itemId, currentVal);
      }

      // Remove button
      const removeBtn = e.target.closest(".cart-remove-btn");
      if (removeBtn) {
        const itemId = removeBtn.getAttribute("data-item-id");
        removeCartItem(itemId);
      }
    });

    // Direct input change
    cartTable.addEventListener("change", function (e) {
      if (e.target.classList.contains("cart-qty-input")) {
        const itemId = e.target.getAttribute("data-item-id");
        let val = parseInt(e.target.value) || 1;
        if (val < 1) val = 1;
        e.target.value = val;
        updateCartItem(itemId, val);
      }
    });
  }

  function updateCartItem(itemId, quantity) {
    fetch("/api/cart/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item_id: itemId, quantity: quantity }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          // Update item subtotal
          const itemSubtotalEl = document.getElementById(`item-subtotal-${itemId}`);
          if (itemSubtotalEl) itemSubtotalEl.textContent = data.item_subtotal;

          // Update summary block
          updateSummaryBlock(data);
        }
      });
  }

  function removeCartItem(itemId) {
    fetch("/api/cart/remove", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item_id: itemId }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          const row = document.getElementById(`cart-row-${itemId}`);
          if (row) row.remove();

          updateSummaryBlock(data);
          showToast(data.message, "primary");

          if (data.cart_count === 0) {
            window.location.reload();
          }
        }
      });
  }

  function updateSummaryBlock(data) {
    const badge = document.getElementById("header-cart-badge");
    if (badge) {
      badge.textContent = data.cart_count;
      badge.style.display = data.cart_count > 0 ? "inline-block" : "none";
    }

    const subtotalEl = document.getElementById("cart-subtotal");
    if (subtotalEl) subtotalEl.textContent = data.subtotal;

    const shippingEl = document.getElementById("cart-shipping");
    if (shippingEl) shippingEl.textContent = data.shipping_fee;

    const discountEl = document.getElementById("cart-discount");
    if (discountEl) discountEl.textContent = data.discount_amount;

    const taxEl = document.getElementById("cart-tax");
    if (taxEl) taxEl.textContent = data.tax_amount;

    const totalEl = document.getElementById("cart-total");
    if (totalEl) totalEl.textContent = data.total_amount;
  }
});
