(function () {
  "use strict";

  var statusEl = document.querySelector(".chronicles-filter-status");
  var pills = Array.prototype.slice.call(document.querySelectorAll("[data-topic-filter]"));
  var cards = Array.prototype.slice.call(document.querySelectorAll("[data-filterable-cards] .chronicles-card"));
  var searchInput = document.querySelector(".chronicles-search-input");
  var activeTopic = "all";
  var indexCache = null;

  function announce(msg) {
    if (statusEl) statusEl.textContent = msg || "";
  }

  function cardMatches(card, topic, q) {
    var t = (card.getAttribute("data-topic") || "").toLowerCase();
    if (topic && topic !== "all" && t !== topic.toLowerCase()) return false;
    if (!q) return true;
    var hay = [
      card.getAttribute("data-title") || "",
      card.getAttribute("data-deck") || "",
      card.getAttribute("data-tags") || "",
      t
    ].join(" ").toLowerCase();
    return hay.indexOf(q) !== -1;
  }

  function applyFilters() {
    var q = (searchInput && searchInput.value ? searchInput.value : "").trim().toLowerCase();
    var shown = 0;
    cards.forEach(function (card) {
      var ok = cardMatches(card, activeTopic, q);
      card.hidden = !ok;
      if (ok) shown += 1;
    });
    if (!cards.length) return;
    if (shown === 0) {
      announce("No stories match your filters. Try another topic or clear search.");
    } else {
      announce(shown + " stor" + (shown === 1 ? "y" : "ies") + " shown.");
    }
  }

  pills.forEach(function (btn) {
    btn.addEventListener("click", function () {
      activeTopic = btn.getAttribute("data-topic-filter") || "all";
      pills.forEach(function (b) {
        b.setAttribute("aria-pressed", b === btn ? "true" : "false");
      });
      applyFilters();
    });
  });

  if (searchInput && cards.length) {
    searchInput.addEventListener("input", applyFilters);
  }

  /* —— Search results page —— */
  var resultsRoot = document.querySelector("[data-search-results]");
  function indexUrl() {
    var scripts = document.getElementsByTagName("script");
    for (var i = 0; i < scripts.length; i++) {
      var src = scripts[i].src || "";
      if (src.indexOf("chronicles.js") !== -1) {
        return src.replace(/chronicles\.js(?:\?.*)?$/, "search-index.json");
      }
    }
    return "../assets/search-index.json";
  }

  function scoreEntry(entry, tokens) {
    var title = (entry.title || "").toLowerCase();
    var deck = (entry.deck || "").toLowerCase();
    var topic = (entry.topic || "").toLowerCase();
    var tags = (entry.tags || []).join(" ").toLowerCase();
    var body = (entry.body || entry.excerpt || "").toLowerCase();
    var score = 0;
    tokens.forEach(function (tok) {
      if (!tok) return;
      if (title === tok) score += 50;
      if (title.indexOf(tok) !== -1) score += 20;
      if (topic.indexOf(tok) !== -1) score += 12;
      if (tags.indexOf(tok) !== -1) score += 10;
      if (deck.indexOf(tok) !== -1) score += 8;
      if (body.indexOf(tok) !== -1) score += 2;
    });
    return score;
  }

  function renderResults(entries, q) {
    if (!resultsRoot) return;
    resultsRoot.innerHTML = "";
    if (!q) {
      announce("Enter a search to find stories.");
      return;
    }
    var tokens = q.toLowerCase().split(/\s+/).filter(Boolean);
    var ranked = entries
      .map(function (e) { return { e: e, s: scoreEntry(e, tokens) }; })
      .filter(function (x) { return x.s > 0; })
      .sort(function (a, b) { return b.s - a.s; });
    if (!ranked.length) {
      announce("No results for “" + q + "”.");
      resultsRoot.innerHTML = '<p class="chronicles-empty">No matching stories. Try a broader topic or different wording.</p>';
      return;
    }
    announce(ranked.length + " result" + (ranked.length === 1 ? "" : "s") + " for “" + q + "”.");
    ranked.forEach(function (row) {
      var e = row.e;
      var a = document.createElement("article");
      a.className = "chronicles-card story-compact";
      a.innerHTML =
        '<a class="chronicles-card-link" href="' + (e.url || ("../" + e.slug + "/")) + '">' +
        '<div class="chronicles-card-body">' +
        '<p class="chronicles-card-meta">' + (e.content_type || "") + " · " + (e.topic || "") + " · " + (e.datePublished || "") + "</p>" +
        "<h3 class=\"chronicles-card-title\">" + escapeHtml(e.title || "") + "</h3>" +
        "<p class=\"chronicles-card-deck\">" + escapeHtml(e.deck || "") + "</p>" +
        "</div></a>";
      resultsRoot.appendChild(a);
    });
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function loadIndex(cb) {
    if (indexCache) return cb(indexCache);
    var req = new XMLHttpRequest();
    req.open("GET", indexUrl(), true);
    req.onload = function () {
      try {
        indexCache = JSON.parse(req.responseText);
      } catch (err) {
        indexCache = [];
      }
      cb(indexCache);
    };
    req.onerror = function () { cb([]); };
    req.send();
  }

  if (resultsRoot) {
    var params = new URLSearchParams(window.location.search);
    var q = params.get("q") || "";
    if (searchInput) searchInput.value = q;
    loadIndex(function (data) { renderResults(data, q); });
    var form = document.querySelector(".chronicles-search");
    if (form) {
      form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        var next = (searchInput && searchInput.value) || "";
        var url = new URL(window.location.href);
        if (next) url.searchParams.set("q", next);
        else url.searchParams.delete("q");
        history.replaceState(null, "", url.toString());
        loadIndex(function (data) { renderResults(data, next.trim()); });
      });
    }
  }

  /* —— Share controls ——
     Keep click handlers minimal. Event Timing on this long article showed
     presentation delay (next paint), not handler cost, dominates INP — so
     avoid any synchronous DOM writes in the click turn (incl. aria-live status). */
  function afterNextPaint(fn) {
    if (typeof requestAnimationFrame !== "function") {
      setTimeout(fn, 0);
      return;
    }
    requestAnimationFrame(function () {
      requestAnimationFrame(fn);
    });
  }

  document.querySelectorAll(".chronicles-share-controls").forEach(function (root) {
    var url = root.getAttribute("data-share-url") || window.location.href;
    var title = root.getAttribute("data-share-title") || document.title;
    var status = root.parentElement && root.parentElement.querySelector(".chronicles-share-status");
    function setStatus(msg) {
      if (!status) return;
      afterNextPaint(function () {
        status.textContent = msg || "";
      });
    }

    var nativeBtn = root.querySelector("[data-share-native]");
    if (nativeBtn) {
      if (!navigator.share) {
        nativeBtn.hidden = true;
      } else {
        nativeBtn.addEventListener("click", function () {
          // Invoke share as the only sync work (preserves user activation).
          navigator.share({ title: title, url: url }).catch(function () {});
        });
      }
    }
    var copyBtn = root.querySelector("[data-share-copy]");
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(url).then(function () {
            setStatus("Link copied.");
          }).catch(function () {
            setStatus("Could not copy link.");
          });
        } else {
          setStatus("Copy not available in this browser.");
        }
      });
    }
  });
})();
