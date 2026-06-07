(function () {
  "use strict";

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function gtag() {
    window.dataLayer.push(arguments);
  };

  window.gtag("consent", "default", {
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied",
    analytics_storage: "denied",
    functionality_storage: "granted",
    personalization_storage: "denied",
    security_storage: "granted",
    wait_for_update: 500
  });

  function getConfigPath() {
    var currentScript = document.currentScript;
    if (currentScript && currentScript.dataset && currentScript.dataset.configPath) {
      return currentScript.dataset.configPath;
    }

    var src = currentScript && currentScript.getAttribute("src") ? currentScript.getAttribute("src") : "";
    if (src) {
      return src.replace(/assets\/js\/site-config\.js(?:\?.*)?$/, "config.generated.json");
    }

    return "config.generated.json";
  }

  function pickHostConfig(config) {
    if (!config || typeof config !== "object") return {};

    var host = window.location.hostname || "";
    var withoutWww = host.replace(/^www\./, "");

    if (config[host] && typeof config[host] === "object") return config[host];
    if (config[withoutWww] && typeof config[withoutWww] === "object") return config[withoutWww];

    return config;
  }

  function loadGoogleTagManager(containerId) {
    if (!containerId || window.__etalGtmLoaded) return;

    window.__etalGtmLoaded = true;
    window.dataLayer.push({ "gtm.start": new Date().getTime(), event: "gtm.js" });

    var firstScript = document.getElementsByTagName("script")[0];
    var script = document.createElement("script");
    var dataLayerParam = "dataLayer" !== "dataLayer" ? "&l=dataLayer" : "";

    script.async = true;
    script.src = "https://www.googletagmanager.com/gtm.js?id=" + encodeURIComponent(containerId) + dataLayerParam;
    firstScript.parentNode.insertBefore(script, firstScript);
  }

  function applyConfiguredEmail(config) {
    var email = config.SITE_CONTACT_EMAIL || config.siteContactEmail || config.contactEmail || "";
    if (!email) return;

    document.querySelectorAll('a[href^="mailto:"]').forEach(function (link) {
      var href = link.getAttribute("href") || "";
      var queryIndex = href.indexOf("?");
      var query = queryIndex >= 0 ? href.slice(queryIndex) : "";
      link.setAttribute("href", "mailto:" + email + query);
    });

    document.querySelectorAll("[data-config-text='SITE_CONTACT_EMAIL']").forEach(function (el) {
      el.textContent = email;
    });
  }

  function applyConfig(rawConfig) {
    var config = pickHostConfig(rawConfig);
    window.PORTMASON_CONFIG = config || {};

    var containerId =
      window.PORTMASON_CONFIG.GTM_CONTAINER_ID ||
      window.PORTMASON_CONFIG.gtmContainerId ||
      "";

    loadGoogleTagManager(containerId);

    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", function () {
        applyConfiguredEmail(window.PORTMASON_CONFIG);
      });
    } else {
      applyConfiguredEmail(window.PORTMASON_CONFIG);
    }
  }

  function handleConfigError(error) {
    window.PORTMASON_CONFIG = window.PORTMASON_CONFIG || {};
    if (window.console && typeof window.console.warn === "function") {
      window.console.warn("Unable to load Portmason browser config.", error);
    }
  }

  fetch(getConfigPath(), { cache: "no-store" })
    .then(function (response) {
      if (!response.ok) throw new Error("Unable to load generated config");
      return response.json();
    })
    .then(applyConfig)
    .catch(handleConfigError);
}());
