import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { TrendLineGraphCompiler } from "../../../editorial/data-viz/trend-line-graph-compiler.js";
import { DataVisualizationDataset, TrendLineSpec } from "../../../editorial/data-viz/types.js";
import { verifyVisualizationChecksum } from "../../../editorial/data-viz/dataset-hash.js";

describe("TrendLineGraphCompiler Tests", () => {
  const dataset: DataVisualizationDataset = {
    id: "ds_trend_test",
    title: "Inflation Curve",
    unit: "PERCENT",
    columns: [
      { key: "year", label: "Year", type: "NUMBER" },
      { key: "rate", label: "Rate", type: "NUMBER" },
    ],
    rows: [
      { year: 2021, rate: 2.1 },
      { year: 2022, rate: 8.5 },
      { year: 2023, rate: 4.1 },
      { year: 2024, rate: 2.9 },
    ],
  };

  it("compiles trend line with stroke write-on animation and extrema highlights", () => {
    const spec: TrendLineSpec = {
      xColumn: "year",
      yColumn: "rate",
      showPoints: true,
      showLabels: true,
      showAxis: true,
      showGrid: true,
      highlightExtrema: true,
      animationDurationSeconds: 2.5,
    };

    const ir = TrendLineGraphCompiler.compile({ dataset, spec });

    assert.equal(ir.type, "TREND_LINE");
    const pathElem = ir.elements.find((e) => e.type === "PATH");
    assert.ok(pathElem);

    const writeOnAnim = ir.animation.animations.find((a) => a.property === "PATH_PROGRESS");
    assert.ok(writeOnAnim);
    assert.equal(writeOnAnim.from, 0);
    assert.equal(writeOnAnim.to, 1);

    assert.ok(verifyVisualizationChecksum(ir));
  });

  it("throws if Y column is not numeric", () => {
    const spec: TrendLineSpec = {
      xColumn: "rate",
      yColumn: "year",
      showPoints: true,
      showLabels: false,
      showAxis: true,
      showGrid: false,
      highlightExtrema: false,
      animationDurationSeconds: 2.0,
    };

    const badDataset: DataVisualizationDataset = {
      id: "ds_bad",
      columns: [
        { key: "rate", label: "Rate", type: "NUMBER" },
        { key: "year", label: "Year", type: "STRING" },
      ],
      rows: [{ rate: 10, year: "text" }],
    };

    assert.throws(() => TrendLineGraphCompiler.compile({ dataset: badDataset, spec }));
  });
});
