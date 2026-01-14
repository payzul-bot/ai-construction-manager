import assert from "node:assert/strict";
import { deleteManyProjects } from "../src/lib/api/index.js";

process.env.NEXT_PUBLIC_API_BASE = "http://example.test";
process.env.NEXT_PUBLIC_TENANT_ID = "demo";

let captured = null;

global.fetch = async (_url, options) => {
  captured = options;
  return {
    ok: true,
    status: 200,
    statusText: "OK",
    text: async () => JSON.stringify({ deleted: 1 })
  };
};

const run = async () => {
  await deleteManyProjects(["project-1", "project-2"]);

  assert.ok(captured, "fetch was not called");
  assert.equal(captured.method, "POST");
  assert.equal(captured.headers["X-Tenant-Id"], "demo");

  const body = JSON.parse(captured.body);
  assert.ok(Array.isArray(body.project_ids), "project_ids should be an array");
  assert.equal(body.project_ids.length, 2);
  assert.equal(body.ids, undefined);

  console.log("check_delete_many_payload: ok");
};

run().catch((error) => {
  console.error("check_delete_many_payload failed:", error);
  process.exit(1);
});
