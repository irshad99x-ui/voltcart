// VoltCart Admin Dashboard JS
document.addEventListener("DOMContentLoaded", function () {
  // Chart initialization if canvas is present
  const ctx = document.getElementById("categoryChart");
  if (ctx && typeof Chart !== "undefined") {
    const labels = JSON.parse(ctx.getAttribute("data-labels") || "[]");
    const counts = JSON.parse(ctx.getAttribute("data-counts") || "[]");

    new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [
          {
            data: counts,
            backgroundColor: [
              "#0284c7",
              "#38bdf8",
              "#6366f1",
              "#8b5cf6",
              "#ec4899",
              "#f59e0b",
              "#10b981",
              "#64748b",
            ],
            borderWidth: 2,
            borderColor: "#ffffff",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              boxWidth: 12,
              padding: 14,
              font: { size: 11 },
            },
          },
        },
      },
    });
  }

  // Delete Confirmation Modal / Prompt
  const deleteForms = document.querySelectorAll(".form-delete-confirm");
  deleteForms.forEach((form) => {
    form.addEventListener("submit", function (e) {
      if (!confirm("Are you sure you want to permanently delete this item? This action cannot be undone.")) {
        e.preventDefault();
      }
    });
  });
});
