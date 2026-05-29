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

  function cssEscape(value) {
    if (window.CSS && typeof window.CSS.escape === "function") {
      return window.CSS.escape(value);
    }
    return String(value || "").replace(/[^a-zA-Z0-9_-]/g, "\\$&");
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
    return document.querySelector('[data-catalog-item][data-catalog-slug="' + cssEscape(slug) + '"]');
  }

  function findOverviewPanelById(id) {
    if (!id) return null;
    return document.querySelector('[data-catalog-overview-panel="' + cssEscape(id) + '"]');
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

  function carouselForItem(item) {
    return item ? item.closest("[data-catalog-carousel]") : null;
  }

  function catalogSectionForCarousel(carousel) {
    return carousel ? carousel.closest(".panel[id], section[id]") : null;
  }

  function catalogSectionForItem(item) {
    return catalogSectionForCarousel(carouselForItem(item));
  }

  function catalogSectionForOverview(panel) {
    return panel ? panel.closest(".panel[id], section[id]") : null;
  }

  function itemLeftWithinTrack(item, track) {
    if (!item || !track) return 0;
    var itemRect = item.getBoundingClientRect();
    var trackRect = track.getBoundingClientRect();
    return itemRect.left - trackRect.left + track.scrollLeft;
  }

  function scrollTrackToItem(item, instant) {
    if (!item) return;

    var carousel = carouselForItem(item);
    var track = carousel ? carousel.querySelector("[data-catalog-track]") : null;
    if (!track) return;

    var left = itemLeftWithinTrack(item, track);
    track.scrollTo({ left: left, behavior: instant ? "auto" : "smooth" });
    updateCarouselNav(carousel);

    item.classList.add("is-targeted");
    window.setTimeout(function () {
      item.classList.remove("is-targeted");
    }, 1200);
  }

  function repeatHorizontalAlignment(item, instant) {
    if (!item) return;
    scrollTrackToItem(item, instant);
    window.requestAnimationFrame(function () {
      scrollTrackToItem(item, true);
      window.setTimeout(function () { scrollTrackToItem(item, true); }, 120);
      window.setTimeout(function () { scrollTrackToItem(item, true); }, 320);
    });
  }

  function defaultItemForCarousel(carousel) {
    if (!carousel) return null;
    var defaultSlug = carousel.getAttribute("data-catalog-default") || "";
    if (defaultSlug) {
      var defaultItem = carousel.querySelector('[data-catalog-item][data-catalog-slug="' + cssEscape(defaultSlug) + '"]');
      if (defaultItem) return defaultItem;
    }
    return carousel.querySelector("[data-catalog-item]");
  }

  function defaultItemForSectionId(sectionId) {
    if (!sectionId) return null;
    var section = document.getElementById(sectionId);
    var carousel = section ? section.querySelector("[data-catalog-carousel]") : null;
    return defaultItemForCarousel(carousel);
  }

  function catalogTargetForHash(hash) {
    var slug = hash ? hash.replace(/^#/, "") : "";
    if (!slug) return null;

    var item = findCatalogItemBySlug(slug);
    if (item) {
      return { item: item, section: catalogSectionForItem(item), isSectionDefault: false };
    }

    item = defaultItemForSectionId(slug);
    if (item) {
      return { item: item, section: document.getElementById(slug), isSectionDefault: true };
    }

    return null;
  }

  function closeOverviewPanels() {
    document.querySelectorAll("[data-catalog-overview-panel]").forEach(function (panel) {
      panel.hidden = true;
      panel.setAttribute("aria-hidden", "true");
    });
  }

  function openOverviewPanel(panel, instant, updateHash) {
    if (!panel) return;

    closeOverviewPanels();
    panel.hidden = false;
    panel.setAttribute("aria-hidden", "false");

    var section = catalogSectionForOverview(panel);
    if (section) {
      section.scrollIntoView({ behavior: instant ? "auto" : "smooth", block: "center" });
    }

    var id = panel.getAttribute("data-catalog-overview-panel") || "";
    if (updateHash && id) {
      updateHashWithoutJump("#" + id);
    }

    var closeButton = panel.querySelector("[data-catalog-overview-close]");
    if (closeButton) {
      window.setTimeout(function () { closeButton.focus({ preventScroll: true }); }, 50);
    }
  }

  function closeOverviewAndReturn(panel) {
    var section = catalogSectionForOverview(panel);
    closeOverviewPanels();

    if (section && section.id) {
      var defaultItem = defaultItemForSectionId(section.id);
      if (defaultItem) {
        activateCatalogTarget({ item: defaultItem, section: section, isSectionDefault: true }, false, true);
      }
      updateHashWithoutJump("#" + section.id);
    }
  }

  function activateCatalogTarget(target, instant, includeSectionScroll) {
    if (!target || !target.item) return;

    closeOverviewPanels();

    if (includeSectionScroll && target.section) {
      target.section.scrollIntoView({ behavior: instant ? "auto" : "smooth", block: "center" });
    }

    repeatHorizontalAlignment(target.item, instant);
  }

  function updateHashWithoutJump(hash) {
    if (!hash || hash === "#") return;
    if (window.history && window.history.pushState) {
      window.history.pushState(null, "", hash);
      return;
    }
    window.location.hash = hash;
  }

  function handleHash(instant) {
    var slug = window.location.hash ? window.location.hash.slice(1) : "";
    if (!slug) return;

    var overviewPanel = findOverviewPanelById(slug);
    if (overviewPanel) {
      openOverviewPanel(overviewPanel, instant, false);
      return;
    }

    var target = catalogTargetForHash(slug);
    if (!target) {
      closeOverviewPanels();
      return;
    }

    activateCatalogTarget(target, instant, true);
  }

  function hashFromHref(href) {
    if (!href) return "";
    var hashIndex = href.indexOf("#");
    if (hashIndex < 0) return "";
    return href.slice(hashIndex + 1);
  }

  function samePageHashFromLink(link) {
    var raw = link.getAttribute("href") || "";
    if (!raw || raw === "#") return "";

    try {
      var url = new URL(raw, window.location.href);
      if (url.origin !== window.location.origin) return "";
      var currentPath = window.location.pathname.replace(/\/index\.html$/, "/");
      var linkPath = url.pathname.replace(/\/index\.html$/, "/");
      if (currentPath !== linkPath) return "";
      return url.hash ? url.hash.slice(1) : "";
    } catch (error) {
      return raw.charAt(0) === "#" ? raw.slice(1) : hashFromHref(raw);
    }
  }

  function wireCatalogLinks() {
    document.addEventListener("click", function (event) {
      var link = event.target.closest ? event.target.closest("a[href]") : null;
      if (!link) return;

      var overviewId = link.getAttribute("data-catalog-overview-open") || "";
      if (overviewId) {
        var overviewPanel = findOverviewPanelById(overviewId);
        if (overviewPanel) {
          event.preventDefault();
          openOverviewPanel(overviewPanel, false, true);
        }
        return;
      }

      var explicitTarget = link.getAttribute("data-catalog-target") || "";
      var hrefHash = samePageHashFromLink(link);
      var slug = explicitTarget || hrefHash;
      if (!slug) return;

      var target = catalogTargetForHash(slug);

      if (explicitTarget && !target) {
        if (!hrefHash) return;
        event.preventDefault();
        link.setAttribute("aria-disabled", "true");
        return;
      }

      if (target && target.item) {
        event.preventDefault();

        var itemCarousel = carouselForItem(target.item);
        var linkCarousel = link.closest("[data-catalog-carousel]");
        var shouldScrollSection = itemCarousel !== linkCarousel;
        var hashToSet = explicitTarget || hrefHash;

        activateCatalogTarget(target, false, shouldScrollSection);
        updateHashWithoutJump("#" + hashToSet);
      }
    }, true);

    document.addEventListener("click", function (event) {
      var closeButton = event.target.closest ? event.target.closest("[data-catalog-overview-close]") : null;
      if (!closeButton) return;
      event.preventDefault();
      closeOverviewAndReturn(closeButton.closest("[data-catalog-overview-panel]"));
    }, true);

    document.addEventListener("keydown", function (event) {
      if (event.key !== "Escape") return;
      var openPanel = document.querySelector("[data-catalog-overview-panel]:not([hidden])");
      if (openPanel) {
        event.preventDefault();
        closeOverviewAndReturn(openPanel);
      }
    });
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
