import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { LinearScale } from "../../../editorial/data-viz/scales.js";
import {
  formatCompactNumber,
  formatPercentage,
  formatCurrency,
} from "../../../editorial/data-viz/formatters.js";
import {
  deterministicCanonicalStringify,
  generateDeterministicId,
} from "../../../editorial/data-viz/dataset-hash.js";
import { getContrastRatio } from "../../../editorial/data-viz/color-mapping.js";

describe("DataVisualizationProperty Tests (fast-check PBT)", () => {
  it("PBT-001: LinearScale produces clamped values strictly in [0.0, 1.0] for finite inputs", () => {
    fc.assert(
      fc.property(
        fc.float({ noNaN: true }),
        fc.float({ noNaN: true }),
        fc.float({ noNaN: true }),
        (min, max, val) => {
          const scale = new LinearScale(min, max);
          const scaled = scale.scale(val);
          assert.ok(scaled >= 0.0 && scaled <= 1.0);
        }
      )
    );
  });

  it("PBT-002: Formatters never output NaN or Infinity for any finite number", () => {
    fc.assert(
      fc.property(fc.double({ noNaN: true }), (num) => {
        const compact = formatCompactNumber(num);
        const pct = formatPercentage(num);
        const curr = formatCurrency(num);

        assert.equal(compact.includes("NaN"), false);
        assert.equal(compact.includes("Infinity"), false);
        assert.equal(pct.includes("NaN"), false);
        assert.equal(curr.includes("NaN"), false);
      })
    );
  });

  it("PBT-003: Deterministic ID generator produces identical output regardless of object key order", () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1 }),
        fc.integer(),
        fc.boolean(),
        (str, num, bool) => {
          const objA = { a: str, b: num, c: bool };
          const objB = { c: bool, a: str, b: num };
          const idA = generateDeterministicId("pbt", [objA]);
          const idB = generateDeterministicId("pbt", [objB]);
          assert.equal(idA, idB);
        }
      )
    );
  });

  it("PBT-004: Canonical JSON stringifier produces identical strings for permuted keys", () => {
    const safeKeyGen = fc
      .stringMatching(/^[a-z][a-z0-9]{1,8}$/)
      .filter((k) => k !== "__proto__" && k !== "constructor" && k !== "prototype");

    fc.assert(
      fc.property(fc.dictionary(safeKeyGen, fc.integer()), (dict) => {
        const keys = Object.keys(dict);
        const permuted: Record<string, number> = {};
        for (const k of keys.reverse()) {
          permuted[k] = dict[k];
        }
        assert.equal(
          deterministicCanonicalStringify(dict),
          deterministicCanonicalStringify(permuted)
        );
      })
    );
  });

  it("PBT-005: Contrast ratio always resides in [1.0, 21.0]", () => {
    const hexGen = fc
      .array(fc.integer({ min: 0, max: 255 }), { minLength: 3, maxLength: 3 })
      .map(([r, g, b]: number[]) =>
        `#${r.toString(16).padStart(2, "0")}${g.toString(16).padStart(2, "0")}${b.toString(16).padStart(2, "0")}`
      );

    fc.assert(
      fc.property(hexGen, hexGen, (c1: string, c2: string) => {
        const ratio = getContrastRatio(c1, c2);
        assert.ok(ratio >= 1.0 && ratio <= 21.0);
      })
    );
  });
});
