import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { SRTParser } from "../../captions/transcript/SRTParser.js";
import { WhisperJSONParser } from "../../captions/transcript/WhisperJSONParser.js";
import { CaptionParseError } from "../../errors/index.js";

describe("Fase 16 — SRT Parser Tests", () => {
  it("parses standard SRT with multiple cues, multiline text and CRLF line endings", () => {
    const srt = "1\r\n00:00:01,000 --> 00:00:03,000\r\nHola mundo\r\nsegunda línea\r\n\r\n2\r\n00:00:03,500 --> 00:00:05,200\r\nSubtítulo final";
    const doc = SRTParser.parse(srt, "test_doc");

    assert.equal(doc.id, "test_doc");
    assert.equal(doc.segments.length, 2);

    assert.equal(doc.segments[0].start, 1.0);
    assert.equal(doc.segments[0].end, 3.0);
    assert.equal(doc.segments[0].text, "Hola mundo segunda línea");
    assert.equal(doc.segments[0].words.length, 4);

    assert.equal(doc.segments[1].start, 3.5);
    assert.equal(doc.segments[1].end, 5.2);
    assert.equal(doc.segments[1].words.length, 2);
    assert.equal(doc.duration, 5.2);
  });

  it("handles UTF-8 BOM, extra whitespace and sorts out-of-order cues", () => {
    const srt = "\uFEFF2\n00:00:04,000 --> 00:00:06,000\nSegundo bloque\n\n1\n00:00:01,000 --> 00:00:03,000\nPrimer bloque";
    const doc = SRTParser.parse(srt);

    assert.equal(doc.segments.length, 2);
    assert.equal(doc.segments[0].id, "seg_0");
    assert.equal(doc.segments[0].text, "Primer bloque");
    assert.equal(doc.segments[1].id, "seg_1");
    assert.equal(doc.segments[1].text, "Segundo bloque");
  });

  it("handles empty or whitespace-only SRT gracefully returning 0 segments", () => {
    const doc = SRTParser.parse("   \n\r\n   ");
    assert.equal(doc.segments.length, 0);
    assert.equal(doc.duration, 0);
  });

  it("throws CaptionParseError on invalid timestamp format", () => {
    const badSrt = "1\n00:00:01 --> invalid_time\nTexto";
    assert.throws(() => SRTParser.parse(badSrt), CaptionParseError);
  });

  it("throws CaptionParseError when cue end <= start", () => {
    const badSrt = "1\n00:00:05,000 --> 00:00:02,000\nTiempo invertido";
    assert.throws(() => SRTParser.parse(badSrt), (err: any) => {
      assert.match(err.message, /must be strictly greater than start time/);
      return true;
    });
  });
});

describe("Fase 16 — Whisper JSON Parser Tests", () => {
  it("parses valid Whisper JSON with detailed word timestamps and confidence", () => {
    const whisperObj = {
      language: "es",
      segments: [
        {
          id: 0,
          start: 0.5,
          end: 2.5,
          text: "Edición viral con IA",
          words: [
            { word: "Edición", start: 0.5, end: 1.0, probability: 0.98 },
            { word: "viral", start: 1.0, end: 1.6, probability: 0.95 },
            { word: "con", start: 1.6, end: 1.9, probability: 0.99 },
            { word: "IA", start: 1.9, end: 2.5, probability: 0.92 },
          ],
        },
      ],
    };

    const doc = WhisperJSONParser.parse(whisperObj, "whisper_test");
    assert.equal(doc.id, "whisper_test");
    assert.equal(doc.segments.length, 1);
    assert.equal(doc.segments[0].words.length, 4);
    assert.equal(doc.segments[0].words[0].text, "Edición");
    assert.equal(doc.segments[0].words[0].confidence, 0.98);
    assert.equal(doc.segments[0].words[1].start, 1.0);
    assert.equal(doc.segments[0].words[3].end, 2.5);
  });

  it("falls back to uniform word distribution if segment has no words array", () => {
    const whisperObj = {
      segments: [
        {
          start: 1.0,
          end: 3.0,
          text: "Tres palabras simples",
        },
      ],
    };

    const doc = WhisperJSONParser.parse(whisperObj);
    assert.equal(doc.segments.length, 1);
    assert.equal(doc.segments[0].words.length, 3);
    assert.equal(doc.segments[0].words[0].start, 1.0);
    assert.equal(doc.segments[0].words[2].end, 3.0);
  });

  it("throws CaptionParseError on invalid JSON string", () => {
    assert.throws(() => WhisperJSONParser.parse("{ invalid json"), CaptionParseError);
  });

  it("throws CaptionParseError on negative start time or end <= start", () => {
    const badWhisper = {
      segments: [{ start: -1.0, end: 2.0, text: "Negativo" }],
    };
    assert.throws(() => WhisperJSONParser.parse(badWhisper), CaptionParseError);
  });
});
