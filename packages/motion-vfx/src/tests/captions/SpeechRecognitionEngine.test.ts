import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AudioBuffer } from "../../audio/core/AudioBuffer.js";
import { SpeechRecognitionEngine } from "../../captions/intelligence/SpeechRecognitionEngine.js";

describe("Captions — SpeechRecognitionEngine Tests", () => {
  it("aligns speech transcript with audio buffer and calculates word timestamps", () => {
    const sampleRate = 44100;
    const duration = 3.0; // 3.0 seconds
    const totalFrames = Math.round(sampleRate * duration);
    const buf = AudioBuffer.create(1, totalFrames, sampleRate);

    const text = "GUADALAJARA ES FUEGO PURO";
    const result = SpeechRecognitionEngine.alignTranscriptWithAudio(text, buf, {
      wordsPerSegment: 2,
      emphasisWords: ["fuego"],
    });

    assert.equal(result.words.length, 4);
    assert.equal(result.words[0].word, "GUADALAJARA");
    assert.equal(result.words[2].word, "FUEGO");
    assert.equal(result.words[2].isEmphasis, true);

    // Segment clustering (2 words per segment)
    assert.equal(result.segments.length, 2);
    assert.equal(result.segments[0].text, "GUADALAJARA ES");
    assert.equal(result.segments[1].text, "FUEGO PURO");

    // Timestamps monotonically increasing
    assert.ok(result.words[0].start < result.words[0].end);
    assert.ok(result.words[0].end <= result.words[1].start);
    assert.ok(result.words[3].end <= 3.0);
  });

  it("converts to canonical CaptionDocument seamlessly", () => {
    const buf = AudioBuffer.create(1, 44100 * 2, 44100);
    const result = SpeechRecognitionEngine.alignTranscriptWithAudio("VIVA MEXICO", buf);
    const doc = SpeechRecognitionEngine.toCaptionDocument(result, "custom_doc_101");

    assert.equal(doc.id, "custom_doc_101");
    assert.equal(doc.timingPrecision, "word");
    assert.equal(doc.segments.length, 1);
    assert.equal(doc.segments[0].words.length, 2);
  });
});
