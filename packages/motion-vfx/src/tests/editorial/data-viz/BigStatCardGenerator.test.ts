import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { BigStatCardGenerator } from "../../../editorial/data-viz/big-stat-card-generator.js";
import { BigStatSpec } from "../../../editorial/data-viz/types.js";
import { verifyVisualizationChecksum } from "../../../editorial/data-viz/dataset-hash.js";

describe("BigStatCardGenerator Tests", () => {
  it("generates isolated big stat card without requiring a prior dataset", () => {
    const spec: BigStatSpec = {
      staticValue: 14200000,
      label: "Subscribers Reached",
      prefix: "",
      unit: "COUNT",
      sourceLabel: "YouTube Analytics Verified",
      animationDurationSeconds: 1.8,
    };

    const ir = BigStatCardGenerator.compile({ spec });

    assert.equal(ir.type, "BIG_STAT");
    const valElem = ir.elements.find((e) => e.text && e.text.includes("14.2"));
    assert.ok(valElem);

    const scaleAnim = ir.animation.animations.find((a) => a.property === "SCALE");
    assert.ok(scaleAnim);

    assert.ok(verifyVisualizationChecksum(ir));
  });

  it("extracts stat value from a tabular dataset column", () => {
    const dataset = {
      id: "ds_stat_val",
      columns: [{ key: "net_worth", label: "Net Worth", type: "NUMBER" as const }],
      rows: [{ net_worth: 250000000 }],
    };

    const spec: BigStatSpec = {
      valueColumn: "net_worth",
      label: "Valuation",
      prefix: "$",
      animationDurationSeconds: 2.0,
    };

    const ir = BigStatCardGenerator.compile({ dataset, spec });
    assert.equal(ir.type, "BIG_STAT");
    const valElem = ir.elements.find((e) => e.text && e.text.includes("$250M"));
    assert.ok(valElem);
    assert.ok(verifyVisualizationChecksum(ir));
  });
});
