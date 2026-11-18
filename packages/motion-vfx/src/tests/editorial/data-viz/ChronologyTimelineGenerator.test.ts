import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { ChronologyTimelineGenerator } from "../../../editorial/data-viz/chronology-timeline-generator.js";
import { ChronologyTimelineSpec } from "../../../editorial/data-viz/types.js";
import { verifyVisualizationChecksum } from "../../../editorial/data-viz/dataset-hash.js";

describe("ChronologyTimelineGenerator Tests", () => {
  it("compiles horizontal timeline with alternating milestone lanes", () => {
    const spec: ChronologyTimelineSpec = {
      orientation: "HORIZONTAL",
      animationDurationSeconds: 2.5,
      events: [
        { date: "1945-05-08", title: "VE Day" },
        { date: "1969-07-20", title: "Moon Landing" },
        { date: "1989-11-09", title: "Fall of Berlin Wall" },
      ],
    };

    const ir = ChronologyTimelineGenerator.compile({ spec });

    assert.equal(ir.type, "CHRONOLOGY");
    assert.equal(ir.elements.filter((e) => e.type === "CIRCLE").length, 3);
    assert.ok(verifyVisualizationChecksum(ir));
  });

  it("rejects undated events under default undatedPolicy REJECT", () => {
    const spec: ChronologyTimelineSpec = {
      orientation: "VERTICAL",
      animationDurationSeconds: 2.0,
      events: [
        { date: "2024-01-01", title: "Valid Event" },
        { date: "", title: "Undated Event" },
      ],
    };

    assert.throws(() => ChronologyTimelineGenerator.compile({ spec }));
  });
});
