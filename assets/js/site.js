(function () {
  "use strict";

  var STORAGE_KEY = "lonko-public-appearance";

  function resolveTheme(preference) {
    if (preference === "dark" || preference === "light") {
      return preference;
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyTheme(preference) {
    var theme = resolveTheme(preference);
    document.documentElement.setAttribute("data-theme", theme);
  }

  function themeToggleLabel(theme) {
    return theme === "dark" ? "Switch to light theme" : "Switch to dark theme";
  }

  function initTheme() {
    var stored = localStorage.getItem(STORAGE_KEY) || "system";
    applyTheme(stored);

    var toggle = document.getElementById("theme-toggle");
    if (!toggle) return;

    toggle.setAttribute(
      "aria-label",
      themeToggleLabel(document.documentElement.getAttribute("data-theme") || "light")
    );

    toggle.addEventListener("click", function () {
      var current = document.documentElement.getAttribute("data-theme") || "light";
      var next = current === "dark" ? "light" : "dark";
      localStorage.setItem(STORAGE_KEY, next);
      applyTheme(next);
      toggle.setAttribute("aria-label", themeToggleLabel(next));
    });

    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () {
      if ((localStorage.getItem(STORAGE_KEY) || "system") === "system") {
        applyTheme("system");
        toggle.setAttribute(
          "aria-label",
          themeToggleLabel(document.documentElement.getAttribute("data-theme") || "light")
        );
      }
    });
  }

  function initNav() {
    var button = document.querySelector(".nav-toggle");
    var nav = document.querySelector(".site-nav");
    if (!button || !nav) return;

    function setOpen(open) {
      nav.classList.toggle("is-open", open);
      button.setAttribute("aria-expanded", open ? "true" : "false");
      button.setAttribute("aria-label", open ? "Close navigation menu" : "Open navigation menu");
    }

    button.addEventListener("click", function () {
      setOpen(!nav.classList.contains("is-open"));
    });

    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        setOpen(false);
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTheme();
    initNav();
  });
})();
