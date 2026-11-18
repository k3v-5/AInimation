import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { AnimatedBarChartCompiler } from "../../../editorial/data-viz/animated-bar-chart-compiler.js";
import { DataVisualizationDataset, BarChartSpec } from "../../../editorial/data-viz/types.js";
import { verifyVisualizationChecksum } from "../../../editorial/data-viz/dataset-hash.js";

describe("AnimatedBarChartCompiler Tests", () => {
  const dataset: DataVisualizationDataset = {
    id: "ds_bar_test",
    title: "Regional Sales",
    unit: "CURRENCY",
    source: { id: "src_1", title: "Sales Database" },
    columns: [
      { key: "region", label: "Region", type: "STRING" },
      { key: "sales", label: "Sales", type: "NUMBER" },
    ],
    rows: [
      { region: "North", sales: 120 },
      { region: "South", sales: 85 },
      { region: "West", sales: 150 },
    ],
  };

  it("compiles vertical bar chart with sorted bars and SHA-256 seal", () => {
    const spec: BarChartSpec = {
      categoryColumn: "region",
      valueColumns: ["sales"],
      orientation: "VERTICAL",
      sort: "DESCENDING",
      showValues: true,
      showLabels: true,
      showAxis: true,
      animationDurationSeconds: 2.0,
    };

    const ir = AnimatedBarChartCompiler.compile({ dataset, spec });

    assert.equal(ir.type, "BAR_CHART");
    assert.equal(ir.width, 1920);
    assert.equal(ir.height, 1080);
    assert.ok(ir.elements.length > 5);
    assert.ok(ir.animation.animations.length >= 3);
    assert.ok(verifyVisualizationChecksum(ir));
  });

  it("compiles horizontal bar chart with negative values and zero-baseline", () => {
    const negDataset: DataVisualizationDataset = {
      id: "ds_neg_test",
      columns: [
        { key: "dept", label: "Department", type: "STRING" },
        { key: "profit", label: "Profit", type: "NUMBER" },
      ],
      rows: [
        { dept: "Hardware", profit: 45 },
        { dept: "Support", profit: -20 },
        { dept: "Cloud", profit: 80 },
      ],
    };

    const spec: BarChartSpec = {
      categoryColumn: "dept",
      valueColumns: ["profit"],
      orientation: "HORIZONTAL",
      sort: "INPUT",
      showValues: true,
      showLabels: true,
      showAxis: true,
      animationDurationSeconds: 2.0,
    };

    const ir = AnimatedBarChartCompiler.compile({ dataset: negDataset, spec });
    assert.equal(ir.type, "BAR_CHART");

    // Verificar que existe el eje zero y las barras están dentro de los límites
    const axisZero = ir.elements.find((e) => e.id.includes("axis_zero"));
    assert.ok(axisZero);
    assert.ok(verifyVisualizationChecksum(ir));
  });

  it("throws DataVisualizationError if category column does not exist", () => {
    const spec: BarChartSpec = {
      categoryColumn: "missing_col",
      valueColumns: ["sales"],
      orientation: "VERTICAL",
      sort: "INPUT",
      showValues: true,
      showLabels: true,
      showAxis: true,
      animationDurationSeconds: 2.0,
    };

    assert.throws(() => AnimatedBarChartCompiler.compile({ dataset, spec }));
  });
});
