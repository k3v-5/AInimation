import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { FontRegistry } from "../../typography/fonts/FontRegistry.js";

describe("Fase 5F — Font Registry & Fallback Resolver Tests", () => {
  it("resolves registered fonts and handles weight fallback matching", () => {
    assert.strictEqual(FontRegistry.has("Inter"), true);
    assert.strictEqual(FontRegistry.has("Montserrat"), true);

    // Solicitar Inter weight 800 -> Debe resolver a Inter weight 700 (el más cercano disponible)
    const resolvedInter = FontRegistry.resolve("Inter", 800);
    assert.strictEqual(resolvedInter.family, "Inter");
    assert.strictEqual(resolvedInter.weight, 700);

    // Solicitar fuente inexistente "CustomNonExistent" -> Fallback a "Inter"
    const fallbackFont = FontRegistry.resolve("CustomNonExistent", 400);
    assert.strictEqual(fallbackFont.family, "Inter");
    assert.strictEqual(fallbackFont.weight, 400);
  });

  it("throws ValidationError on duplicate font variant registration", () => {
    assert.throws(
      () =>
        FontRegistry.register({
          family: "Inter",
          weight: 400,
          style: "normal",
          metrics: { ascent: 0.8, descent: 0.2, lineGap: 0, unitsPerEm: 1000 },
        }),
      /DUPLICATE_FONT/
    );
  });
});
