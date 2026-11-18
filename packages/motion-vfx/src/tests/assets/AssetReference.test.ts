import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetReference } from "../../assets/AssetReference.js";
import { AssetRegistry } from "../../assets/AssetRegistry.js";

describe("Fase 2A — AssetReference Resolution Tests", () => {
  it("resolves lightweight AssetReference against registry", () => {
    const reg = new AssetRegistry();
    reg.add({
      id: "brand_logo",
      type: "image",
      source: { path: "assets/brand.png" },
      metadata: { width: 512, height: 512 },
    });

    const ref: AssetReference = {
      id: "brand_logo",
      type: "image",
    };

    assert.strictEqual(reg.has(ref.id), true);
    const resolved = reg.require(ref.id);
    assert.strictEqual(resolved.id, "brand_logo");
    assert.strictEqual(resolved.source.path, "assets/brand.png");
  });
});
