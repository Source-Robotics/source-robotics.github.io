/* The Develop page's filter: "Works with" one product. hooks/develop.py writes every entry with data-for (the
   products it works with); a button keeps the entries of its product and hides the rest, a group left empty goes
   with its heading, and in the matrix the product's column is marked. ?for=parol6 in the address chooses a product,
   so a product's README can link straight to its own list. Without JavaScript the page is the whole list. */
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
      groups.forEach(function (g) {
        var empty = !g.querySelector(".dev-entry:not([data-dev-off])");
        off(g, empty);
        // the group's lead and heading sit just before it
        var id = "";
        for (var n = g.previousElementSibling; n; n = n.previousElementSibling) {
          off(n, empty);
          if (n.tagName === "H2") { id = n.id; break; }
        }
        var link = id && document.querySelector('.md-nav--secondary a[href$="#' + id + '"]');
        if (link && link.parentElement) link.parentElement.style.display = empty ? "none" : "";
      });
      document.querySelectorAll(".dev-matrix .dev-col").forEach(function (c) {
        c.classList.toggle("dev-col--on", !!key && c.dataset.col === key);
      });
      count.hidden = !key;
      count.textContent = key ? "Showing " + shown + " of " + entries.length + " for " + names[key] + "." : "";

      // the address, and the links between the draft's three styles, carry the choice
      try {
        var url = new URL(window.location.href);
        if (key) url.searchParams.set("for", key); else url.searchParams.delete("for");
        window.history.replaceState(null, "", url);
        document.querySelectorAll(".dev-draft a").forEach(function (a) {
          var u = new URL(a.href);
          if (key) u.searchParams.set("for", key); else u.searchParams.delete("for");
          a.href = u.toString();
        });
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
