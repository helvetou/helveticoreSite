/* Helveticore — lightweight JavaScript (progressive enhancement).
   Nothing is blocking: the site remains fully usable without JS. */
(function () {
  "use strict";

  /* 1. Mobile navigation (toggle + close on link click) */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* 2. Light / dark theme — follows the system by default, persists the choice */
  var themeToggle = document.querySelector(".theme-toggle");
  var STORAGE_KEY = "helveticore-theme";

  function applyTheme(theme) {
    var root = document.documentElement;
    if (theme === "light" || theme === "dark") {
      root.setAttribute("data-theme", theme);
    } else {
      root.removeAttribute("data-theme");
    }
  }

  if (themeToggle) {
    try {
      var saved = localStorage.getItem(STORAGE_KEY);
      if (saved === "light" || saved === "dark") {
        applyTheme(saved);
      }
    } catch (err) {
      /* storage unavailable: keep the system theme */
    }

    themeToggle.addEventListener("click", function () {
      var current = document.documentElement.getAttribute("data-theme");
      var next = current === "dark" ? "light" : "dark";
      applyTheme(next);
      try {
        localStorage.setItem(STORAGE_KEY, next);
      } catch (err) {
        /* ignore */
      }
    });
  }

  /* 3. Footer year */
  var year = document.getElementById("year");
  if (year) {
    year.textContent = String(new Date().getFullYear());
  }
})();
