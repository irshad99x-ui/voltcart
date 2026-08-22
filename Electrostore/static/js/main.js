// VoltCart Main JS
document.addEventListener("DOMContentLoaded", function () {
  // 1. Live Search Suggestions
  const searchInput = document.getElementById("search-input");
  const suggestBox = document.getElementById("search-suggestions");

  if (searchInput && suggestBox) {
    let debounceTimer;
    searchInput.addEventListener("input", function () {
      clearTimeout(debounceTimer);
      const query = this.value.trim();

      if (query.length < 2) {
        suggestBox.style.display = "none";
        suggestBox.innerHTML = "";
        return;
      }

      debounceTimer = setTimeout(() => {
        fetch(`/api/search-suggest?q=${encodeURIComponent(query)}`)
          .then((res) => res.json())
          .then((data) => {
            if (data.length > 0) {
              suggestBox.innerHTML = data
                .map(
                  (item) => `
                <a href="/product/${item.slug}" class="suggest-item">
                  <img src="${item.image}" alt="${item.name}" />
                  <div class="flex-grow-1">
                    <div class="fw-semibold text-truncate" style="max-width: 320px;">${item.name}</div>
                    <small class="text-muted">${item.brand} • ${item.category}</small>
                  </div>
                  <div class="fw-bold text-primary">${item.price}</div>
                </a>
              `
                )
                .join("");
              suggestBox.style.display = "block";
            } else {
              suggestBox.innerHTML =
                '<div class="p-3 text-muted text-center small">No matching electronics found</div>';
              suggestBox.style.display = "block";
            }
          })
          .catch((err) => console.error("Search error:", err));
      }, 250);
    });

    // Close suggestion on click outside
    document.addEventListener("click", function (e) {
      if (!searchInput.contains(e.target) && !suggestBox.contains(e.target)) {
        suggestBox.style.display = "none";
      }
    });
  }

  // 2. Flash Deals Countdown Timer
  const countdownEl = document.getElementById("deal-countdown");
  if (countdownEl) {
    let targetTime = new Date().getTime() + 18 * 60 * 60 * 1000 + 45 * 60 * 1000; // 18h 45m from now
    function updateCountdown() {
      const now = new Date().getTime();
      const distance = targetTime - now;
      if (distance < 0) {
        countdownEl.innerHTML = "Deal ended!";
        return;
      }
      const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((distance % (1000 * 60)) / 1000);

      document.getElementById("cd-hours").textContent = String(hours).padStart(2, "0");
      document.getElementById("cd-mins").textContent = String(minutes).padStart(2, "0");
      document.getElementById("cd-secs").textContent = String(seconds).padStart(2, "0");
    }
    setInterval(updateCountdown, 1000);
    updateCountdown();
  }

  // 3. Product Detail Thumbnail Switcher
  const mainImage = document.getElementById("main-product-img");
  const thumbs = document.querySelectorAll(".product-thumbnail");
  if (mainImage && thumbs.length > 0) {
    thumbs.forEach((thumb) => {
      thumb.addEventListener("click", function () {
        thumbs.forEach((t) => t.classList.remove("border-primary", "active"));
        this.classList.add("border-primary", "active");
        mainImage.src = this.getAttribute("data-img-url");
      });
    });
  }
});

// Global Toast Notification Helper
function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const bgClass = type === "success" ? "bg-success" : type === "danger" ? "bg-danger" : "bg-primary";
  const icon = type === "success" ? "fa-circle-check" : type === "danger" ? "fa-circle-xmark" : "fa-info-circle";

  const toastEl = document.createElement("div");
  toastEl.className = `toast align-items-center text-white ${bgClass} border-0 shadow-lg mb-2 show`;
  toastEl.setAttribute("role", "alert");
  toastEl.innerHTML = `
    <div class="d-flex">
      <div class="toast-body d-flex align-items-center gap-2">
        <i class="fa-solid ${icon}"></i>
        <div>${message}</div>
      </div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  `;

  container.appendChild(toastEl);
  setTimeout(() => {
    toastEl.classList.remove("show");
    setTimeout(() => toastEl.remove(), 400);
  }, 3500);
}
