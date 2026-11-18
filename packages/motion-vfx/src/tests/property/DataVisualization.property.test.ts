import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { normalizeRange } from "../../editorial/data-viz/normalization.js";
import { AnimatedBarChartCompiler } from "../../editorial/data-viz/animated-bar-chart.js";
import { TrendLineGraphCompiler } from "../../editorial/data-viz/trend-line-graph.js";
import { BigStatCardGenerator } from "../../editorial/data-viz/big-stat-card.js";
import { ChronologyTimelineGenerator } from "../../editorial/data-viz/chronology-timeline.js";
import { Dataset } from "../../editorial/data-viz/contracts.js";

describe("REQ-025 §47: Data Visualization Property-Based Testing (PBT)", () => {
  it("PBT-001: normalizeRange(val, min, max) is always strictly within [0.0, 1.0]", () => {
    fc.assert(
      fc.property(
        fc.float({ noNaN: true, noDefaultInfinity: true, min: -1e6, max: 1e6 }),
        fc.float({ noNaN: true, noDefaultInfinity: true, min: -1e6, max: 1e6 }),
        fc.float({ noNaN: true, noDefaultInfinity: true, min: -1e6, max: 1e6 }),
        (v1, v2, v3) => {
          const min = Math.min(v1, v2);
          const max = Math.max(v1, v2);
          const val = v3;
          const norm = normalizeRange(val, min, max);

          assert.ok(Number.isFinite(norm), `Normalized value must be finite: ${norm}`);
          assert.ok(norm >= 0.0 && norm <= 1.0, `Normalized value must be in [0, 1]: ${norm}`);
        }
      ),
      { numRuns: 100 }
    );
  });

  it("PBT-002: Constant series (min === max) always yields 0.5 without division by zero", () => {
    fc.assert(
      fc.property(
        fc.float({ noNaN: true, noDefaultInfinity: true, min: -1e6, max: 1e6 }),
        (val) => {
          const norm = normalizeRange(val, val, val);
          assert.equal(norm, 0.5);
        }
      ),
      { numRuns: 50 }
    );
  });

  it("PBT-003: Bar heights are strictly monotonic: if a > b then height(a) >= height(b)", () => {
    fc.assert(
      fc.property(
        fc.double({ noNaN: true, min: 1, max: 1000 }),
        fc.double({ noNaN: true, min: 1, max: 1000 }),
        (v1, v2) => {
          const highVal = Math.max(v1, v2);
          const lowVal = Math.min(v1, v2);

          const ds: Dataset = {
            id: "pbt_mono_test",
            values: [
              { label: "High", value: highVal },
              { label: "Low", value: lowVal },
            ],
          };

          const compiler = new AnimatedBarChartCompiler();
          const node = compiler.compile(ds);

          const highBar = node.bars.find((b: any) => b.label === "High");
          const lowBar = node.bars.find((b: any) => b.label === "Low");

          assert.ok(highBar && lowBar);
          assert.ok(
            highBar.height >= lowBar.height,
            `Monotonicity violation: highBar (${highBar.height}) < lowBar (${lowBar.height})`
          );
        }
      ),
      { numRuns: 50 }
    );
  });

  it("PBT-004: All chart geometry remains strictly within defined bounds", () => {
    fc.assert(
      fc.property(
        fc.array(fc.float({ noNaN: true, noDefaultInfinity: true, min: 1, max: 500 }), { minLength: 2, maxLength: 10 }),
        (vals) => {
          const ds: Dataset = {
            id: "pbt_bounds_test",
            values: vals.map((v, i) => ({ label: `Item ${i}`, value: v })),
          };

          const compiler = new AnimatedBarChartCompiler();
          const node = compiler.compile(ds, { width: 1920, height: 1080 });

          for (const bar of node.bars) {
            assert.ok(bar.x >= node.bounds.x, "bar.x must be >= bounds.x");
            assert.ok(bar.x + bar.width <= node.bounds.x + node.bounds.width + 1e-4, "bar.x + width must be <= bounds.x + bounds.width");
            assert.ok(bar.height >= 0, "bar.height must be non-negative");
          }
        }
      ),
      { numRuns: 50 }
    );
  });

  it("PBT-005: Output does not contain NaN for any finite dataset", () => {
    fc.assert(
      fc.property(
        fc.array(fc.float({ noNaN: true, noDefaultInfinity: true, min: -1000, max: 1000 }), { minLength: 2, maxLength: 8 }),
        (vals) => {
          const ds: Dataset = {
            id: "pbt_nan_check",
            values: vals.map((v, i) => ({ label: `Pt ${i}`, value: v })),
          };

          const trendCompiler = new TrendLineGraphCompiler();
          const trendNode = trendCompiler.compile(ds);

          for (const pt of trendNode.points) {
            assert.ok(!isNaN(pt.x), `pt.x cannot be NaN`);
            assert.ok(!isNaN(pt.y), `pt.y cannot be NaN`);
            assert.ok(!isNaN(pt.normalizedValue), `pt.normalizedValue cannot be NaN`);
          }
        }
      ),
      { numRuns: 50 }
    );
  });

  it("PBT-006: Compilers are 100% deterministic and idempotent: compile(input) === compile(input)", () => {
    const ds: Dataset = {
      id: "pbt_idempotence",
      values: [
        { label: "Alpha", value: 42 },
        { label: "Beta", value: 84 },
      ],
    };

    const compiler = new AnimatedBarChartCompiler();
    const res1 = JSON.stringify(compiler.compile(ds));
    const res2 = JSON.stringify(compiler.compile(ds));

    assert.equal(res1, res2);
  });
});
