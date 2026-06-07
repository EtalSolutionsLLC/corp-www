(function () {
  "use strict";

  var root = document.documentElement;
  var reducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  root.classList.add("site-enhanced");

  function revealContent() {
    var elements = Array.prototype.slice.call(document.querySelectorAll("[data-reveal]"));
    if (!elements.length) return;

    if (reducedMotion || !("IntersectionObserver" in window)) {
      elements.forEach(function (element) { element.classList.add("is-visible"); });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -10%", threshold: 0.08 });

    elements.forEach(function (element) { observer.observe(element); });
  }

  function updateHeader() {
    var header = document.querySelector(".site-header");
    if (!header) return;

    function sync() {
      header.classList.toggle("is-scrolled", window.scrollY > 24);
    }

    sync();
    window.addEventListener("scroll", sync, { passive: true });
  }

  function updateActiveNavigation() {
    if (!("IntersectionObserver" in window)) return;
    var links = Array.prototype.slice.call(document.querySelectorAll('.nav a[href^="/#"], .nav a[href^="#"]'));
    var sections = links.map(function (link) {
      var hash = link.getAttribute("href").replace(/^\//, "");
      return document.querySelector(hash);
    }).filter(Boolean);
    if (!sections.length) return;

    var byId = {};
    links.forEach(function (link) {
      var id = link.getAttribute("href").replace(/^\/#?/, "").replace(/^#/, "");
      byId[id] = link;
    });

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        links.forEach(function (link) { link.removeAttribute("aria-current"); });
        if (byId[entry.target.id]) byId[entry.target.id].setAttribute("aria-current", "page");
      });
    }, { rootMargin: "-30% 0px -60%", threshold: 0.01 });

    sections.forEach(function (section) { observer.observe(section); });
  }

  function formatBytes(bytes) {
    if (!Number.isFinite(bytes) || bytes <= 0) return "Limited";
    if (bytes < 1024) return Math.round(bytes) + " B";
    if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  }

  function measuredSize(entry) {
    return Number(entry.transferSize || entry.encodedBodySize || 0);
  }

  function updatePerformanceProof() {
    var proof = document.querySelector("[data-performance-proof]");
    if (!proof || !window.performance || typeof window.performance.getEntriesByType !== "function") return;

    var resources = window.performance.getEntriesByType("resource");
    var navigations = window.performance.getEntriesByType("navigation");
    var entries = navigations.concat(resources);
    var total = entries.reduce(function (sum, entry) { return sum + measuredSize(entry); }, 0);
    var javascript = resources.filter(function (entry) {
      return entry.initiatorType === "script" || /\.js(?:\?|$)/i.test(entry.name || "");
    }).reduce(function (sum, entry) { return sum + measuredSize(entry); }, 0);

    var transfer = proof.querySelector('[data-performance-value="transfer"]');
    var scripts = proof.querySelector('[data-performance-value="javascript"]');
    var count = proof.querySelector('[data-performance-value="resources"]');
    var note = proof.querySelector("[data-performance-note]");

    if (transfer) transfer.textContent = formatBytes(total);
    if (scripts) scripts.textContent = formatBytes(javascript);
    if (count) count.textContent = String(entries.length);
    if (note) note.textContent = "Observed live in this browser. Some third-party transfer sizes may be hidden by browser privacy rules.";
  }

  revealContent();
  updateHeader();
  updateActiveNavigation();

  if (document.readyState === "complete") {
    window.setTimeout(updatePerformanceProof, 250);
  } else {
    window.addEventListener("load", function () { window.setTimeout(updatePerformanceProof, 250); }, { once: true });
  }
})();
