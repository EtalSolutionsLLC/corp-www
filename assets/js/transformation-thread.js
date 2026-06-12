(function () {
  "use strict";

  var root = document.querySelector("[data-thread-blog]");
  if (!root || typeof window.fetch !== "function") return;

  var source = root.getAttribute("data-thread-source") || "/content/transformation-thread-posts.json";
  var modal = root.querySelector("[data-thread-article-modal]");
  var closeButton = root.querySelector("[data-thread-article-close]");
  var title = root.querySelector("[data-thread-article-title]");
  var meta = root.querySelector("[data-thread-article-meta]");
  var article = root.querySelector("[data-thread-article-body]");
  var postsPromise = null;

  function loadPosts() {
    if (postsPromise) return postsPromise;
    postsPromise = window.fetch(source, { cache: "no-store" })
      .then(function (response) {
        if (!response.ok) throw new Error("Article library unavailable");
        return response.json();
      })
      .then(function (data) { return data.posts || []; });
    return postsPromise;
  }

  function loadText(ref) {
    if (!ref || !/\.md(?:$|\?)/.test(ref)) return Promise.reject(new Error("Markdown article reference missing"));
    return window.fetch(ref, { cache: "no-store" }).then(function (response) {
      if (!response.ok) throw new Error("Markdown article unavailable");
      return response.text();
    });
  }

  function safeHref(value) {
    var href = String(value || "").trim();
    return /^(https?:|mailto:)/i.test(href) ? href : "";
  }

  function appendInlineMarkdown(container, value) {
    var sourceText = String(value || "");
    var token = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]+\]\([^)]+\))/g;
    var cursor = 0;
    var match;

    function appendText(text) {
      if (text) container.appendChild(document.createTextNode(text));
    }

    while ((match = token.exec(sourceText))) {
      appendText(sourceText.slice(cursor, match.index));
      var raw = match[0];
      var element;

      if (raw.charAt(0) === "`") {
        element = document.createElement("code");
        element.textContent = raw.slice(1, -1);
      } else if (raw.slice(0, 2) === "**") {
        element = document.createElement("strong");
        element.textContent = raw.slice(2, -2);
      } else if (raw.charAt(0) === "*") {
        element = document.createElement("em");
        element.textContent = raw.slice(1, -1);
      } else {
        var link = raw.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
        var href = link && safeHref(link[2]);
        if (href) {
          element = document.createElement("a");
          element.href = href;
          element.textContent = link[1];
        } else {
          element = document.createTextNode(link ? link[1] : raw);
        }
      }

      container.appendChild(element);
      cursor = match.index + raw.length;
    }

    appendText(sourceText.slice(cursor));
  }

  function renderMarkdown(text) {
    article.replaceChildren();

    var lines = String(text || "").replace(/\r\n?/g, "\n").split("\n");
    var paragraph = [];
    var list = null;
    var listType = "";
    var codeLines = [];
    var inCode = false;

    function appendInlineElement(tag, textValue) {
      var element = document.createElement(tag);
      appendInlineMarkdown(element, textValue);
      article.appendChild(element);
      return element;
    }

    function flushParagraph() {
      if (!paragraph.length) return;
      appendInlineElement("p", paragraph.join(" "));
      paragraph = [];
    }

    function flushList() {
      list = null;
      listType = "";
    }

    function flushCode() {
      if (!codeLines.length) return;
      var pre = document.createElement("pre");
      var code = document.createElement("code");
      code.textContent = codeLines.join("\n");
      pre.appendChild(code);
      article.appendChild(pre);
      codeLines = [];
    }

    lines.forEach(function (line) {
      if (/^```/.test(line)) {
        flushParagraph();
        flushList();
        if (inCode) flushCode();
        inCode = !inCode;
        return;
      }

      if (inCode) {
        codeLines.push(line);
        return;
      }

      if (!line.trim()) {
        flushParagraph();
        flushList();
        return;
      }

      if (/^---+$/.test(line.trim())) {
        flushParagraph();
        flushList();
        article.appendChild(document.createElement("hr"));
        return;
      }

      var heading = line.match(/^(#{2,4})\s+(.+)$/);
      if (heading) {
        flushParagraph();
        flushList();
        appendInlineElement(heading[1].length === 2 ? "h4" : "h5", heading[2]);
        return;
      }

      var quote = line.match(/^>\s?(.+)$/);
      if (quote) {
        flushParagraph();
        flushList();
        appendInlineElement("blockquote", quote[1]);
        return;
      }

      var unordered = line.match(/^\s*[-*]\s+(.+)$/);
      var ordered = line.match(/^\s*\d+\.\s+(.+)$/);
      if (unordered || ordered) {
        flushParagraph();
        var desired = ordered ? "ol" : "ul";
        if (!list || listType !== desired) {
          flushList();
          list = document.createElement(desired);
          listType = desired;
          article.appendChild(list);
        }
        var item = document.createElement("li");
        appendInlineMarkdown(item, (ordered || unordered)[1]);
        list.appendChild(item);
        return;
      }

      paragraph.push(line.trim());
    });

    flushParagraph();
    flushList();
    if (inCode || codeLines.length) flushCode();
  }

  function renderTitle(markdown) {
    title.replaceChildren();
    appendInlineMarkdown(title, String(markdown || "").replace(/\s+/g, " ").trim());
  }

  function openArticle(post) {
    if (!modal || !post) return Promise.reject(new Error("Article modal unavailable"));
    return Promise.all([loadText(post.title_md), loadText(post.full_article_md)]).then(function (parts) {
      renderTitle(parts[0]);
      meta.textContent = "Article TT-" + String(post.id).padStart(3, "0") + " · " + (post.category || "Field note");
      renderMarkdown(parts[1]);
      if (typeof modal.showModal === "function") modal.showModal();
      else modal.setAttribute("open", "");
    });
  }

  function closeArticle() {
    if (!modal) return;
    if (typeof modal.close === "function") modal.close();
    else modal.removeAttribute("open");
  }

  root.addEventListener("click", function (event) {
    var request = event.target.closest("[data-thread-request-post-id]");
    if (request) {
      event.preventDefault();
      var id = Number(request.getAttribute("data-thread-request-post-id"));
      loadPosts()
        .then(function (posts) {
          var post = posts.find(function (item) { return Number(item.id) === id; });
          return openArticle(post);
        })
        .catch(function () { window.location.href = request.href; });
      return;
    }

    if (event.target === modal) closeArticle();
  });

  if (closeButton) closeButton.addEventListener("click", closeArticle);
}());
