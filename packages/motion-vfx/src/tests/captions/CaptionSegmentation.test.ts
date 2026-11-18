import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { CaptionSegmenter } from "../../captions/segmentation/CaptionSegmenter.js";
import { TranscriptWord } from "../../captions/types/index.js";

describe("Fase 5E — Caption Segmentation Tests", () => {
  it("segments 10 words into groups of maxWords = 3 (3, 3, 3, 1)", () => {
    const words: TranscriptWord[] = [];
    for (let i = 0; i < 10; i++) {
      words.push({
        id: `w_${i}`,
        text: `Word${i}`,
        start: i * 0.5,
        end: (i + 1) * 0.5,
      });
    }

    const captions = CaptionSegmenter.segment(words, { maxWords: 3 });
    assert.strictEqual(captions.length, 4);

    assert.strictEqual(captions[0].words.length, 3);
    assert.strictEqual(captions[0].timelineRange.start, 0.0);
    assert.strictEqual(captions[0].timelineRange.end, 1.5);

    assert.strictEqual(captions[1].words.length, 3);
    assert.strictEqual(captions[2].words.length, 3);

    assert.strictEqual(captions[3].words.length, 1);
    assert.strictEqual(captions[3].timelineRange.start, 4.5);
    assert.strictEqual(captions[3].timelineRange.end, 5.0);
  });

  it("splits segments when exceeding maxDuration", () => {
    const words: TranscriptWord[] = [
      { id: "w1", text: "Long", start: 0.0, end: 1.5 },
      { id: "w2", text: "Pause", start: 1.5, end: 3.5 }, // 3.5s total exceeds maxDuration = 2.0s
    ];

    const captions = CaptionSegmenter.segment(words, { maxWords: 10, maxDuration: 2.0 });
    assert.strictEqual(captions.length, 2);
    assert.strictEqual(captions[0].words.length, 1);
    assert.strictEqual(captions[1].words.length, 1);
  });
});
