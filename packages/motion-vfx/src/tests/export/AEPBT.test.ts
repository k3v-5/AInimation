import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import { AEExpressionBuilder } from "../../exporters/ae/expressions/AEExpressionBuilder.js";
import { AEExpressionValidator } from "../../exporters/ae/expressions/AEExpressionValidator.js";

describe("Fase 26 — Capa 5: Property-Based Testing (fast-check) Suite", () => {
  it("PBT: AEExpressionBuilder generates syntactically balanced expressions for arbitrary parameters", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 100 }),
        fc.integer({ min: 1, max: 1000 }),
        fc.constantFrom<"cycle" | "pingpong" | "offset" | "continue">("cycle", "pingpong", "offset", "continue"),
        fc.integer({ min: 0, max: 10 }),
        (freq, amp, loopType, keyframes) => {
          const w = AEExpressionBuilder.wiggle(freq, amp);
          const valW = AEExpressionValidator.validate(w);
          assert.equal(valW.valid, true);

          const l = AEExpressionBuilder.loopOut(loopType, keyframes);
          const valL = AEExpressionValidator.validate(l);
          assert.equal(valL.valid, true);

          return true;
        }
      ),
      { numRuns: 50 }
    );
  });
});
