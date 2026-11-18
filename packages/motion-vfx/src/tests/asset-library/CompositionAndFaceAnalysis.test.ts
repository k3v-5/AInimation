import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { CompositionAnalyzer } from "../../asset-library/core/CompositionAnalyzer.js";

describe("Fase 10 — Composition & Face Analysis Tests", () => {
  it("determines safe caption placement zone avoiding face obstruction", () => {
    // Caso 1: Cara en el tercio inferior -> subtítulo debe ir arriba (top)
    const zoneTop = CompositionAnalyzer.determineSafeCaptionZone({
      x: 0.3,
      y: 0.7,
      width: 0.4,
      height: 0.25,
    });
    assert.strictEqual(zoneTop, "top");

    // Caso 2: Cara en el tercio superior -> subtítulo debe ir abajo (bottom)
    const zoneBottom = CompositionAnalyzer.determineSafeCaptionZone({
      x: 0.3,
      y: 0.1,
      width: 0.4,
      height: 0.3,
    });
    assert.strictEqual(zoneBottom, "bottom");
  });

  it("calculates negative space area correctly", () => {
    const comp = CompositionAnalyzer.analyzeComposition(
      { x: 0.2, y: 0.2, width: 0.5, height: 0.4 }, // area = 0.2
      undefined,
      ["#1a1a2e", "#16213e"]
    );

    assert.strictEqual(Math.abs(comp.negativeSpaceArea - 0.8) < 1e-6, true);
    assert.strictEqual(comp.dominantColors.length, 2);
  });
});
