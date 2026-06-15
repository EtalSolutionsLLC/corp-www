(function () {
  "use strict";

  var root = document.querySelector("[data-explore-root]");
  if (!root) return;

  var source = root.getAttribute("data-explore-source") || "content/explore-decision-tree.json";
  var trailSteps = Array.prototype.slice.call(root.querySelectorAll("[data-explore-trail-step]"));
  var trailActions = Array.prototype.slice.call(root.querySelectorAll("[data-explore-jump-to]"));
  var eyebrow = root.querySelector("[data-explore-eyebrow]");
  var prompt = root.querySelector("[data-explore-prompt]");
  var options = root.querySelector("[data-explore-options]");
  var questionBody = root.querySelector("[data-explore-question-body]");
  var routeList = root.querySelector("[data-explore-route-list]");
  var signalNote = root.querySelector("[data-explore-signal-note]");
  var result = root.querySelector("[data-explore-result]");
  var back = root.querySelector("[data-explore-back]");
  var reset = root.querySelector("[data-explore-reset]");
  var resultTitle = root.querySelector("[data-explore-result-title]");
  var resultSummary = root.querySelector("[data-explore-result-summary]");
  var resultInsight = root.querySelector("[data-explore-result-insight]");
  var resultWhy = root.querySelector("[data-explore-result-why]");
  var resultMove = root.querySelector("[data-explore-result-move]");
  var routeSummary = root.querySelector("[data-explore-route-summary]");
  var localWeight = root.querySelector("[data-explore-local-weight]");
  var firstLook = root.querySelector("[data-explore-first-look]");
  var firstLookList = root.querySelector("[data-explore-first-look-list]");
  var resultLink = root.querySelector("[data-explore-result-link]");
  var meshHelp = root.querySelector("[data-explore-mesh-help]");
  var meshModal = root.querySelector("[data-explore-mesh-modal]");
  var meshModalClose = root.querySelector("[data-explore-mesh-modal-close]");
  var storageKey = "etal.explore.mesh.v1";
  var tree = null;
  var current = "pressure";
  var history = [];
  var path = [];
  var showingResult = false;
  var weights = readWeights();

  function setHidden(element, hidden) { if (element) element.hidden = hidden; }
  function readWeights() { try { return JSON.parse(window.localStorage.getItem(storageKey)) || { edges: {}, routes: {} }; } catch (error) { return { edges: {}, routes: {} }; } }
  function writeWeights() { try { window.localStorage.setItem(storageKey, JSON.stringify(weights)); } catch (error) { /* optional */ } }
  function edgeRecord(cardKey, edgeKey) { var key = cardKey + ":" + edgeKey; if (!weights.edges[key]) weights.edges[key] = { shown: 0, selected: 0 }; return weights.edges[key]; }
  function recordExposure(cardKey, node) { node.options.forEach(function (option) { edgeRecord(cardKey, option.key).shown += 1; }); writeWeights(); }
  function recordSelection(cardKey, option) { edgeRecord(cardKey, option.key).selected += 1; writeWeights(); }
  function edgeSignal(cardKey, option) { var record = edgeRecord(cardKey, option.key); if (record.shown < 2) return { label: "new choice", strength: 0.18 }; var rate = Math.min(1, record.selected / record.shown); return { label: Math.round(rate * 100) + "% chosen locally", strength: Math.max(0.18, rate) }; }
  function stageOrder() { return (tree && tree.order ? tree.order.slice() : ["pressure", "constraint", "exposure", "move"]).concat(["brief"]); }

  function setTrail(stage) {
    root.setAttribute("data-explore-stage", stage);
    var order = stageOrder();
    var activeIndex = order.indexOf(stage);
    trailSteps.forEach(function (step) {
      var key = step.getAttribute("data-explore-trail-step");
      var index = order.indexOf(key);
      var action = step.querySelector("[data-explore-jump-to]");
      var canReturn = index >= 0 && index < activeIndex;
      step.classList.toggle("is-current", index === activeIndex);
      step.classList.toggle("is-complete", canReturn);
      if (action) { action.disabled = !canReturn; action.setAttribute("aria-label", canReturn ? "Return to " + key + " card" : key + " card"); }
    });
  }

  function goToCard(cardKey) {
    if (!tree || tree.order.indexOf(cardKey) === -1) return;
    var cardIndex = tree.order.indexOf(cardKey);
    path = path.slice(0, cardIndex);
    history = tree.order.slice(0, cardIndex);
    showingResult = false;
    renderQuestion(cardKey);
  }

  function renderRoute() {
    if (!routeList) return;
    routeList.replaceChildren();
    if (!path.length) { var empty = document.createElement("li"); empty.textContent = "No answer yet."; routeList.appendChild(empty); return; }
    path.forEach(function (selection) {
      var li = document.createElement("li");
      var button = document.createElement("button");
      button.type = "button";
      button.className = "explore-route-return";
      button.setAttribute("data-explore-route-jump", selection.card);
      button.setAttribute("aria-label", "Return to " + selection.cardLabel + " card");
      button.innerHTML = '<span>' + selection.cardLabel + '</span><strong>' + selection.label + '</strong>';
      button.addEventListener("click", function () { goToCard(selection.card); });
      li.appendChild(button);
      routeList.appendChild(li);
    });
  }

  function renderQuestion(key) {
    var node = tree && tree.cards && tree.cards[key];
    if (!node || !options || !prompt) return;
    current = key; showingResult = false; setTrail(key);
    if (eyebrow) eyebrow.textContent = node.eyebrow;
    prompt.textContent = node.prompt; options.replaceChildren(); recordExposure(key, node);
    node.options.forEach(function (option, index) {
      var signal = edgeSignal(key, option); var button = document.createElement("button");
      button.type = "button"; button.className = "choice-card mesh-edge mesh-edge-" + (index + 1);
      button.style.setProperty("--edge-strength", signal.strength); button.setAttribute("data-explore-option", option.key);
      button.innerHTML = '<span class="choice-card-icon" aria-hidden="true">' + option.icon + '</span><span class="choice-card-copy"><strong>' + option.label + '</strong><small>' + signal.label + '</small></span><span class="choice-card-arrow" aria-hidden="true">→</span>';
      button.addEventListener("click", function () { choose(option); }); options.appendChild(button);
    });
    renderRoute();
    if (signalNote) signalNote.textContent = "Your choices stay anonymous in this browser. You can review and change them at any time.";
    setHidden(questionBody, false); setHidden(result, true); setHidden(resultLink, true); setHidden(back, history.length === 0); setHidden(reset, history.length === 0);
  }

  function choose(option) {
    var node = tree.cards[current]; recordSelection(current, option);
    path.push({ card: current, cardLabel: node.label, key: option.key, label: option.label, option: option });
    if (option.next) { history.push(current); renderQuestion(option.next); return; }
    if (option.complete) renderResult();
  }

  function unique(items) { return items.filter(function (item, index) { return item && items.indexOf(item) === index; }); }
  function renderResult() {
    var pressure = path[0].option, constraint = path[1].option, exposure = path[2].option, move = path[3].option;
    var routeKey = path.map(function (item) { return item.key; }).join("/"); weights.routes[routeKey] = (weights.routes[routeKey] || 0) + 1; writeWeights();
    showingResult = true; setTrail("brief");
    if (resultTitle) resultTitle.textContent = move.title + " for " + pressure.title;
    if (resultSummary) resultSummary.textContent = pressure.summary + " " + constraint.summary;
    if (resultInsight) resultInsight.textContent = exposure.insight;
    if (resultWhy) resultWhy.textContent = exposure.why;
    if (resultMove) resultMove.textContent = move.move;
    if (routeSummary) routeSummary.textContent = path.map(function (item) { return item.cardLabel + ": " + item.label; }).join(" → ");
    if (localWeight) localWeight.textContent = "This combination of answers has been completed " + weights.routes[routeKey] + " time" + (weights.routes[routeKey] === 1 ? "" : "s") + " in this browser.";
    var firstLookItems = unique([].concat(pressure.firstLook || [], constraint.firstLook || [], exposure.firstLook || [], move.firstLook || [])).slice(0, 6);
    if (firstLookList) { firstLookList.replaceChildren(); firstLookItems.forEach(function (item) { var li = document.createElement("li"); li.textContent = item; firstLookList.appendChild(li); }); }
    setHidden(firstLook, !firstLookItems.length); setHidden(questionBody, true); setHidden(result, false); setHidden(resultLink, false); setHidden(back, false); setHidden(reset, false);
    if (resultLink) { var subject = "Guided path: " + move.title + " for " + pressure.title; var body = "My answers from the guided path:\n\n" + path.map(function (item) { return item.cardLabel + ": " + item.label; }).join("\n") + "\n\nRecommended first move: " + move.move; resultLink.href = "mailto:info@etalsolutions.tech?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body); }
    renderRoute();
  }

  function goBack() { if (showingResult) { goToCard(current); return; } if (!history.length) return; goToCard(history[history.length - 1]); }
  function startOver() { history = []; path = []; showingResult = false; renderQuestion(tree.start); }
  function openMeshModal() { if (!meshModal) return; if (typeof meshModal.showModal === "function") meshModal.showModal(); else meshModal.setAttribute("open", ""); }
  function closeMeshModal() { if (!meshModal) return; if (typeof meshModal.close === "function") meshModal.close(); else meshModal.removeAttribute("open"); }
  trailActions.forEach(function (action) { action.addEventListener("click", function () { if (!action.disabled) goToCard(action.getAttribute("data-explore-jump-to")); }); });
  if (back) back.addEventListener("click", goBack); if (reset) reset.addEventListener("click", startOver); if (meshHelp) meshHelp.addEventListener("click", openMeshModal); if (meshModalClose) meshModalClose.addEventListener("click", closeMeshModal);
  if (meshModal) meshModal.addEventListener("click", function (event) { if (event.target === meshModal) closeMeshModal(); });
  fetch(source, { cache: "no-store" }).then(function (response) { if (!response.ok) throw new Error("Guided path request failed"); return response.json(); }).then(function (data) { if (!data || !data.cards || !data.order || !data.start) throw new Error("Guided path is incomplete"); tree = data; renderQuestion(tree.start); }).catch(function () { if (options) options.innerHTML = '<p class="explore-error">The guided path is temporarily unavailable. Please use the contact link and tell us what is getting in the way.</p>'; });
}());
