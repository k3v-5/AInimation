import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { AnimatedBarChartCompiler } from "../../../editorial/dataviz/animated-bar-chart-compiler.js";
import { DataSet } from "../../../editorial/dataviz/types.js";

describe("Fase 5A — AnimatedBarChartCompiler Suite", () => {
  const sampleDataset: DataSet = {
    id: "ds_gdp",
    title: "GDP Growth",
    unit: "%",
    points: [
      { id: "p1", label: "US", value: 2.5 },
      { id: "p2", label: "EU", value: 0.8 },
      { id: "p3", label: "JP", value: 1.1, emphasis: "PRIMARY" },
      { id: "p4", label: "UK", value: -0.3 }, // Negative value
    ],
  };

  it("compiles vertical bar chart with type BAR_CHART and valid schema", () => {
    const ir = AnimatedBarChartCompiler.compile(sampleDataset, { orientation: "VERTICAL" });
    assert.equal(ir.type, "BAR_CHART");
    assert.ok(ir.checksumSha256 !== undefined);
    assert.equal(ir.checksumSha256?.length, 64);
  });

  it("compiles horizontal bar chart", () => {
    const ir = AnimatedBarChartCompiler.compile(sampleDataset, { orientation: "HORIZONTAL" });
    assert.equal(ir.type, "BAR_CHART");
    assert.ok(ir.elements.some((e) => e.type === "BAR"));
  });

  it("places zero baseline axis explicitly per REQ-025 §19", () => {
    const ir = AnimatedBarChartCompiler.compile(sampleDataset, { orientation: "VERTICAL", showBaseline: true });
    const baseline = ir.elements.find((e) => e.id === `axis_baseline_${sampleDataset.id}`);
    assert.ok(baseline !== undefined);
    assert.equal(baseline?.type, "AXIS");
  });

  it("handles mixed positive and negative values correctly without baseline = bottom assumption", () => {
    const ir = AnimatedBarChartCompiler.compile(sampleDataset, { orientation: "VERTICAL" });
    const posBar = ir.elements.find((e) => e.id === `bar_${sampleDataset.id}_p1`);
    const negBar = ir.elements.find((e) => e.id === `bar_${sampleDataset.id}_p4`);

    assert.ok(posBar?.bounds !== undefined);
    assert.ok(negBar?.bounds !== undefined);
    // Negative bar y starts at baseline and extends downwards
    assert.ok(negBar!.bounds!.y >= posBar!.bounds!.y);
  });

  it("enforces non-overlapping invariant: bar[i].right <= bar[i+1].left (REQ-025 §21)", () => {
    const ir = AnimatedBarChartCompiler.compile(sampleDataset, { orientation: "VERTICAL" });
    const bars = ir.elements.filter((e) => e.type === "BAR");

    for (let i = 0; i < bars.length - 1; i++) {
      const b1 = bars[i].bounds!;
      const b2 = bars[i + 1].bounds!;
      assert.ok(
        b1.x + b1.width <= b2.x + 1e-4,
        `Bar ${i} right (${b1.x + b1.width}) must be <= Bar ${i + 1} left (${b2.x})`
      );
    }
  });

  it("generates growth animation with EASE_OUT_CUBIC (REQ-025 §22)", () => {
    const ir = AnimatedBarChartCompiler.compile(sampleDataset);
    const growthAnim = ir.animations.find((a) => a.id === `anim_growth_bar_${sampleDataset.id}_p1`);
    assert.ok(growthAnim !== undefined);
    assert.equal(growthAnim?.easing, "EASE_OUT_CUBIC");
    assert.equal(growthAnim?.property, "SCALE");
  });

  it("generates counter animations for numeric values (REQ-025 §23)", () => {
    const ir = AnimatedBarChartCompiler.compile(sampleDataset, { showValues: true });
    const counter = ir.elements.find((e) => e.id === `val_${sampleDataset.id}_p1`);
    assert.ok(counter !== undefined);
    assert.equal(counter?.type, "COUNTER");
    assert.equal(counter?.properties.rawNumericValue, 2.5);
  });

  it("preserves data traceability binding on every bar element (REQ-025 §103)", () => {
    const ir = AnimatedBarChartCompiler.compile(sampleDataset);
    const bar = ir.elements.find((e) => e.id === `bar_${sampleDataset.id}_p3`);
    assert.deepEqual(bar?.dataBinding, {
      datasetId: "ds_gdp",
      dataPointId: "p3",
      sourcePath: "points.2.value",
    });
  });

  it("compiles constant dataset cleanly without NaN or zero-division", () => {
    const constDs: DataSet = {
      id: "ds_const_bar",
      points: [
        { id: "c1", label: "A", value: 10 },
        { id: "c2", label: "B", value: 10 },
      ],
    };
    const ir = AnimatedBarChartCompiler.compile(constDs);
    assert.equal(ir.type, "BAR_CHART");
    assert.equal(ir.elements.filter((e) => e.type === "BAR").length, 2);
  });

  it("highlights PRIMARY emphasis bars with accent color", () => {
    const ir = AnimatedBarChartCompiler.compile(sampleDataset);
    const primaryBar = ir.elements.find((e) => e.id === `bar_${sampleDataset.id}_p3`);
    assert.equal(primaryBar?.properties.color, "#FF1424"); // Carmesi
  });
});
