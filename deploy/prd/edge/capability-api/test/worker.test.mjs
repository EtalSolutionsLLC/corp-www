import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";

test("health endpoint publishes the v1 contract", async () => {
  const response = await worker.fetch(new Request("https://api.example/v1/health"));
  assert.equal(response.status, 200);
  const payload = await response.json();
  assert.equal(payload.version, "v1");
  assert.equal(payload.status, "operational");
  assert.equal(response.headers.get("access-control-allow-origin"), "*");
});

test("capabilities endpoint returns structured capabilities", async () => {
  const response = await worker.fetch(new Request("https://api.example/v1/capabilities"));
  const payload = await response.json();
  assert.ok(payload.capabilities.length >= 4);
  assert.ok(payload.capabilities.every((item) => item.id && item.title && item.summary));
});

test("unknown endpoints return a machine-readable 404", async () => {
  const response = await worker.fetch(new Request("https://api.example/nope"));
  assert.equal(response.status, 404);
  const payload = await response.json();
  assert.equal(payload.error, "not_found");
});
