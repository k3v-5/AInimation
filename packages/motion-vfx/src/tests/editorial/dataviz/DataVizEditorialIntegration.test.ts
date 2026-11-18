import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { dataVisualizationEngine } from "../../../editorial/dataviz/index.js";
import { StyleProfileManager } from "../../../styles/StyleProfileManager.js";
import { DataSet } from "../../../editorial/dataviz/types.js";

describe("Fase 5A — DataViz Editorial Integration Suite (REQ-025 §81)", () => {
  const editorialDataset: DataSet = {
    id: "ds_investigative",
    title: "Public Spending Divergence",
    unit: "%",
    points: [
      { id: "p1", label: "Health", value: 14.2 },
      { id: "p2", label: "Education", value: 18.5 },
      { id: "p3", label: "Defense", value: 31.0, emphasis: "PRIMARY" },
      { id: "p4", label: "Infrastructure", value: 8.4 },
    ],
    source: "Audit Bureau 2024",
  };

  it("integrates end-to-end: Profile -> Engine -> DataVizIR -> Validator -> AE Compiler", () => {
    // 1. Resolve Profile from existing StyleProfileManager
    const profile = StyleProfileManager.getProfile("time_editorial_impact");
    assert.ok(profile !== undefined);

    // 2. Compile via DataVisualizationEngine
    const result = dataVisualizationEngine.compileBarChart(editorialDataset, {
      composition: "LANDSCAPE_16_9",
      styleProfile: {
        titleFontFamily: profile.typography.fontFamily,
        accentColor: "#FF1424",
      },
      executionMode: "COMPILE",
    });

    // 3. Verify DataVizIR
    assert.equal(result.ir.type, "BAR_CHART");
    assert.equal(result.ir.style.accentColor, "#FF1424");
    assert.ok(result.ir.checksumSha256 !== undefined);

    // 4. Verify Validator Report
    assert.equal(result.report.status, "VALID");
    assert.equal(result.report.blockingIssues.length, 0);
    assert.equal(result.report.deterministic, true);

    // 5. Verify AE JSX Output
    assert.ok(result.jsx !== undefined);
    assert.ok(result.jsx.includes("app.beginUndoGroup"));
    assert.ok(result.jsx.includes("comp.motionBlur = true"));
    assert.ok(result.jsx.includes("[DTV] BAR 001"));
    assert.ok(result.jsx.includes("app.endUndoGroup()"));
  });

  it("respects execution modes: VALIDATE_ONLY, IR_ONLY, COMPILE (REQ-025 §65)", () => {
    const valOnly = dataVisualizationEngine.compileBarChart(editorialDataset, { executionMode: "VALIDATE_ONLY" });
    assert.equal(valOnly.jsx, undefined);
    assert.equal(valOnly.report.status, "VALID");

    const irOnly = dataVisualizationEngine.compileBarChart(editorialDataset, { executionMode: "IR_ONLY" });
    assert.equal(irOnly.jsx, undefined);
    assert.ok(irOnly.ir.checksumSha256 !== undefined);

    const fullCompile = dataVisualizationEngine.compileBarChart(editorialDataset, { executionMode: "COMPILE" });
    assert.ok(fullCompile.jsx !== undefined);
  });
});
