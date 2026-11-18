import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { AnimatedBarChartCompiler } from "../../../editorial/data-viz/animated-bar-chart-compiler.js";
import {
  deterministicCanonicalStringify,
  verifyVisualizationChecksum,
} from "../../../editorial/data-viz/dataset-hash.js";
import { DataVisualizationDataset, BarChartSpec } from "../../../editorial/data-viz/types.js";

describe("DataVisualizationDeterminism Tests", () => {
  const dataset: DataVisualizationDataset = {
    id: "ds_determ_test",
    title: "Determinism Probe",
    unit: "PERCENT",
    columns: [
      { key: "category", label: "Category", type: "STRING" },
      { key: "share", label: "Share", type: "NUMBER" },
    ],
    rows: [
      { category: "Alpha", share: 35.2 },
      { category: "Beta", share: 44.8 },
      { category: "Gamma", share: 20.0 },
    ],
  };

  const spec: BarChartSpec = {
    categoryColumn: "category",
    valueColumns: ["share"],
    orientation: "VERTICAL",
    sort: "DESCENDING",
    showValues: true,
    showLabels: true,
    showAxis: true,
    animationDurationSeconds: 2.0,
  };

  it("produces byte-identical canonical JSON across 100 repeated executions", () => {
    const baseIR = AnimatedBarChartCompiler.compile({ dataset, spec });
    const baseCanonical = deterministicCanonicalStringify(baseIR);
    const baseChecksum = baseIR.checksumSha256;

    for (let i = 0; i < 100; i++) {
      const runIR = AnimatedBarChartCompiler.compile({ dataset, spec });
      const runCanonical = deterministicCanonicalStringify(runIR);
      assert.equal(runCanonical, baseCanonical);
      assert.equal(runIR.checksumSha256, baseChecksum);
    }
  });

  it("strictly preserves input dataset immutability", () => {
    const originalClone = JSON.parse(JSON.stringify(dataset));
    AnimatedBarChartCompiler.compile({ dataset, spec });
    assert.deepEqual(dataset, originalClone);
  });

  it("detects tampered IR when elements or geometry are altered", () => {
    const ir = AnimatedBarChartCompiler.compile({ dataset, spec });
    assert.equal(verifyVisualizationChecksum(ir), true);

    // Alteración maliciosa de una coordenada
    const tampered = JSON.parse(JSON.stringify(ir));
    tampered.elements[1].x += 0.001;
    assert.equal(verifyVisualizationChecksum(tampered), false);
  });
});
