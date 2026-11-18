import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ImageElement } from "../../elements/ImageElement.js";

describe("Fase 2B — ImageElement Description Tests", () => {
  it("describes image asset reference and evaluates state deterministically", () => {
    const img = new ImageElement({
      assetId: "logo_512",
      startTime: 2,
      duration: 5,
    });

    assert.strictEqual(img.assetId, "logo_512");
    assert.strictEqual(img.type, "image");

    const evalAt3 = img.evaluate(3);
    assert.strictEqual(evalAt3.active, true);
    assert.strictEqual(evalAt3.assetId, "logo_512");
    assert.strictEqual(evalAt3.localTime, 1);
  });
});
