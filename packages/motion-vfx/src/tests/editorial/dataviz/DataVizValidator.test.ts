import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { DataVizIRBuilder } from "../../../editorial/dataviz/dataviz-ir.js";
import { DataVizValidator } from "../../../editorial/dataviz/dataviz-validator.js";
import { LayoutEngine } from "../../../editorial/dataviz/layout-engine.js";
import { DEFAULT_EDITORIAL_COLORS } from "../../../editorial/dataviz/constants.js";
import { DataVizStyleProfile } from "../../../editorial/dataviz/types.js";

describe("Fase 5A — DataVizValidator Suite", () => {
  const defaultStyle: DataVizStyleProfile = {
    primaryColor: DEFAULT_EDITORIAL_COLORS.primary,
    accentColor: DEFAULT_EDITORIAL_COLORS.accent,
    backgroundColor: DEFAULT_EDITORIAL_COLORS.background,
    textColor: DEFAULT_EDITORIAL_COLORS.text,
    mutedColor: DEFAULT_EDITORIAL_COLORS.muted,
    positiveColor: DEFAULT_EDITORIAL_COLORS.positive,
    negativeColor: DEFAULT_EDITORIAL_COLORS.negative,
    titleFontFamily: "Impact",
    titleFontWeight: 900,
    labelFontFamily: "Arial Black",
    labelFontWeight: 800,
    titleSize: 64,
    labelSize: 24,
    valueSize: 36,
    tracking: 2,
    cornerRadius: 4,
    motionPreset: "EDITORIAL",
  };

  const layout = LayoutEngine.computeLayout("LANDSCAPE_16_9");

  it("validates a compliant DataVizIR and returns status VALID", () => {
    const ir = DataVizIRBuilder.build({
      id: "ir_valid",
      type: "BAR_CHART",
      composition: { width: 1920, height: 1080, fps: 30, durationSeconds: 2.0 },
      dataset: { id: "ds_1", points: [{ id: "p1", label: "A", value: 10, normalizedValue: 0.5 }] },
      layout,
      elements: [
        {
          id: "bar_01",
          type: "BAR",
          position: { x: 300, y: 500 },
          bounds: { x: 300, y: 500, width: 60, height: 200 },
          properties: {},
        },
      ],
      style: defaultStyle,
    });

    const report = DataVizValidator.validate(ir);
    assert.equal(report.status, "VALID");
    assert.equal(report.blockingIssues.length, 0);
    assert.equal(report.deterministic, true);
    assert.equal(report.elementCount, 1);
  });

  it("blocks IR with duplicate element IDs (REQ-025 §56)", () => {
    const ir = DataVizIRBuilder.build({
      id: "ir_dupe",
      type: "BAR_CHART",
      composition: { width: 1920, height: 1080, fps: 30, durationSeconds: 2.0 },
      dataset: { id: "ds_1", points: [] },
      layout,
      elements: [
        { id: "bar_dupe", type: "BAR", position: { x: 100, y: 100 }, properties: {} },
        { id: "bar_dupe", type: "BAR", position: { x: 200, y: 200 }, properties: {} },
      ],
      style: defaultStyle,
    });

    const report = DataVizValidator.validate(ir);
    assert.equal(report.status, "BLOCKED");
    assert.ok(report.blockingIssues.some((i) => i.code === "DUPLICATE_ELEMENT_ID"));
  });

  it("blocks IR with non-finite element positions", () => {
    const ir: any = {
      schemaVersion: "1.0.0",
      engineVersion: "v4.0.0-editorial-master",
      id: "ir_nan_pos",
      type: "BAR_CHART",
      composition: { width: 1920, height: 1080, fps: 30, durationSeconds: 2.0 },
      dataset: { id: "ds_1", points: [] },
      layout,
      scales: [],
      animations: [],
      checksumSha256: "0".repeat(64),
      elements: [
        { id: "bar_nan", type: "BAR", position: { x: NaN, y: 100 }, properties: {} },
      ],
      style: defaultStyle,
      metadata: {
        datasetId: "ds_1",
        visualizationType: "BAR_CHART",
        generatedAtDeterministic: true,
        engineVersion: "v4.0.0-editorial-master",
      },
    };

    const report = DataVizValidator.validate(ir);
    assert.equal(report.status, "BLOCKED");
    assert.ok(report.blockingIssues.some((i) => i.code === "NON_FINITE_POSITION"));
  });

  it("blocks animations targeting non-existent elements", () => {
    const ir = DataVizIRBuilder.build({
      id: "ir_orphan_anim",
      type: "BAR_CHART",
      composition: { width: 1920, height: 1080, fps: 30, durationSeconds: 2.0 },
      dataset: { id: "ds_1", points: [] },
      layout,
      elements: [{ id: "bar_01", type: "BAR", position: { x: 100, y: 100 }, properties: {} }],
      animations: [
        {
          id: "anim_orphan",
          targetId: "non_existent_bar",
          property: "SCALE",
          startSeconds: 0,
          endSeconds: 1,
          easing: "EASE_OUT_CUBIC",
          from: 0,
          to: 1,
        },
      ],
      style: defaultStyle,
    });

    const report = DataVizValidator.validate(ir);
    assert.equal(report.status, "BLOCKED");
    assert.ok(report.blockingIssues.some((i) => i.code === "MISSING_ANIMATION_TARGET"));
  });

  it("detects elements extending out of canvas bounds as warnings", () => {
    const ir = DataVizIRBuilder.build({
      id: "ir_overflow",
      type: "BAR_CHART",
      composition: { width: 1920, height: 1080, fps: 30, durationSeconds: 2.0 },
      dataset: { id: "ds_1", points: [] },
      layout,
      elements: [
        {
          id: "bar_out",
          type: "BAR",
          position: { x: 1900, y: 500 },
          bounds: { x: 1900, y: 500, width: 200, height: 100 }, // Extends to 2100 > 1920
          properties: {},
        },
      ],
      style: defaultStyle,
    });

    const report = DataVizValidator.validate(ir);
    assert.ok(report.warnings.some((w) => w.code === "ELEMENT_OUT_OF_BOUNDS"));
    assert.equal(report.metrics.overflowCount, 1);
  });

  it("calculates occupiedAreaRatio and safeZoneCompliance metrics accurately", () => {
    const ir = DataVizIRBuilder.build({
      id: "ir_metrics",
      type: "BAR_CHART",
      composition: { width: 1920, height: 1080, fps: 30, durationSeconds: 2.0 },
      dataset: { id: "ds_1", points: [{ id: "p1", label: "A", value: 10, normalizedValue: 0.5 }] },
      layout,
      elements: [
        {
          id: "b1",
          type: "BAR",
          position: { x: 300, y: 300 },
          bounds: { x: 300, y: 300, width: 100, height: 200 }, // Area = 20,000
          properties: {},
        },
      ],
      style: defaultStyle,
    });

    const report = DataVizValidator.validate(ir);
    assert.ok(report.metrics.occupiedAreaRatio > 0);
    assert.equal(report.metrics.safeZoneCompliance, 1.0);
    assert.equal(report.metrics.dataPointCount, 1);
  });
});
