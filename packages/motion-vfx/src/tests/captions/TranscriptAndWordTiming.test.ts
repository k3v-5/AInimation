import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TranscriptParser } from "../../captions/transcript/TranscriptParser.js";

describe("Fase 5E — Transcript & Word Timing Tests", () => {
  it("parses transcript with word-level timestamps precisely", () => {
    const raw = {
      id: "tr_1",
      language: "es",
      segments: [
        {
          id: "s1",
          start: 0.0,
          end: 1.2,
          text: "Esto es increíble",
          words: [
            { id: "w1", text: "Esto", start: 0.0, end: 0.35, confidence: 0.99 },
            { id: "w2", text: "es", start: 0.35, end: 0.48, confidence: 0.98 },
            { id: "w3", text: "increíble", start: 0.48, end: 1.2, confidence: 0.95 },
          ],
        },
      ],
    };

    const transcript = TranscriptParser.fromJSON(raw);
    assert.strictEqual(transcript.id, "tr_1");
    assert.strictEqual(transcript.segments.length, 1);
    assert.strictEqual(transcript.segments[0].words?.length, 3);

    const words = transcript.segments[0].words!;
    assert.strictEqual(words[0].text, "Esto");
    assert.strictEqual(words[0].start, 0.0);
    assert.strictEqual(words[0].end, 0.35);

    assert.strictEqual(words[2].text, "increíble");
    assert.strictEqual(words[2].start, 0.48);
    assert.strictEqual(words[2].end, 1.2);
  });
});
