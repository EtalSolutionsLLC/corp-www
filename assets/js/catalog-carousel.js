(function () {
  "use strict";

  if (window.history && "scrollRestoration" in window.history) {
    window.history.scrollRestoration = "manual";
  }

  function htmlEscape(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function catalogItems(carousel) {
    return Array.prototype.slice.call(carousel.querySelectorAll("[data-catalog-item]"));
  }

  function itemSlug(item) {
    return item ? item.getAttribute("data-catalog-slug") || "" : "";
  }

  function itemTitle(item) {
    if (!item) return "";
    var titleElement = item.querySelector("h2, h3");
    return item.getAttribute("data-catalog-title") || (titleElement ? titleElement.textContent : "");
  }

  function findCatalogItemBySlug(slug) {
    if (!slug) return null;
    try {
      return document.querySelector('[data-catalog-item][data-catalog-slug="' + CSS.escape(slug) + '"]');
    } catch (error) {
      return Array.prototype.slice.call(document.querySelectorAll("[data-catalog-item]")).find(function (item) {
        return itemSlug(item) === slug;
      }) || null;
    }
  }

  function linkHtml(label, item, direction) {
    var href = "#" + itemSlug(item);
    var title = itemTitle(item);

    var slug = itemSlug(item);
    if (direction === "newer") {
      return '<a class="catalog-direction-link" data-catalog-target="' + htmlEscape(slug) + '" href="' + htmlEscape(href) + '"><span>←</span> ' + htmlEscape(label) + ': <strong>' + htmlEscape(title) + '</strong></a>';
    }

    return '<a class="catalog-direction-link" data-catalog-target="' + htmlEscape(slug) + '" href="' + htmlEscape(href) + '">' + htmlEscape(label) + ': <strong>' + htmlEscape(title) + '</strong> <span>→</span></a>';
  }

  function activeIndexForTrack(track, items) {
    if (!track || !items.length) return 0;

    var left = track.scrollLeft;
    var bestIndex = 0;
    var bestDistance = Infinity;

    items.forEach(function (item, index) {
      var distance = Math.abs(item.offsetLeft - left);
      if (distance < bestDistance) {
        bestDistance = distance;
        bestIndex = index;
      }
    });

    return bestIndex;
  }

  function updateCarouselNav(carousel) {
    if (!carousel) return;

    var nav = carousel.querySelector("[data-catalog-nav]");
    var track = carousel.querySelector("[data-catalog-track]");
    var newerSlot = carousel.querySelector("[data-catalog-newer-slot]");
    var previousSlot = carousel.querySelector("[data-catalog-previous-slot]");
    var items = catalogItems(carousel);

    if (!nav || !track || !newerSlot || !previousSlot || !items.length) return;

    var index = activeIndexForTrack(track, items);
    var newer = items[index - 1] || null;
    var previous = items[index + 1] || null;
    var newerLabel = nav.getAttribute("data-newer-label") || "Newer item";
    var previousLabel = nav.getAttribute("data-previous-label") || "Previous item";
    var endLabel = nav.getAttribute("data-end-label") || "End of items";

    newerSlot.innerHTML = newer ? linkHtml(newerLabel, newer, "newer") : '<span class="catalog-direction-empty"></span>';
    previousSlot.innerHTML = previous ? linkHtml(previousLabel, previous, "previous") : '<span class="catalog-direction-empty">' + htmlEscape(endLabel) + '</span>';
  }

  function preserveWindowScroll(callback) {
    var x = window.scrollX;
    var y = window.scrollY;
    callback();
    window.scrollTo(x, y);
    window.requestAnimationFrame(function () {
      window.scrollTo(x, y);
      window.requestAnimationFrame(function () {
        window.scrollTo(x, y);
      });
    });
  }

  function scrollToItem(item, instant) {
    if (!item) return;

    var carousel = item.closest("[data-catalog-carousel]");
    var track = carousel ? carousel.querySelector("[data-catalog-track]") : null;
    if (!track) return;

    preserveWindowScroll(function () {
      track.scrollTo({ left: item.offsetLeft, behavior: instant ? "auto" : "smooth" });
      updateCarouselNav(carousel);
    });

    item.classList.add("is-targeted");
    window.setTimeout(function () {
      item.classList.remove("is-targeted");
    }, 1200);
  }

  function handleHash(instant) {
    var slug = window.location.hash ? window.location.hash.slice(1) : "";
    var item = findCatalogItemBySlug(slug);
    if (!item) return;

    window.setTimeout(function () {
      scrollToItem(item, instant);
    }, instant ? 0 : 40);
  }

  function updateHashWithoutJump(hash) {
    if (!hash || hash === "#") return;
    if (window.history && window.history.pushState) {
      window.history.pushState(null, "", hash);
      return;
    }
  }

  function wireCatalogLinks() {
    document.addEventListener("click", function (event) {
      var link = event.target.closest ? event.target.closest('a[href^="#"]') : null;
      if (!link) return;

      var href = link.getAttribute("href");
      var explicitTarget = link.getAttribute("data-catalog-target") || "";
      var slug = explicitTarget || (href ? href.slice(1) : "");
      var item = findCatalogItemBySlug(slug);

      if (explicitTarget && !item) {
        event.preventDefault();
        link.setAttribute("aria-disabled", "true");
        return;
      }

      if (item) {
        event.preventDefault();
        scrollToItem(item, false);
        updateHashWithoutJump("#" + slug);
      }
    }, true);
  }

  function wireCarousels() {
    document.querySelectorAll("[data-catalog-carousel]").forEach(function (carousel) {
      var track = carousel.querySelector("[data-catalog-track]");
      var updateTimer = null;
      if (!track) return;

      track.addEventListener("scroll", function () {
        if (updateTimer) window.clearTimeout(updateTimer);
        updateTimer = window.setTimeout(function () {
          updateCarouselNav(carousel);
        }, 80);
      }, { passive: true });

      updateCarouselNav(carousel);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    wireCarousels();
    wireCatalogLinks();
    handleHash(true);
    window.addEventListener("hashchange", function () {
      handleHash(false);
    });
  });
}());
