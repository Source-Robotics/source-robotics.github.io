/* The Develop page's filter: "Works with" one product. hooks/develop.py writes every entry with data-for (the
   products it works with); a button keeps the entries of its product and hides the rest, and a group left empty
   goes whole. A button clicked again shows everything. ?for=parol6 in the address chooses a product, so a product's
   README can link straight to its own list. Without JavaScript the page is the whole list. */
(function () {
  function setup() {
    var top = document.querySelector(".dev-top");
    if (!top || top.dataset.ready) return;
    top.dataset.ready = "1";
    var bar = top.querySelector(".dev-filter"), count = top.querySelector(".dev-count");
    var buttons = Array.prototype.slice.call(bar.querySelectorAll(".dev-filter__btn"));
    var entries = Array.prototype.slice.call(document.querySelectorAll(".dev-entry"));
    var groups = Array.prototype.slice.call(document.querySelectorAll(".dev-group"));
    var names = {};
    buttons.forEach(function (b) { names[b.dataset.for] = b.textContent; });

    function off(el, yes) { if (yes) el.setAttribute("data-dev-off", ""); else el.removeAttribute("data-dev-off"); }

    function apply(key) {
      if (!(key in names)) key = "";
      buttons.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.for === key ? "true" : "false"); });
      var shown = 0;
      entries.forEach(function (en) {
        var on = !key || en.dataset.for.split(" ").indexOf(key) >= 0;
        off(en, !on);
        if (on) shown += 1;
      });
      groups.forEach(function (g) { off(g, !g.querySelector(".dev-entry:not([data-dev-off])")); });
      count.hidden = !key;
      count.textContent = key ? "Showing " + shown + " of " + entries.length + " for " + names[key] + "." : "";
      try {                                              // the address carries the choice
        var url = new URL(window.location.href);
        if (key) url.searchParams.set("for", key); else url.searchParams.delete("for");
        window.history.replaceState(null, "", url);
      } catch (e) { /* an old browser: the filter still works */ }
    }

    buttons.forEach(function (b) {
      b.addEventListener("click", function () {
        apply(b.getAttribute("aria-pressed") === "true" ? "" : b.dataset.for);
      });
    });
    bar.hidden = false;
    var asked = "";
    try { asked = new URLSearchParams(window.location.search).get("for") || ""; } catch (e) { asked = ""; }
    apply(asked);
  }

  if (window.document$ && window.document$.subscribe) { window.document$.subscribe(setup); }
  else if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", setup); }
  else { setup(); }
})();
