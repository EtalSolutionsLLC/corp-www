/* Portmason Collections: publication profile with browser-time selection. */
(function () {
  "use strict";

  var api = window.PortmasonCollections;
  if (!api) throw new Error("Portmason Collections core must load before the publication profile");

  function copyChildren(source, target) {
    target.replaceChildren();
    Array.prototype.forEach.call(source.childNodes, function (node) {
      target.appendChild(node.cloneNode(true));
    });
  }

  function initializePublication(root, runtimeContext) {
    var modal = root.querySelector("[data-collection-modal]");
    var closeButton = root.querySelector("[data-collection-modal-close]");
    var modalTitle = root.querySelector("[data-collection-modal-title]");
    var modalMeta = root.querySelector("[data-collection-modal-meta]");
    var modalArticle = root.querySelector("[data-collection-modal-body]");
    var featured = root.querySelector("[data-collection-featured]");
    var supporting = root.querySelector("[data-collection-supporting]");
    var templates = Array.prototype.slice.call(root.querySelectorAll("[data-collection-article-template]"));

    function findTemplate(itemId) {
      return templates.find(function (template) {
        return Number(template.getAttribute("data-collection-item-id")) === Number(itemId);
      }) || null;
    }

    function source(template, name) {
      return template && template.content.querySelector("[data-collection-card-" + name + "]");
    }

    function applyIdentity(element, item) {
      element.setAttribute("data-collection-item", "");
      element.setAttribute("data-collection-item-id", String(item.id));
      element.setAttribute("data-collection-slug", String(item.slug || ""));
      if (item.slot != null) element.setAttribute("data-collection-slot", String(item.slot));
      else element.removeAttribute("data-collection-slot");
    }

    function populateFeatured(item) {
      var template = findTemplate(item.id);
      if (!featured || !template) return;
      applyIdentity(featured, item);
      var category = featured.querySelector("[data-collection-featured-category]");
      var title = featured.querySelector("[data-collection-featured-title]");
      var excerpt = featured.querySelector("[data-collection-featured-excerpt]");
      var link = featured.querySelector("[data-collection-featured-link]");
      if (category) category.textContent = item.category || "";
      if (title) copyChildren(source(template, "title"), title);
      if (excerpt) copyChildren(source(template, "excerpt"), excerpt);
      if (link) {
        link.href = item.url || "#";
        link.setAttribute("data-collection-open-item", String(item.id));
      }
      featured.hidden = false;
    }

    function supportingCard(item) {
      var template = findTemplate(item.id);
      if (!template) return null;
      var article = document.createElement("article");
      article.className = "thread-post-card";
      article.setAttribute("data-post-category", item.category || "");
      applyIdentity(article, item);

      var meta = document.createElement("div");
      meta.className = "thread-post-meta";
      var category = document.createElement("span");
      var status = document.createElement("span");
      category.textContent = item.category || "";
      status.textContent = item.status || "";
      meta.append(category, status);

      var title = document.createElement("h3");
      var excerpt = document.createElement("p");
      copyChildren(source(template, "title"), title);
      copyChildren(source(template, "excerpt"), excerpt);

      var link = document.createElement("a");
      link.className = "thread-post-link";
      link.href = item.url || "#";
      link.textContent = root.getAttribute("data-collection-open-item-label") || "Read article →";
      link.setAttribute("data-collection-open-item", String(item.id));
      article.append(meta, title, excerpt, link);
      return article;
    }

    function renderSelection(items) {
      if (!items.length) throw new Error("Portmason Collections: publication selection is empty");
      populateFeatured(items[0]);
      if (supporting) {
        supporting.replaceChildren();
        items.slice(1).forEach(function (item) {
          var card = supportingCard(item);
          if (card) supporting.appendChild(card);
        });
      }
    }

    function openItem(itemId) {
      if (!modal || !modalTitle || !modalMeta || !modalArticle) return false;
      var template = findTemplate(itemId);
      if (!template || !template.content) return false;
      var title = template.content.querySelector("[data-collection-article-title]");
      var meta = template.content.querySelector("[data-collection-article-meta]");
      var article = template.content.querySelector("[data-collection-article-body]");
      if (!title || !meta || !article) return false;
      copyChildren(title, modalTitle);
      modalMeta.textContent = meta.textContent;
      copyChildren(article, modalArticle);
      if (typeof modal.showModal === "function") modal.showModal();
      else modal.setAttribute("open", "");
      return true;
    }

    function closeItem() {
      if (!modal) return;
      if (typeof modal.close === "function") modal.close();
      else modal.removeAttribute("open");
      try {
        var url = new URL(window.location.href);
        if (url.searchParams.has("release")) {
          url.searchParams.delete("release");
          window.history.replaceState(window.history.state, "", url.pathname + url.search + url.hash);
        }
      } catch (error) {
        // Closing remains functional when URL parsing is unavailable.
      }
    }

    root.addEventListener("click", function (event) {
      var trigger = event.target.closest("[data-collection-open-item]");
      if (trigger) {
        if (openItem(Number(trigger.getAttribute("data-collection-open-item")))) event.preventDefault();
        return;
      }
      if (event.target === modal) closeItem();
    });
    if (closeButton) closeButton.addEventListener("click", closeItem);

    return runtimeContext.load().then(function (context) {
      renderSelection(context.selectedItems || []);
      try {
        var requestedRelease = new URL(window.location.href).searchParams.get("release") || "";
        var match = requestedRelease.match(/^nr-(\d+)$/i);
        if (runtimeContext.id === "newsroom" && match) openItem(Number(match[1]));
      } catch (error) {
        // The newsroom still works through its in-page controls.
      }
    });
  }

  api.registerProfile("publication", { initialize: initializePublication });
}());
