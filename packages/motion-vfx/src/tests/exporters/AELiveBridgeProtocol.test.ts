import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AELiveBridgeProtocol } from "../../exporters/ae/bridge/AELiveBridgeProtocol.js";

describe("Exporters — AELiveBridgeProtocol Tests", () => {
  it("formats and serializes JSON-RPC 2.0 requests accurately", () => {
    const req = AELiveBridgeProtocol.createRequest("query_comp", { compName: "MainComp" }, 101);

    assert.equal(req.jsonrpc, "2.0");
    assert.equal(req.id, 101);
    assert.equal(req.method, "query_comp");
    assert.deepEqual(req.params, { compName: "MainComp" });
  });

  it("parses valid JSON-RPC 2.0 responses and catches errors gracefully", () => {
    const validJson = JSON.stringify({
      jsonrpc: "2.0",
      id: 101,
      result: { duration: 120.0, layersCount: 15 },
    });

    const parsed = AELiveBridgeProtocol.parseResponse<{ duration: number }>(validJson);
    assert.equal(parsed.jsonrpc, "2.0");
    assert.equal(parsed.id, 101);
    assert.equal(parsed.result?.duration, 120.0);

    const invalidJson = "invalid_not_json";
    const errorParsed = AELiveBridgeProtocol.parseResponse(invalidJson);
    assert.ok(errorParsed.error);
    assert.equal(errorParsed.error?.code, -32700);
  });

  it("builds ExtendScript payloads for querying comp and patching properties", () => {
    const queryPayload = AELiveBridgeProtocol.buildQueryCompPayload("MyComp");
    assert.ok(queryPayload.includes('app.project'));
    assert.ok(queryPayload.includes('"MyComp"'));
    assert.ok(queryPayload.includes('JSON.stringify'));

    const patchPayload = AELiveBridgeProtocol.buildPatchPropertyPayload("MyComp", "TextLayer", "transform.opacity", "80");
    assert.ok(patchPayload.includes('layer.transform.opacity.setValue(80)'));

    const renderPayload = AELiveBridgeProtocol.buildRenderStatusPayload();
    assert.ok(renderPayload.includes('p.renderQueue'));
    assert.ok(renderPayload.includes('RQItemStatus'));
  });
});
