(function () {
  "use strict";

  var root = document.querySelector("[data-site-size-compare]");
  if (!root || typeof window.fetch !== "function") return;

  var endpoint = "https://pagespeedonline.googleapis.com/pagespeedonline/v5/runPagespeed";
  var medianDesktopBytes = 2.86 * 1024 * 1024;
  var selfUrl = root.getAttribute("data-site-size-self-url") || "https://www.etal.solutions/";
  var configUrl = root.getAttribute("data-site-size-config-url") || "config.generated.json";
  var form = root.querySelector("[data-site-size-form]");
  var input = root.querySelector("[data-site-size-url]");
  var submit = root.querySelector("[data-site-size-submit]");
  var status = root.querySelector("[data-site-size-status]");
  var result = root.querySelector("[data-site-size-result]");
  var theirs = root.querySelector("[data-site-size-theirs]");
  var ours = root.querySelector("[data-site-size-ours]");
  var summary = root.querySelector("[data-site-size-summary]");
  var context = root.querySelector("[data-site-size-context]");
  var apiKeyPromise = null;

  function setText(element, value) {
    if (element) element.textContent = value;
  }

  function setBusy(isBusy) {
    if (!submit) return;

    submit.disabled = isBusy;
    submit.setAttribute("aria-busy", isBusy ? "true" : "false");
    submit.innerHTML = isBusy
      ? "Checking both pages…"
      : 'Check my site <span aria-hidden="true">→</span>';
  }

  function normalizeUrl(raw) {
    var value = String(raw || "").trim();
    if (!value) throw new Error("Please enter your homepage address.");
    if (!/^https?:\/\//i.test(value)) value = "https://" + value;

    var parsed;
    try {
      parsed = new URL(value);
    } catch (error) {
      throw new Error("Please enter a valid public homepage address.");
    }

    if (!/^https?:$/.test(parsed.protocol)) {
      throw new Error("Please enter an address that begins with http:// or https://.");
    }

    if (!parsed.hostname || parsed.hostname === "localhost" || parsed.hostname.endsWith(".local")) {
      throw new Error("Please enter a public homepage address.");
    }

    return parsed.href;
  }

  function formatBytes(bytes) {
    if (!Number.isFinite(bytes) || bytes <= 0) return "Not available";
    if (bytes < 1024) return String(Math.round(bytes)) + " B";
    if (bytes < 1024 * 1024) return String(Math.round(bytes / 1024)) + " KB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
  }

  function formatMultiplier(value) {
    if (!Number.isFinite(value) || value <= 0) return "";
    if (value >= 10) return value.toFixed(0) + "×";
    return value.toFixed(1).replace(/\.0$/, "") + "×";
  }

  function describeComparedToOurs(theirBytes, ourBytes) {
    if (theirBytes === ourBytes) {
      return "The two homepages downloaded about the same amount of data in this test.";
    }

    if (theirBytes > ourBytes) {
      return "Your homepage downloaded about " + formatMultiplier(theirBytes / ourBytes) + " more data than this homepage in the same PageSpeed desktop test.";
    }

    return "Your homepage downloaded about " + formatMultiplier(ourBytes / theirBytes) + " less data than this homepage in the same PageSpeed desktop test.";
  }

  function describeComparedToMedian(theirBytes) {
    if (Math.abs(theirBytes - medianDesktopBytes) < 0.05 * medianDesktopBytes) {
      return "For context, that is close to the typical desktop homepage: about 2.86 MB.";
    }

    if (theirBytes > medianDesktopBytes) {
      return "For context, that is about " + formatMultiplier(theirBytes / medianDesktopBytes) + " the typical desktop homepage size of 2.86 MB.";
    }

    return "For context, that is about " + formatMultiplier(medianDesktopBytes / theirBytes) + " lighter than the typical desktop homepage size of 2.86 MB.";
  }

  function pickHostConfig(config) {
    var host = window.location.hostname || "";
    var withoutWww = host.replace(/^www\./, "");

    if (!config || typeof config !== "object") return {};
    if (config[host] && typeof config[host] === "object") return config[host];
    if (config[withoutWww] && typeof config[withoutWww] === "object") return config[withoutWww];

    return config;
  }

  function extractApiKey(config) {
    var hostConfig = pickHostConfig(config);

    return String(
      hostConfig.PAGESPEED_APIKEY ||
      hostConfig.pagespeedApiKey ||
      ""
    ).trim();
  }

  function loadApiKey() {
    if (apiKeyPromise) return apiKeyPromise;

    apiKeyPromise = Promise.resolve()
      .then(function () {
        var configured = extractApiKey(window.PORTMASON_CONFIG || {});
        if (configured) return configured;

        return window.fetch(configUrl, { cache: "no-store" })
          .then(function (response) {
            if (!response.ok) {
              throw new Error("The PageSpeed comparison configuration could not be loaded.");
            }

            return response.json();
          })
          .then(function (config) {
            var apiKey = extractApiKey(config);
            if (!apiKey) {
              throw new Error("The PageSpeed comparison is not configured yet. Run pm-setup after adding PAGESPEED_APIKEY.");
            }

            return apiKey;
          });
      });

    return apiKeyPromise;
  }

  function buildRequest(url, apiKey) {
    var query = new URLSearchParams({
      url: url,
      strategy: "desktop",
      category: "performance",
      key: apiKey
    });

    return endpoint + "?" + query.toString();
  }

  function readApiMessage(payload) {
    var apiError = payload && payload.error && payload.error.message;
    var runtimeError = payload &&
      payload.lighthouseResult &&
      payload.lighthouseResult.runtimeError &&
      payload.lighthouseResult.runtimeError.message;

    return apiError || runtimeError || "";
  }

  function extractTotalBytes(payload, label) {
    var audit = payload &&
      payload.lighthouseResult &&
      payload.lighthouseResult.audits &&
      payload.lighthouseResult.audits["total-byte-weight"];

    var bytes = audit && Number(audit.numericValue);
    if (!Number.isFinite(bytes) || bytes <= 0) {
      throw new Error(label + " did not return a page-size measurement.");
    }

    return bytes;
  }

  function runPageSpeed(url, label, apiKey) {
    return window.fetch(buildRequest(url, apiKey), { method: "GET", mode: "cors" })
      .then(function (response) {
        return response.json()
          .catch(function () { return {}; })
          .then(function (payload) {
            if (!response.ok) {
              throw new Error(label + " could not be checked. " + (readApiMessage(payload) || "Google PageSpeed returned an error."));
            }

            var apiMessage = readApiMessage(payload);
            if (apiMessage) {
              throw new Error(label + " could not be checked. " + apiMessage);
            }

            return extractTotalBytes(payload, label);
          });
      })
      .catch(function (error) {
        if (error && error.message) throw error;
        throw new Error(label + " could not be checked. Google PageSpeed could not be reached from this browser.");
      });
  }

  function showError(message) {
    setText(status, message || "We could not complete the comparison. Please try again in a moment.");
    if (result) result.hidden = true;
  }

  function showResult(theirBytes, ourBytes) {
    setText(theirs, formatBytes(theirBytes));
    setText(ours, formatBytes(ourBytes));
    setText(summary, describeComparedToOurs(theirBytes, ourBytes));
    setText(context, describeComparedToMedian(theirBytes));
    setText(status, "Done. Both homepages were checked with the same desktop test.");
    if (result) result.hidden = false;
  }

  function submitComparison(event) {
    event.preventDefault();

    var theirUrl;
    try {
      theirUrl = normalizeUrl(input && input.value);
    } catch (error) {
      showError(error.message);
      return;
    }

    if (input) input.value = theirUrl;
    setBusy(true);
    setText(status, "Checking both homepages with Google PageSpeed. This may take a few moments.");
    if (result) result.hidden = true;

    loadApiKey()
      .then(function (apiKey) {
        return Promise.allSettled([
          runPageSpeed(theirUrl, "Your homepage", apiKey),
          runPageSpeed(selfUrl, "This homepage", apiKey)
        ]);
      })
      .then(function (measurements) {
        var theirMeasurement = measurements[0];
        var ourMeasurement = measurements[1];

        if (theirMeasurement.status === "rejected") {
          throw theirMeasurement.reason;
        }

        if (ourMeasurement.status === "rejected") {
          throw ourMeasurement.reason;
        }

        showResult(theirMeasurement.value, ourMeasurement.value);
      })
      .catch(function (error) {
        showError(error && error.message ? error.message : "The independent comparison is temporarily unavailable.");
      })
      .finally(function () {
        setBusy(false);
      });
  }

  if (form) form.addEventListener("submit", submitComparison);
}());
