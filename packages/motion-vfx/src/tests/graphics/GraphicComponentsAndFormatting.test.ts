import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { CounterFormatter, GraphicComponents } from "../../graphics/components/GraphicComponents.js";

describe("Fase 5J — Graphic Components & Counter Formatting Tests", () => {
  it("formats numbers smartly in compact, currency, integer and percentage modes", () => {
    assert.strictEqual(CounterFormatter.format(1200000, "compact"), "1.2M");
    assert.strictEqual(CounterFormatter.format(45000, "compact"), "45K");
    assert.strictEqual(CounterFormatter.format(1500, "currency"), "$1,500");
    assert.strictEqual(CounterFormatter.format(0.854, "percentage"), "1%");
    assert.strictEqual(CounterFormatter.format(85.4, "percentage"), "85%");
    assert.strictEqual(CounterFormatter.format(1000000, "integer"), "1,000,000");
  });

  it("generates progress bar elements and bar chart elements", () => {
    const pb = GraphicComponents.createProgressBar(50, 0, 100, 400, 20);
    assert.strictEqual(pb.length, 2);
    assert.strictEqual(pb[0].geometry.type, "rounded-rectangle");
    assert.strictEqual((pb[1].geometry as any).width, 200); // 50% de 400 = 200

    const chart = GraphicComponents.createBarChart({
      type: "bar",
      values: [10, 50, 100],
    }, 300, 200);
    assert.strictEqual(chart.length, 3);
  });
});
