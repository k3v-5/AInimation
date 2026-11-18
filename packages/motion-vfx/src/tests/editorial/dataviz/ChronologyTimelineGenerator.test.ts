import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { ChronologyTimelineGenerator } from "../../../editorial/dataviz/chronology-timeline-generator.js";
import { TimelineEvent } from "../../../editorial/dataviz/types.js";

describe("Fase 5A — ChronologyTimelineGenerator Suite", () => {
  const sampleEvents: TimelineEvent[] = [
    { id: "e1", date: "1998", label: "Foundation" },
    { id: "e2", date: "2005", label: "Global Launch" },
    { id: "e3", date: "2012", label: "IPO", importance: "PEAK" },
    { id: "e4", date: "2020", label: "Remote Transition" },
    { id: "e5", date: "2026", label: "AI Sovereign Autonomy" },
  ];

  it("compiles horizontal chronology timeline with valid type and checksum", () => {
    const ir = ChronologyTimelineGenerator.compile(sampleEvents, { orientation: "HORIZONTAL" });
    assert.equal(ir.type, "CHRONOLOGY");
    assert.ok(ir.checksumSha256 !== undefined);
    assert.equal(ir.checksumSha256?.length, 64);
  });

  it("compiles vertical chronology timeline", () => {
    const ir = ChronologyTimelineGenerator.compile(sampleEvents, { orientation: "VERTICAL" });
    assert.equal(ir.type, "CHRONOLOGY");
    assert.ok(ir.elements.some((e) => e.type === "NODE"));
  });

  it("sorts unordered input events chronologically (REQ-025 §38)", () => {
    const unordered: TimelineEvent[] = [
      { id: "e3", date: "2020", label: "Later" },
      { id: "e1", date: "1990", label: "Earliest" },
      { id: "e2", date: "2005", label: "Middle" },
    ];
    const ir = ChronologyTimelineGenerator.compile(unordered);
    assert.equal(ir.dataset.points[0].id, "e1");
    assert.equal(ir.dataset.points[1].id, "e2");
    assert.equal(ir.dataset.points[2].id, "e3");
  });

  it("verifies monotonic spatial positioning on horizontal timeline: x(A) <= x(B) (REQ-025 §116, §117)", () => {
    const ir = ChronologyTimelineGenerator.compile(sampleEvents, { orientation: "HORIZONTAL" });
    const nodes = ir.elements.filter((e) => e.type === "NODE");
    assert.equal(nodes.length, 5);

    for (let i = 0; i < nodes.length - 1; i++) {
      assert.ok(
        nodes[i].position.x <= nodes[i + 1].position.x,
        `Node ${i} x (${nodes[i].position.x}) must be <= Node ${i + 1} x (${nodes[i + 1].position.x})`
      );
    }
  });

  it("verifies monotonic spatial positioning on vertical timeline: y(A) <= y(B)", () => {
    const ir = ChronologyTimelineGenerator.compile(sampleEvents, { orientation: "VERTICAL" });
    const nodes = ir.elements.filter((e) => e.type === "NODE");

    for (let i = 0; i < nodes.length - 1; i++) {
      assert.ok(
        nodes[i].position.y <= nodes[i + 1].position.y,
        `Node ${i} y (${nodes[i].position.y}) must be <= Node ${i + 1} y (${nodes[i + 1].position.y})`
      );
    }
  });

  it("normalizes ISO dates in UTC timestamp without local timezone offset (REQ-025 §37)", () => {
    const isoEvents: TimelineEvent[] = [
      { id: "d1", date: "2024-01-01T00:00:00Z", label: "Start of year" },
      { id: "d2", date: "2024-12-31T23:59:59Z", label: "End of year" },
    ];
    const ir = ChronologyTimelineGenerator.compile(isoEvents);
    assert.equal(ir.dataset.points.length, 2);
    assert.ok(ir.dataset.points[0].value < ir.dataset.points[1].value);
  });

  it("renders PEAK and HIGH events with larger radius and accent color", () => {
    const ir = ChronologyTimelineGenerator.compile(sampleEvents);
    const peakNode = ir.elements.find((e) => e.id === "node_e3");
    assert.ok(peakNode !== undefined);
    assert.equal(peakNode?.properties.radius, 8);
    assert.equal(peakNode?.properties.color, "#FF1424"); // Carmesi
  });

  it("generates stagger animation for timeline nodes", () => {
    const ir = ChronologyTimelineGenerator.compile(sampleEvents);
    const anims = ir.animations.filter((a) => a.id.startsWith("anim_node_"));
    assert.equal(anims.length, 5);
    assert.ok(anims[0].startSeconds < anims[4].startSeconds);
  });
});
