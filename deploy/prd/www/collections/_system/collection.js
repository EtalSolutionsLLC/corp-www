/* Portmason Collections™: shared browser runtime and profile registry. */
(function (global) {
  "use strict";

  var profiles = Object.create(null);
  var instances = Object.create(null);
  var contextPromises = new Map();

  function requireName(value, label) {
    var name = String(value || "").trim();
    if (!name) throw new Error("Portmason Collections: " + label + " is required");
    return name;
  }

  function registerProfile(mode, profile) {
    var name = requireName(mode, "profile mode");
    if (!profile || typeof profile.initialize !== "function") {
      throw new Error("Portmason Collections: profile " + name + " must expose initialize(root, context)");
    }
    if (profiles[name]) {
      throw new Error("Portmason Collections: profile already registered: " + name);
    }
    profiles[name] = profile;
    return profile;
  }

  function registerInstance(collectionId, adapter) {
    var id = requireName(collectionId, "collection id");
    if (!adapter || typeof adapter !== "object") {
      throw new Error("Portmason Collections: instance adapter must be an object: " + id);
    }
    if (instances[id]) {
      throw new Error("Portmason Collections: instance adapter already registered: " + id);
    }
    instances[id] = adapter;
    return adapter;
  }

  function getInstance(collectionId) {
    return instances[String(collectionId || "")] || null;
  }

  function loadCollectionContext(root) {
    var configSource = root.getAttribute("data-collection-config");
    if (!configSource) {
      return Promise.reject(new Error("Portmason Collections: data-collection-config is missing"));
    }

    var manifestUrl = new URL(configSource, global.location.href);
    var cacheKey = manifestUrl.href;
    if (contextPromises.has(cacheKey)) return contextPromises.get(cacheKey);

    var runtime = global.PortmasonCollectionRuntime;
    if (!runtime || typeof runtime.loadCollection !== "function") {
      return Promise.reject(new Error("Portmason Collections: filesystem runtime is unavailable"));
    }
    var promise = runtime.loadCollection(manifestUrl).then(function (loaded) {
      return {
        root: root,
        id: String(loaded.manifest.id || root.getAttribute("data-collection-id") || ""),
        mode: String(loaded.manifest.mode || root.getAttribute("data-collection-mode") || ""),
        manifest: loaded.manifest,
        items: loaded.items,
        selectedItems: loaded.selectedItems,
        selectionDate: loaded.selectionDate,
        manifestUrl: loaded.manifestUrl,
        baseUrl: new URL(".", loaded.manifestUrl)
      };
    });

    contextPromises.set(cacheKey, promise);
    return promise;
  }

  function buildRuntimeContext(root, collectionId, mode) {
    return {
      root: root,
      id: collectionId,
      mode: mode,
      load: function () { return loadCollectionContext(root); },
      getInstance: function () { return getInstance(collectionId); },
      api: api
    };
  }

  function initCollection(root) {
    if (!root || !root.getAttribute) return Promise.resolve(null);
    if (root.getAttribute("data-collection-runtime") === "initialized") {
      return Promise.resolve(root);
    }
    if (root.getAttribute("data-collection-runtime") === "initializing" && root.__portmasonCollectionPromise) {
      return root.__portmasonCollectionPromise;
    }

    var collectionId = requireName(root.getAttribute("data-collection-id"), "data-collection-id");
    var mode = requireName(root.getAttribute("data-collection-mode"), "data-collection-mode");
    var profile = profiles[mode];
    if (!profile) {
      return Promise.reject(new Error("Portmason Collections: no profile registered for mode: " + mode));
    }

    root.setAttribute("data-collection-runtime", "initializing");
    var runtimeContext = buildRuntimeContext(root, collectionId, mode);
    var promise = Promise.resolve(profile.initialize(root, runtimeContext))
      .then(function () {
        root.setAttribute("data-collection-runtime", "initialized");
        root.dispatchEvent(new CustomEvent("portmason:collection-ready", {
          bubbles: true,
          detail: { id: collectionId, mode: mode }
        }));
        return root;
      })
      .catch(function (error) {
        root.setAttribute("data-collection-runtime", "failed");
        root.dispatchEvent(new CustomEvent("portmason:collection-error", {
          bubbles: true,
          detail: { id: collectionId, mode: mode, error: error }
        }));
        throw error;
      });

    root.__portmasonCollectionPromise = promise;
    return promise;
  }

  function initAll(scope) {
    var container = scope && scope.querySelectorAll ? scope : document;
    var roots = [];
    if (container.matches && container.matches("[data-collection]")) roots.push(container);
    roots = roots.concat(Array.prototype.slice.call(container.querySelectorAll("[data-collection]")));
    return Promise.allSettled(roots.map(initCollection));
  }

  var api = {
    registerProfile: registerProfile,
    registerInstance: registerInstance,
    getInstance: getInstance,
    loadCollectionContext: loadCollectionContext,
    initCollection: initCollection,
    initAll: initAll,
    profiles: profiles
  };

  global.PortmasonCollections = api;

  document.addEventListener("DOMContentLoaded", function () {
    initAll(document).then(function (results) {
      results.forEach(function (result) {
        if (result.status === "rejected") {
          console.error(result.reason);
        }
      });
    });
  });
}(window));
