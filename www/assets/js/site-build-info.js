(function () {
  "use strict";

  var trigger = document.querySelector("[data-site-build-open]");
  var modal = document.querySelector("[data-site-build-modal]");

  if (!trigger || !modal || typeof modal.showModal !== "function") {
    return;
  }

  var closeButton = modal.querySelector("[data-site-build-close]");
  var fields = {
    version: modal.querySelector("[data-site-build-version]"),
    commit: modal.querySelector("[data-site-build-commit]"),
    built_at: modal.querySelector("[data-site-build-time]"),
    target: modal.querySelector("[data-site-build-target]")
  };
  var loaded = false;

  function text(field, value) {
    if (fields[field]) {
      fields[field].textContent = value || "Unavailable";
    }
  }

  function fallbackVersion() {
    var meta = document.querySelector('meta[name="etal-site-build"]');
    return meta ? meta.getAttribute("content") : "Unavailable";
  }

  function loadBuildInfo() {
    if (loaded) {
      return Promise.resolve();
    }

    var infoMeta = document.querySelector('meta[name="etal-site-build-info"]');
    var endpoint = infoMeta ? infoMeta.getAttribute("content") : "/build-info.json";

    return fetch(endpoint, { cache: "no-store" })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Build information was not available");
        }
        return response.json();
      })
      .then(function (info) {
        text("version", info.version || fallbackVersion());
        text("commit", info.commit);
        text("built_at", info.built_at);
        text("target", info.target);
        loaded = true;
      })
      .catch(function () {
        text("version", fallbackVersion());
        text("commit", "Unavailable");
        text("built_at", "Unavailable");
        text("target", window.location.hostname || "Unavailable");
      });
  }

  trigger.addEventListener("click", function () {
    loadBuildInfo().finally(function () {
      modal.showModal();
    });
  });

  if (closeButton) {
    closeButton.addEventListener("click", function () {
      modal.close();
    });
  }

  modal.addEventListener("click", function (event) {
    if (event.target === modal) {
      modal.close();
    }
  });
})();
