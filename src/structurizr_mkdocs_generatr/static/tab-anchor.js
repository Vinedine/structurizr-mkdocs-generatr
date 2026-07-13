// Make anchor navigation work for headings inside pymdownx tabbed content.
// The right-hand TOC lists headings from every tab, but a heading in an
// inactive tab is display:none — clicking its TOC link did nothing. This
// activates the tab containing the target before the browser scrolls to it.
document.addEventListener("DOMContentLoaded", function () {
  function activateTabsFor(el) {
    var block = el.closest(".tabbed-block");
    var activated = false;
    while (block) {
      var set = block.closest(".tabbed-set");
      if (!set) break;
      var blocks = Array.prototype.filter.call(
        block.parentElement.children,
        function (c) { return c.classList.contains("tabbed-block"); }
      );
      var index = blocks.indexOf(block);
      var inputs = Array.prototype.filter.call(set.children, function (c) {
        return c.tagName === "INPUT";
      });
      if (inputs[index] && !inputs[index].checked) {
        inputs[index].checked = true;
        activated = true;
      }
      // Support nested tab sets
      block = set.parentElement ? set.parentElement.closest(".tabbed-block") : null;
    }
    return activated;
  }

  function targetFromHash(hash) {
    if (!hash || hash === "#") return null;
    var id;
    try {
      id = decodeURIComponent(hash.slice(1));
    } catch (err) {
      id = hash.slice(1);
    }
    return document.getElementById(id);
  }

  document.body.addEventListener("click", function (e) {
    var link = e.target.closest('a[href*="#"]');
    if (!link) return;
    var url;
    try {
      url = new URL(link.getAttribute("href"), window.location.href);
    } catch (err) {
      return;
    }
    if (url.pathname !== window.location.pathname || !url.hash) return;
    var target = targetFromHash(url.hash);
    if (!target) return;
    // Reveal the tab first; the default anchor navigation then scrolls to it.
    activateTabsFor(target);
  });

  function revealHashTarget() {
    var target = targetFromHash(window.location.hash);
    if (target && activateTabsFor(target)) {
      target.scrollIntoView();
    }
  }

  window.addEventListener("hashchange", revealHashTarget);
  // Deep link into a hidden tab on initial page load
  revealHashTarget();
});
