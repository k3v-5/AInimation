import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { KaraokeGenerator } from "../../../vlog/index.js";

describe("Milestone 6-B — Karaoke Generator Suite", () => {
  const mockWordTimings = [
    { word: "Bienvenidos", startSeconds: 0.0, endSeconds: 0.5, confidence: 0.99 },
    { word: "a", startSeconds: 0.5, endSeconds: 0.7, confidence: 0.99 },
    { word: "la", startSeconds: 0.7, endSeconds: 0.9, confidence: 0.99 },
    { word: "ciudad", startSeconds: 0.9, endSeconds: 1.4, confidence: 0.99 },
    { word: "de", startSeconds: 1.4, endSeconds: 1.6, confidence: 0.99 },
    { word: "Guadalajara", startSeconds: 1.6, endSeconds: 2.3, confidence: 0.99 },
  ];

  it("generates synchronized karaoke cues with uppercase text and highlight colors", () => {
    const cues = KaraokeGenerator.generateCues(mockWordTimings, "es-MX", {
      wordsPerCueMax: 4,
    });

    assert.ok(cues.length >= 2);
    assert.equal(cues[0].words.length, 4);
    assert.equal(cues[0].text, "BIENVENIDOS A LA CIUDAD");
    assert.equal(cues[0].words[0].highlightColor, "#FF1424");
    assert.equal(cues[0].startSeconds, 0.0);
    assert.equal(cues[0].endSeconds, 1.4);

    assert.equal(cues[1].text, "DE GUADALAJARA");
    assert.equal(cues[1].startSeconds, 1.4);
    assert.equal(cues[1].endSeconds, 2.3);
  });

  it("handles empty timings safely returning empty array", () => {
    const cues = KaraokeGenerator.generateCues([], "en-US");
    assert.deepEqual(cues, []);
  });
});
