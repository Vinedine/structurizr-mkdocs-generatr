// Diagram zoom modal — used by <object>-embedded SVG diagrams (PlantUML)
// and client-side rendered Mermaid diagrams.
// Toolbar: zoom out / percentage / zoom in / reset / close.
// Zoom via buttons or Ctrl+wheel; pan via the viewport's scrollbars.
// NOTE: runs at script evaluation, NOT on DOMContentLoaded — Material's
// bundle detaches Mermaid blocks before DOMContentLoaded fires, so the
// source must be stashed synchronously while the <pre> is still in the DOM.
(function () {
  var ZOOM_STEP = 1.25;
  var MIN_SCALE = 0.1;
  var MAX_SCALE = 10;

  var ZOOM_ICON =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"' +
    ' width="20" height="20" fill="currentColor">' +
    '<path d="M15 3l2.3 2.3-2.89 2.87 1.42 1.42L18.7 6.7 21 9V3h-6z' +
    "M3 9l2.3-2.3 2.87 2.89 1.42-1.42L6.7 5.3 9 3H3v6z" +
    "m6 12l-2.3-2.3 2.89-2.87-1.42-1.42L5.3 17.3 3 15v6h6z" +
    'm12-6l-2.3 2.3-2.87-2.89-1.42 1.42 2.89 2.87L15 21h6v-6z"/></svg>';

  // content: element placed in the scrollable viewport (object or cloned svg)
  function openModal(content) {
    var overlay = document.createElement("div");
    overlay.className = "diagram-modal-overlay";

    var toolbar = document.createElement("div");
    toolbar.className = "diagram-modal-toolbar";

    function toolButton(label, tooltip) {
      var b = document.createElement("button");
      b.className = "diagram-modal-tool";
      b.setAttribute("title", tooltip);
      b.textContent = label;
      toolbar.appendChild(b);
      return b;
    }

    var zoomOutBtn = toolButton("−", "Zoom out");
    var pct = document.createElement("span");
    pct.className = "diagram-modal-pct";
    pct.textContent = "100%";
    toolbar.appendChild(pct);
    var zoomInBtn = toolButton("+", "Zoom in (or Ctrl+scroll)");
    var resetBtn = toolButton("Reset", "Reset zoom");

    var closeBtn = document.createElement("button");
    closeBtn.className = "diagram-modal-close";
    closeBtn.setAttribute("title", "Close (Esc)");
    closeBtn.innerHTML = "&times;";
    toolbar.appendChild(closeBtn);

    overlay.appendChild(toolbar);

    // Scrollable viewport: scrollbars provide panning without covering the
    // SVG with an event-eating layer, so links inside diagrams keep working.
    var viewport = document.createElement("div");
    viewport.className = "diagram-modal-viewport";
    viewport.appendChild(content);
    overlay.appendChild(viewport);

    document.body.appendChild(overlay);

    var scale = 1;
    var baseWidth = null;

    function apply() {
      if (baseWidth === null) {
        baseWidth = content.getBoundingClientRect().width || viewport.clientWidth;
      }
      content.style.width = baseWidth * scale + "px";
      content.style.maxWidth = "none";
      content.style.maxHeight = "none";
      pct.textContent = Math.round(scale * 100) + "%";
    }

    function zoom(factor) {
      scale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale * factor));
      apply();
    }

    zoomInBtn.addEventListener("click", function () { zoom(ZOOM_STEP); });
    zoomOutBtn.addEventListener("click", function () { zoom(1 / ZOOM_STEP); });
    resetBtn.addEventListener("click", function () {
      scale = 1;
      content.style.width = "";
      content.style.maxWidth = "";
      content.style.maxHeight = "";
      pct.textContent = "100%";
      viewport.scrollTo(0, 0);
    });

    viewport.addEventListener("wheel", function (ev) {
      if (!ev.ctrlKey) return; // plain wheel scrolls/pans
      ev.preventDefault();
      zoom(ev.deltaY < 0 ? ZOOM_STEP : 1 / ZOOM_STEP);
    }, { passive: false });

    function close() {
      overlay.remove();
      document.removeEventListener("keydown", keyHandler);
    }

    function keyHandler(ev) {
      if (ev.key === "Escape") close();
      else if (ev.key === "+" || ev.key === "=") zoom(ZOOM_STEP);
      else if (ev.key === "-") zoom(1 / ZOOM_STEP);
    }

    closeBtn.addEventListener("click", function (ev) {
      ev.stopPropagation();
      close();
    });

    viewport.addEventListener("click", function (ev) {
      // Only close when clicking the backdrop area, not the diagram itself
      if (ev.target === viewport) close();
    });

    document.addEventListener("keydown", keyHandler);
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".diagram-zoom-btn");
    if (!btn) return;

    e.preventDefault();
    e.stopPropagation();

    var src = btn.getAttribute("data-diagram-src");
    if (src) {
      // <object>-embedded SVG file (PlantUML)
      var obj = document.createElement("object");
      obj.setAttribute("data", src);
      obj.setAttribute("type", "image/svg+xml");
      obj.className = "diagram";
      obj.textContent = btn.getAttribute("data-diagram-title") || "";
      openModal(obj);
      return;
    }

    // Mermaid: re-render the stashed source into the modal.
    // Material renders diagrams into a *closed* shadow DOM, so the rendered
    // SVG cannot be reached or cloned — but the same lazily loaded global
    // mermaid API can render a fresh copy from the original source text.
    var wrap = btn.closest(".mermaid-container");
    if (!wrap || !wrap.mermaidSource || !window.mermaid) return;

    var canvas = document.createElement("div");
    canvas.className = "diagram-modal-mermaid";
    openModal(canvas);
    window.mermaid.render("__diagram_zoom_" + (zoomSeq++), wrap.mermaidSource).then(function (res) {
      canvas.innerHTML = res.svg;
      var svg = canvas.querySelector("svg");
      if (!svg) return;
      // Natural size caps at the svg's own max-width; free it so the
      // modal's width-based zoom drives the size instead.
      var natural = parseFloat(svg.style.maxWidth) || 0;
      svg.style.maxWidth = "none";
      svg.style.width = "100%";
      svg.removeAttribute("height");
      if (natural) canvas.style.width = natural + "px";
    });
  });

  // Stash each Mermaid diagram's source and wrap it before Material's
  // pipeline takes the block: the wrapper keeps the source (as an element
  // property) and hosts the zoom button through the pre -> shadow-host swap.
  var zoomSeq = 0;

  function wrapMermaids() {
    document.querySelectorAll("pre.mermaid").forEach(function (pre) {
      if (pre.closest(".mermaid-container")) return;
      var wrap = document.createElement("div");
      wrap.className = "mermaid-container";
      wrap.mermaidSource = pre.textContent;
      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(pre);
      var btn = document.createElement("button");
      btn.className = "diagram-zoom-btn";
      btn.setAttribute("title", "Enlarge diagram");
      btn.innerHTML = ZOOM_ICON;
      wrap.appendChild(btn);
    });
  }

  wrapMermaids();
  // Fallback in case this script ever loads before the content is parsed
  document.addEventListener("DOMContentLoaded", wrapMermaids);
})();
