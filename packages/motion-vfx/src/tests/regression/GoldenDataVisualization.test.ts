import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { AnimatedBarChartCompiler } from "../../editorial/data-viz/animated-bar-chart.js";
import { TrendLineGraphCompiler } from "../../editorial/data-viz/trend-line-graph.js";
import { BigStatCardGenerator } from "../../editorial/data-viz/big-stat-card.js";
import { ChronologyTimelineGenerator } from "../../editorial/data-viz/chronology-timeline.js";
import { Dataset } from "../../editorial/data-viz/contracts.js";

describe("REQ-025 §48: Golden Regression Suite for Data Visualization", () => {
  const fixturesDir = path.resolve(process.cwd(), "src/tests/fixtures/data-viz");

  function loadFixture(filename: string): any {
    const filePath = path.join(fixturesDir, filename);
    const content = fs.readFileSync(filePath, "utf-8");
    return JSON.parse(content);
  }

  function hashPayload(payload: any): string {
    const json = JSON.stringify(payload);
    return crypto.createHash("sha256").update(json).digest("hex");
  }

  it("1. Compiles 'bar-basic.json' with reproducible hash", () => {
    const ds: Dataset = loadFixture("bar-basic.json");
    const compiler = new AnimatedBarChartCompiler();
    const node = compiler.compile(ds);

    assert.equal(node.type, "BAR_CHART");
    assert.equal(node.bars.length, 4);
    assert.equal(node.bars[3].value, 190.4);

    const hash1 = hashPayload(node);
    const hash2 = hashPayload(compiler.compile(ds));
    assert.equal(hash1, hash2);
  });

  it("2. Compiles 'bar-negative.json' preserving baseline and negative bars below baseline", () => {
    const ds: Dataset = loadFixture("bar-negative.json");
    const compiler = new AnimatedBarChartCompiler();
    const node = compiler.compile(ds);

    assert.equal(node.type, "BAR_CHART");
    const negativeBars = node.bars.filter((b: any) => b.isNegative);
    assert.equal(negativeBars.length, 2);
    for (const b of negativeBars) {
      assert.ok(b.value < 0);
      assert.ok(b.y >= node.baseline.y1, `Negative bar y (${b.y}) must be at or below baseline (${node.baseline.y1})`);
    }
  });

  it("3. Compiles 'bar-zero.json' with zero bar exactly on baseline", () => {
    const ds: Dataset = loadFixture("bar-zero.json");
    const compiler = new AnimatedBarChartCompiler();
    const node = compiler.compile(ds);

    const zeroBar = node.bars.find((b: any) => b.value === 0);
    assert.ok(zeroBar);
    assert.equal(zeroBar.y, node.baseline.y1);
  });

  it("4. Compiles 'bar-large.json' with large billion-scale values", () => {
    const ds: Dataset = loadFixture("bar-large.json");
    const compiler = new AnimatedBarChartCompiler();
    const node = compiler.compile(ds);

    assert.equal(node.bars.length, 4);
    assert.ok(node.bars[0].value >= 1e9);
  });

  it("5. Compiles 'trend-basic.json' with chronological monotonicity", () => {
    const ds: Dataset = loadFixture("trend-basic.json");
    const compiler = new TrendLineGraphCompiler();
    const node = compiler.compile(ds);

    assert.equal(node.type, "TREND_LINE");
    assert.equal(node.points.length, 5);
    for (let i = 0; i < node.points.length - 1; i++) {
      assert.ok(node.points[i].x <= node.points[i + 1].x);
    }
    assert.ok(node.svgPath.startsWith("M "));
  });

  it("6. Compiles 'trend-flat.json' resolving flat series without NaN", () => {
    const ds: Dataset = loadFixture("trend-flat.json");
    const compiler = new TrendLineGraphCompiler();
    const node = compiler.compile(ds);

    for (const pt of node.points) {
      assert.equal(pt.normalizedValue, 0.5);
      assert.ok(!isNaN(pt.y));
    }
  });

  it("7. Compiles 'trend-negative.json' handling crossing below zero", () => {
    const ds: Dataset = loadFixture("trend-negative.json");
    const compiler = new TrendLineGraphCompiler();
    const node = compiler.compile(ds);

    assert.equal(node.points.length, 4);
    assert.ok(node.extrema.length >= 1);
  });

  it("8. Generates 'stat-percentage.json' card with % formatted value", () => {
    const ds: Dataset = loadFixture("stat-percentage.json");
    const generator = new BigStatCardGenerator();
    const node = generator.compile(ds);

    assert.equal(node.type, "BIG_STAT");
    assert.equal(node.formattedValue, "73.5%");
    assert.equal(node.primaryLabel, "OF USERS RETURNED");
  });

  it("9. Generates 'stat-currency.json' card with USD currency formatting and evidence", () => {
    const ds: Dataset = loadFixture("stat-currency.json");
    const generator = new BigStatCardGenerator();
    const node = generator.compile(ds);

    assert.equal(node.type, "BIG_STAT");
    assert.ok(node.formattedValue.includes("$"));
    assert.equal(node.sourceText, "sec_filing_form_d_2024");
  });

  it("10. Generates 'timeline-basic.json' chronologically with ordered nodes", () => {
    const ds = loadFixture("timeline-basic.json");
    const generator = new ChronologyTimelineGenerator();
    const node = generator.compile(ds);

    assert.equal(node.type, "CHRONOLOGY");
    assert.equal(node.events.length, 4);
    for (let i = 0; i < node.events.length - 1; i++) {
      assert.ok(node.events[i].normalizedProgress <= node.events[i + 1].normalizedProgress);
      assert.ok(node.events[i].x <= node.events[i + 1].x);
    }
  });

  it("11. Rejects 'timeline-unsorted.json' under BLOCKING policy", () => {
    const ds = loadFixture("timeline-unsorted.json");
    const generator = new ChronologyTimelineGenerator();

    assert.throws(
      () => generator.compile(ds, { config: { unsortedPolicy: "BLOCKING" } }),
      /UNSORTED_EVENTS/
    );
  });
});
