(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.add("has-visual-polish");

  function formatBytes(bytes) {
    if (!Number.isFinite(bytes) || bytes <= 0) return "Not exposed";
    if (bytes < 1024) return String(Math.round(bytes)) + " B";
    if (bytes < 1024 * 1024) return String(Math.round(bytes / 1024)) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  }

  function observedSize(entry) {
    return entry.transferSize || entry.encodedBodySize || 0;
  }

  function updatePerformanceProof() {
    var proof = document.querySelector("[data-performance-proof]");
    if (!proof || !window.performance || typeof window.performance.getEntriesByType !== "function") return;

    var resources = window.performance.getEntriesByType("resource");
    var total = resources.reduce(function (sum, entry) { return sum + observedSize(entry); }, 0);
    var scripts = resources.filter(function (entry) { return entry.initiatorType === "script"; });
    var scriptTotal = scripts.reduce(function (sum, entry) { return sum + observedSize(entry); }, 0);

    var transfer = proof.querySelector("[data-performance-transfer]");
    var javascript = proof.querySelector("[data-performance-js]");
    var resourceCount = proof.querySelector("[data-performance-resources]");

    if (transfer) transfer.textContent = formatBytes(total);
    if (javascript) javascript.textContent = formatBytes(scriptTotal);
    if (resourceCount) resourceCount.textContent = String(resources.length);
  }

  function updateHeader() {
    var header = document.querySelector(".site-header");
    if (!header) return;
    header.classList.toggle("is-scrolled", window.scrollY > 16);
  }

  function enableReveal() {
    var elements = Array.prototype.slice.call(document.querySelectorAll("[data-reveal]"));
    if (!elements.length) return;

    if (!("IntersectionObserver" in window)) {
      elements.forEach(function (element) { element.classList.add("is-visible"); });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12 });

    elements.forEach(function (element) { observer.observe(element); });
  }

  function enableKineticWord() {
    var word = document.querySelector("[data-kinetic-word]");
    if (!word || !window.setInterval) return;

    var words = ["light", "clear", "responsive", "maintainable"];
    var index = 0;

    window.setInterval(function () {
      word.classList.add("is-changing");
      window.setTimeout(function () {
        index = (index + 1) % words.length;
        word.textContent = words[index];
        word.classList.remove("is-changing");
      }, 170);
    }, 2600);
  }

  window.addEventListener("scroll", updateHeader, { passive: true });
  window.addEventListener("load", function () {
    updateHeader();
    updatePerformanceProof();
  });

  updateHeader();
  enableReveal();
  enableKineticWord();
}());
