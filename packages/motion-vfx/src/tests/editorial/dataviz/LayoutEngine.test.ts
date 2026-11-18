import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { LayoutEngine } from "../../../editorial/dataviz/layout-engine.js";
import { SafeZoneEngine } from "../../../editorial/dataviz/safe-zone-engine.js";
import { ColorResolver } from "../../../editorial/dataviz/color-resolver.js";
import { LabelEngine } from "../../../editorial/dataviz/label-engine.js";
import { AxisEngine } from "../../../editorial/dataviz/axis-engine.js";

describe("Fase 5A — Layout, SafeZones & Collision Suite", () => {
  it("computes 16:9 landscape bounds and safe zones", () => {
    const layout = LayoutEngine.computeLayout("LANDSCAPE_16_9");
    assert.equal(layout.bounds.width, 1920);
    assert.equal(layout.bounds.height, 1080);
    assert.equal(layout.safeZone.x, 192);
    assert.equal(layout.safeZone.y, 108);
  });

  it("computes 9:16 vertical bounds and safe zones reserving social UI margins", () => {
    const layout = LayoutEngine.computeLayout("VERTICAL_9_16");
    assert.equal(layout.bounds.width, 1080);
    assert.equal(layout.bounds.height, 1920);
    assert.equal(layout.safeZone.y, 280); // 280px top reserved
    assert.equal(layout.safeZone.height, 1180); // 1920 - 280 - 460
  });

  it("computes 1:1 square bounds and safe zones", () => {
    const layout = LayoutEngine.computeLayout("SQUARE_1_1");
    assert.equal(layout.bounds.width, 1080);
    assert.equal(layout.bounds.height, 1080);
    assert.equal(layout.safeZone.width, 900);
  });

  it("verifies element containment inside safe zone", () => {
    const safeZone = SafeZoneEngine.getSafeZone("LANDSCAPE_16_9");
    const inside = { x: 200, y: 200, width: 100, height: 50 };
    const outside = { x: 50, y: 50, width: 100, height: 50 };

    assert.equal(SafeZoneEngine.isInsideSafeZone(inside, safeZone), true);
    assert.equal(SafeZoneEngine.isInsideSafeZone(outside, safeZone), false);
  });

  it("detects elements that are out of composition bounds", () => {
    const bounds = { x: 0, y: 0, width: 1920, height: 1080 };
    assert.equal(LayoutEngine.isOutOfBounds({ x: 100, y: 100, width: 200, height: 100 }, bounds), false);
    assert.equal(LayoutEngine.isOutOfBounds({ x: 1850, y: 100, width: 200, height: 100 }, bounds), true);
  });

  it("evaluates WCAG contrast and flags low-contrast colors", () => {
    const goodContrast = ColorResolver.calculateContrastRatio("#FFFFFF", "#000000");
    assert.equal(goodContrast, 21); // Maximum possible 21:1

    const badIssue = ColorResolver.checkContrast("#FFFF00", "#FFFFFF"); // Yellow on white
    assert.ok(badIssue !== undefined);
    assert.equal(badIssue?.code, "LOW_COLOR_CONTRAST");
  });

  it("detects label collisions and issues WARNING for standard labels", () => {
    const res = LabelEngine.detectCollisions([
      { id: "l1", text: "Alpha", bounds: { x: 100, y: 100, width: 80, height: 20 }, emphasis: "NONE" },
      { id: "l2", text: "Beta", bounds: { x: 150, y: 105, width: 80, height: 20 }, emphasis: "NONE" },
    ]);

    assert.equal(res.hasCollisions, true);
    assert.equal(res.issues.length, 1);
    assert.equal(res.issues[0].severity, "WARNING");
  });

  it("emits BLOCKING CRITICAL_LABEL_COLLISION when PRIMARY label is occluded (REQ-025 §98)", () => {
    const res = LabelEngine.detectCollisions([
      { id: "l1", text: "Key Stat", bounds: { x: 100, y: 100, width: 100, height: 30 }, emphasis: "PRIMARY" },
      { id: "l2", text: "Other", bounds: { x: 120, y: 110, width: 80, height: 20 }, emphasis: "NONE" },
    ]);

    assert.equal(res.hasCollisions, true);
    assert.equal(res.issues[0].code, "CRITICAL_LABEL_COLLISION");
    assert.equal(res.issues[0].severity, "BLOCKING");
  });

  it("creates valid Axis element geometry", () => {
    const axis = AxisEngine.createAxisElement("baseline", {
      x1: 100,
      y1: 500,
      x2: 900,
      y2: 500,
      color: "#333333",
      thicknessPx: 2,
    });

    assert.equal(axis.id, "baseline");
    assert.equal(axis.type, "AXIS");
    assert.equal(axis.position.x, 100);
    assert.equal(axis.position.y, 500);
  });
});
