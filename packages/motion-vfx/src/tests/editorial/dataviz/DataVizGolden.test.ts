import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { dataVisualizationEngine } from "../../../editorial/dataviz/index.js";

describe("Fase 5A — DataViz Golden Fixtures Suite (REQ-025 §79, §80)", () => {
  const fixturesDir = path.resolve(process.cwd(), "fixtures/dataviz");

  it("verifies bar-chart-basic fixture matches expected structure and checksum", () => {
    const raw = JSON.parse(fs.readFileSync(path.join(fixturesDir, "bar-chart-basic.json"), "utf-8"));
    const res = dataVisualizationEngine.compileBarChart(raw.input);

    assert.equal(res.ir.type, raw.expectedType);
    assert.equal(res.ir.elements.length, raw.expectedElementCount);
    assert.equal(res.ir.animations.length, raw.expectedAnimationCount);
    assert.ok(res.ir.checksumSha256 !== undefined);
    assert.equal(res.ir.checksumSha256?.length, 64);
  });

  it("verifies bar-chart-negative fixture matches expected structure and checksum", () => {
    const raw = JSON.parse(fs.readFileSync(path.join(fixturesDir, "bar-chart-negative.json"), "utf-8"));
    const res = dataVisualizationEngine.compileBarChart(raw.input);

    assert.equal(res.ir.type, raw.expectedType);
    assert.equal(res.ir.elements.length, raw.expectedElementCount);
    assert.equal(res.ir.animations.length, raw.expectedAnimationCount);
    assert.ok(res.ir.checksumSha256 !== undefined);
  });

  it("verifies trend-line-basic fixture matches expected structure and checksum", () => {
    const raw = JSON.parse(fs.readFileSync(path.join(fixturesDir, "trend-line-basic.json"), "utf-8"));
    const res = dataVisualizationEngine.compileTrendLine(raw.input);

    assert.equal(res.ir.type, raw.expectedType);
    assert.equal(res.ir.elements.length, raw.expectedElementCount);
    assert.equal(res.ir.animations.length, raw.expectedAnimationCount);
    assert.ok(res.ir.checksumSha256 !== undefined);
  });

  it("verifies big-stat-basic fixture matches expected structure and display value", () => {
    const raw = JSON.parse(fs.readFileSync(path.join(fixturesDir, "big-stat-basic.json"), "utf-8"));
    const res = dataVisualizationEngine.generateBigStat(raw.input);

    assert.equal(res.ir.type, raw.expectedType);
    const dominant = res.ir.elements.find((e) => e.id === "stat_dominant_value");
    assert.equal(dominant?.properties.displayValue, raw.expectedDisplayValue);
    assert.equal(res.ir.elements.length, raw.expectedElementCount);
  });

  it("verifies chronology-basic fixture matches expected structure and event count", () => {
    const raw = JSON.parse(fs.readFileSync(path.join(fixturesDir, "chronology-basic.json"), "utf-8"));
    const res = dataVisualizationEngine.generateChronology(raw.input);

    assert.equal(res.ir.type, raw.expectedType);
    assert.equal(res.ir.elements.length, raw.expectedElementCount);
    assert.equal(res.ir.animations.length, raw.expectedAnimationCount);
    assert.ok(res.ir.checksumSha256 !== undefined);
  });
});
