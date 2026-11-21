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
