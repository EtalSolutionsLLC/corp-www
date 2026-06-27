const CAPABILITIES = [
  { id: "workflow-integration", title: "Workflow and systems integration", summary: "Connect fragmented tools, remove repeated data movement, and make operational information trustworthy." },
  { id: "ai-automation", title: "A.I. and automation enablement", summary: "Apply A.I. and automation to well-defined work with clear review, governance, and human accountability." },
  { id: "software-development", title: "Practical software development", summary: "Build focused applications, dashboards, and tools around the way the organization actually works." },
  { id: "technology-strategy", title: "Technology strategy and modernization", summary: "Clarify the decision, reduce unnecessary complexity, and sequence modernization into useful moves." },
  { id: "reliability-performance", title: "Reliability and performance engineering", summary: "Improve resilience, observability, delivery confidence, and the speed of systems people depend on." }
];

const OPENAPI = {
  openapi: "3.1.0",
  info: { title: "Et al Systems Lab API", version: "1.0.0" },
  paths: {
    "/v1/health": { get: { summary: "API health" } },
    "/v1/capabilities": { get: { summary: "Et al capability registry" } },
    "/v1/dependency-status": { get: { summary: "Normalized GitHub service status" } },
    "/v1/site-build": { get: { summary: "Served corporate-site build metadata" } },
    "/v1/site-deployment": { get: { summary: "Served corporate-site deployment metadata" } },
    "/v1/site-artifact": { get: { summary: "Served corporate-site artifact manifest" } },
    "/openapi.json": { get: { summary: "OpenAPI contract" } }
  }
};

function json(payload, status = 200, extra = {}) {
  return new Response(JSON.stringify(payload, null, 2) + "\n", {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "access-control-allow-origin": "*",
      "cache-control": status === 200 ? "public, max-age=60" : "no-store",
      ...extra
    }
  });
}

async function dependencyStatus() {
  const started = Date.now();
  const response = await fetch("https://www.githubstatus.com/api/v2/status.json", { headers: { accept: "application/json" } });
  if (!response.ok) return json({ status: "unavailable", upstreamStatus: response.status }, 502);
  const payload = await response.json();
  return json({
    provider: payload?.page?.name || "GitHub",
    service: "GitHub platform",
    status: String(payload?.status?.description || "unknown").toLowerCase(),
    checkedAt: new Date().toISOString(),
    responseTimeMs: Date.now() - started,
    source: "external-api"
  });
}

export default {
  async fetch(request) {
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: { "access-control-allow-origin": "*", "access-control-allow-methods": "GET, OPTIONS" } });
    if (request.method !== "GET") return json({ error: "method_not_allowed" }, 405, { allow: "GET, OPTIONS" });
    const url = new URL(request.url);
    if (url.pathname === "/v1/health") return json({ api: "Et al Systems Lab API", version: "v1", status: "operational", runtime: "Cloudflare Worker" });
    if (url.pathname === "/v1/capabilities") return json({ api: "Et al Systems Lab API", version: "v1", capabilities: CAPABILITIES });
    if (url.pathname === "/v1/dependency-status") return dependencyStatus();
    if (url.pathname === "/v1/site-build" || url.pathname === "/v1/site-deployment" || url.pathname === "/v1/site-artifact") {
      const sourceByPath = {
        "/v1/site-build": "build-info.json",
        "/v1/site-deployment": "deploy-info.json",
        "/v1/site-artifact": "artifact-manifest.json"
      };
      const response = await fetch(`https://www.etal.solutions/${sourceByPath[url.pathname]}`, { headers: { accept: "application/json" } });
      if (!response.ok) return json({ status: "unavailable", upstreamStatus: response.status }, 502);
      return json(await response.json());
    }
    if (url.pathname === "/openapi.json") return json(OPENAPI);
    return json({ error: "not_found", paths: Object.keys(OPENAPI.paths) }, 404);
  }
};
