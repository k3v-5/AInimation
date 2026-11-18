import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { DataNormalizer } from "../../../editorial/dataviz/data-normalizer.js";
import { ScaleEngine } from "../../../editorial/dataviz/scale-engine.js";
import { LayoutEngine } from "../../../editorial/dataviz/layout-engine.js";
import { DataVizHash } from "../../../editorial/dataviz/dataviz-hash.js";
import { dataVisualizationEngine } from "../../../editorial/dataviz/index.js";
import { DataSet } from "../../../editorial/dataviz/types.js";

describe("Fase 5A — DataViz Property-Based Testing Suite", () => {
  it("Property 1: normalizer output is always strictly bounded in [0.0, 1.0] (REQ-025 §72, §111)", () => {
    fc.assert(
      fc.property(
        fc.double({ min: -1e6, max: 1e6, noNaN: true }),
        fc.double({ min: -1e6, max: 1e6, noNaN: true }),
        fc.double({ min: -1e6, max: 1e6, noNaN: true }),
        (val, a, b) => {
          const min = Math.min(a, b);
          const max = Math.max(a, b);
          const norm = DataNormalizer.normalizeValue(val, min, max);
          return Number.isFinite(norm) && norm >= 0.0 && norm <= 1.0;
        }
      ),
      { numRuns: 60 }
    );
  });

  it("Property 2: linear scale mapping never produces NaN or Infinity (REQ-025 §72)", () => {
    fc.assert(
      fc.property(
        fc.double({ min: -1e5, max: 1e5, noNaN: true }),
        fc.double({ min: -1e5, max: 1e5, noNaN: true }),
        fc.double({ min: -1e5, max: 1e5, noNaN: true }),
        fc.double({ min: 0, max: 1920, noNaN: true }),
        fc.double({ min: 0, max: 1080, noNaN: true }),
        (val, dMin, dMax, rMin, rMax) => {
          const scale = ScaleEngine.createScale("LINEAR", [dMin, dMax], [rMin, rMax]);
          const mapped = scale.map(val);
          return Number.isFinite(mapped);
        }
      ),
      { numRuns: 50 }
    );
  });

  it("Property 3: bar geometry bounds always remain within canvas dimensions", () => {
    fc.assert(
      fc.property(
        fc.array(fc.double({ min: -100, max: 100, noNaN: true }), { minLength: 1, maxLength: 8 }),
        (values) => {
          const ds: DataSet = {
            id: "pbt_ds",
            points: values.map((v, i) => ({ id: `p_${i}`, label: `L${i}`, value: v })),
          };

          const res = dataVisualizationEngine.compileBarChart(ds, { composition: "LANDSCAPE_16_9" });
          const canvas = { x: 0, y: 0, width: 1920, height: 1080 };

          for (const el of res.ir.elements) {
            if (el.bounds) {
              if (LayoutEngine.isOutOfBounds(el.bounds, canvas)) {
                return false;
              }
            }
          }
          return true;
        }
      ),
      { numRuns: 30 }
    );
  });

  it("Property 4: reordering keys does NOT alter canonical SHA-256 hash (REQ-025 §72)", () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1 }),
        fc.double({ min: 0, max: 1000, noNaN: true }),
        (label, val) => {
          const obj1 = { id: "test", label, value: val };
          const obj2 = { value: val, id: "test", label };
          return DataVizHash.computeSha256(obj1 as any) === DataVizHash.computeSha256(obj2 as any);
        }
      ),
      { numRuns: 40 }
    );
  });

  it("Property 5: compilation is strictly deterministic: compile(x) === compile(x) (REQ-025 §72)", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 1, max: 100, noNaN: true }),
        fc.double({ min: 1, max: 100, noNaN: true }),
        (v1, v2) => {
          const ds: DataSet = {
            id: "pbt_det_ds",
            points: [
              { id: "a", label: "A", value: v1 },
              { id: "b", label: "B", value: v2 },
            ],
          };

          const run1 = dataVisualizationEngine.compileBarChart(ds);
          const run2 = dataVisualizationEngine.compileBarChart(ds);

          return (
            run1.ir.checksumSha256 === run2.ir.checksumSha256 &&
            run1.jsx === run2.jsx &&
            run1.report.status === run2.report.status
          );
        }
      ),
      { numRuns: 25 }
    );
  });

  it("Property 6: perturbing a single data value changes the SHA-256 hash", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 1, max: 100, noNaN: true }),
        fc.double({ min: 1, max: 100, noNaN: true }),
        (v1, delta) => {
          if (Math.abs(delta) < 0.01) return true;

          const ds1: DataSet = {
            id: "ds_pbt",
            points: [{ id: "p1", label: "V", value: v1 }],
          };
          const ds2: DataSet = {
            id: "ds_pbt",
            points: [{ id: "p1", label: "V", value: v1 + delta }],
          };

          const res1 = dataVisualizationEngine.compileBarChart(ds1);
          const res2 = dataVisualizationEngine.compileBarChart(ds2);

          return res1.ir.checksumSha256 !== res2.ir.checksumSha256;
        }
      ),
      { numRuns: 30 }
    );
  });
});
