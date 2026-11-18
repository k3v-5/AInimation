import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import { MotionEngine } from "../../sdk/MotionEngineSDK.js";

describe("Fase 27 — Capa 4: Property-Based Testing (fast-check) Suite for SDK", () => {
  it("PBT: MotionEngine.exportToAfterEffects produces deterministic hash for arbitrary composition parameters", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 100, max: 3840 }),
        fc.integer({ min: 100, max: 2160 }),
        fc.integer({ min: 1, max: 60 }),
        (width, height, duration) => {
          const comp = MotionEngine.createComposition({
            id: `comp_${width}_${height}`,
            name: "PBT Comp",
            width,
            height,
            fps: 30,
            duration,
          });

          const expA = MotionEngine.exportToAfterEffects(comp);
          const expB = MotionEngine.exportToAfterEffects(comp);

          // Invariante de determinismo estricto
          assert.equal(expA.manifest.deterministicHash, expB.manifest.deterministicHash);
          assert.equal(expA.jsxContent, expB.jsxContent);

          return true;
        }
      ),
      { numRuns: 50 }
    );
  });
});
