import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { compileDataVisualization } from "../../../editorial/data-viz/index.js";
import { verifyVisualizationChecksum } from "../../../editorial/data-viz/dataset-hash.js";

describe("DataVisualizationRegression & Golden Fixtures Tests", () => {
  const fixturesDir = path.resolve(process.cwd(), "fixtures/data-viz");

  it("compiles revenue-bar-chart.json fixture cleanly", () => {
    const filePath = path.join(fixturesDir, "revenue-bar-chart.json");
    const raw = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    const result = compileDataVisualization(raw.dataset, raw.spec);

    assert.equal(result.status, "SUCCESS");
    assert.ok(result.visualization);
    assert.equal(result.visualization.type, "BAR_CHART");
    assert.ok(verifyVisualizationChecksum(result.visualization));
  });

  it("compiles population-trend.json fixture cleanly", () => {
    const filePath = path.join(fixturesDir, "population-trend.json");
    const raw = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    const result = compileDataVisualization(raw.dataset, raw.spec);

    assert.equal(result.status, "SUCCESS");
    assert.ok(result.visualization);
    assert.equal(result.visualization.type, "TREND_LINE");
    assert.ok(verifyVisualizationChecksum(result.visualization));
  });

  it("compiles big-stat-revenue.json fixture cleanly", () => {
    const filePath = path.join(fixturesDir, "big-stat-revenue.json");
    const raw = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    const result = compileDataVisualization(null, raw.spec);

    assert.equal(result.status, "SUCCESS");
    assert.ok(result.visualization);
    assert.equal(result.visualization.type, "BIG_STAT");
    assert.ok(verifyVisualizationChecksum(result.visualization));
  });

  it("compiles historical-timeline.json fixture cleanly", () => {
    const filePath = path.join(fixturesDir, "historical-timeline.json");
    const raw = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    const result = compileDataVisualization(null, raw.spec);

    assert.equal(result.status, "SUCCESS");
    assert.ok(result.visualization);
    assert.equal(result.visualization.type, "CHRONOLOGY");
    assert.ok(verifyVisualizationChecksum(result.visualization));
  });

  it("compiles negative-positive-values.json fixture cleanly", () => {
    const filePath = path.join(fixturesDir, "negative-positive-values.json");
    const raw = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    const result = compileDataVisualization(raw.dataset, raw.spec);

    assert.equal(result.status, "SUCCESS");
    assert.ok(result.visualization);
    assert.equal(result.visualization.type, "BAR_CHART");
    assert.ok(verifyVisualizationChecksum(result.visualization));
  });

  it("compiles multilingual-dataset.json fixture cleanly", () => {
    const filePath = path.join(fixturesDir, "multilingual-dataset.json");
    const raw = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    const result = compileDataVisualization(raw.dataset, raw.spec);

    assert.equal(result.status, "SUCCESS");
    assert.ok(result.visualization);
    assert.equal(result.visualization.type, "BAR_CHART");
    assert.ok(verifyVisualizationChecksum(result.visualization));
  });

  it("handles single-row dataset without mathematical errors", () => {
    const singleRowDs = {
      id: "single_row",
      columns: [
        { key: "cat", label: "Cat", type: "STRING" as const },
        { key: "num", label: "Num", type: "NUMBER" as const },
      ],
      rows: [{ cat: "Only", num: 100 }],
    };

    const result = compileDataVisualization(singleRowDs, {
      type: "BAR_CHART",
      spec: {
        categoryColumn: "cat",
        valueColumns: ["num"],
        orientation: "VERTICAL",
        sort: "INPUT",
        showValues: true,
        showLabels: true,
        showAxis: true,
        animationDurationSeconds: 1.0,
      },
    });

    assert.equal(result.status, "SUCCESS");
    assert.ok(result.visualization);
    assert.ok(verifyVisualizationChecksum(result.visualization));
  });
});
