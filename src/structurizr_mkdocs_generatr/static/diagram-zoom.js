// Diagram zoom modal – preserves clickable SVG links inside <object> tags
document.addEventListener("DOMContentLoaded", function () {
  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".diagram-zoom-btn");
    if (!btn) return;

    e.preventDefault();
    e.stopPropagation();

    var src = btn.getAttribute("data-diagram-src");
    var title = btn.getAttribute("data-diagram-title") || "";

    // Build overlay
    var overlay = document.createElement("div");
    overlay.className = "diagram-modal-overlay";

    var closeBtn = document.createElement("button");
    closeBtn.className = "diagram-modal-close";
    closeBtn.setAttribute("title", "Close");
    closeBtn.innerHTML = "&times;";
    overlay.appendChild(closeBtn);

    var obj = document.createElement("object");
    obj.setAttribute("data", src);
    obj.setAttribute("type", "image/svg+xml");
    obj.className = "diagram";
    obj.textContent = title;
    overlay.appendChild(obj);

    document.body.appendChild(overlay);

    function close() {
      overlay.remove();
    }

    closeBtn.addEventListener("click", function (ev) {
      ev.stopPropagation();
      close();
    });

    overlay.addEventListener("click", function (ev) {
      // Only close when clicking the backdrop, not the diagram itself
      if (ev.target === overlay) {
        close();
      }
    });

    document.addEventListener("keydown", function handler(ev) {
      if (ev.key === "Escape") {
        close();
        document.removeEventListener("keydown", handler);
      }
    });
  });
});
