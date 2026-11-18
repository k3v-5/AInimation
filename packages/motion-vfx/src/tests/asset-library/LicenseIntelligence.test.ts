import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { LicenseManager } from "../../asset-library/core/LicenseManager.js";

describe("Fase 10 — License Intelligence Tests", () => {
  it("determines commercial safety and prevents restricted assets in final renders", () => {
    assert.strictEqual(LicenseManager.isCommercialSafe("royalty-free"), true);
    assert.strictEqual(LicenseManager.isCommercialSafe("licensed"), true);
    assert.strictEqual(LicenseManager.isCommercialSafe("personal"), false);
    assert.strictEqual(LicenseManager.isCommercialSafe("restricted"), false);

    assert.strictEqual(LicenseManager.canUseInRender("restricted", false), false);
    assert.strictEqual(LicenseManager.canUseInRender("restricted", true), true);
    assert.strictEqual(LicenseManager.canUseInRender("royalty-free", false), true);
  });
});
