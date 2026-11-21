// Forschungsatlas: Bedienhilfen. Alle Inhalte sind auch ohne dieses Skript lesbar.
(function () {
  "use strict";
  var root = document.documentElement;
  var KEY = "atlas-theme";

  // --- Helles und dunkles Design ---------------------------------------------
  function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function isDark() {
    var set = root.getAttribute("data-theme");
    if (set) { return set === "dark"; }
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }
  var button = document.getElementById("theme");
  function label() {
    if (!button) { return; }
    var text = isDark() ? "Helles Design" : "Dunkles Design";
    button.querySelector("span").textContent = text;
    button.setAttribute("aria-pressed", isDark() ? "true" : "false");
  }
  if (button) {
    button.hidden = false;
    label();
    button.addEventListener("click", function () {
      var next = isDark() ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem(KEY, next); } catch (e) { /* ohne Speicher gilt die Wahl bis zum Neuladen */ }
      label();
    });
  }

  // --- Kurzinfo zu Kacheln und Balkenteilen -----------------------------------
  var marks = Array.prototype.slice.call(document.querySelectorAll(".tile[title], .seg[title]"));
  if (marks.length) {
    var tip = document.createElement("div");
    tip.className = "tip";
    tip.setAttribute("role", "tooltip");
    tip.hidden = true;
    document.body.appendChild(tip);
    var show = function (el) {
      tip.textContent = el.getAttribute("data-tip");
      tip.hidden = false;
      var box = el.getBoundingClientRect();
      var top = box.top - tip.offsetHeight - 8;
      if (top < 4) { top = box.bottom + 8; }
      var left = box.left + box.width / 2 - tip.offsetWidth / 2;
      left = Math.max(8, Math.min(left, window.innerWidth - tip.offsetWidth - 8));
      tip.style.top = top + "px";
      tip.style.left = left + "px";
    };
    var hide = function () { tip.hidden = true; };
    marks.forEach(function (el) {
      el.setAttribute("data-tip", el.getAttribute("title"));
      el.removeAttribute("title");
      el.addEventListener("pointerenter", function () { show(el); });
      el.addEventListener("focus", function () { show(el); });
      el.addEventListener("pointerleave", hide);
      el.addEventListener("blur", hide);
    });
    window.addEventListener("scroll", hide, { passive: true });
  }

  // --- Suche und Fachfilter auf der Übersicht --------------------------------
  var box = document.getElementById("filter");
  if (!box) { return; }
  var input = document.getElementById("suche");
  var pills = Array.prototype.slice.call(box.querySelectorAll(".pill"));
  var goals = Array.prototype.slice.call(document.querySelectorAll(".goal"));
  var fields = Array.prototype.slice.call(document.querySelectorAll(".field"));
  var result = document.getElementById("treffer");
  var empty = document.getElementById("leer");
  var field = "";
  box.hidden = false;

  function update() {
    var words = input.value.toLowerCase().split(/\s+/).filter(Boolean);
    var shown = 0;
    goals.forEach(function (goal) {
      var text = goal.getAttribute("data-search");
      var ok = (!field || goal.getAttribute("data-field") === field) &&
               words.every(function (w) { return text.indexOf(w) !== -1; });
      goal.hidden = !ok;
      if (ok) { shown += 1; }
    });
    fields.forEach(function (section) {
      section.hidden = !section.querySelector(".goal:not([hidden])");
    });
    var filtered = field || words.length;
    result.textContent = filtered ? shown + " von " + goals.length + " Zielen" : "";
    empty.hidden = shown !== 0;
  }
  input.addEventListener("input", update);
  pills.forEach(function (pill) {
    pill.addEventListener("click", function () {
      field = pill.getAttribute("data-field");
      pills.forEach(function (p) { p.setAttribute("aria-pressed", p === pill ? "true" : "false"); });
      update();
    });
  });
  var reset = document.getElementById("zuruecksetzen");
  if (reset) {
    reset.addEventListener("click", function () {
      input.value = "";
      pills[0].click();
      input.focus();
    });
  }
})();
