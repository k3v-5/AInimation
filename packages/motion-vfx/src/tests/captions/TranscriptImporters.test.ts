import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TranscriptParser } from "../../captions/transcript/TranscriptParser.js";

describe("Fase 5E — Transcript Importers (Whisper, SRT, VTT) Tests", () => {
  it("imports transcripts from Whisper verbose JSON with word timestamps", () => {
    const whisperJson = {
      language: "es",
      segments: [
        {
          id: 0,
          start: 0.0,
          end: 1.5,
          text: "Hola a todos",
          words: [
            { word: "Hola", start: 0.0, end: 0.4, probability: 0.99 },
            { word: "a", start: 0.4, end: 0.6, probability: 0.98 },
            { word: "todos", start: 0.6, end: 1.5, probability: 0.96 },
          ],
        },
      ],
    };

    const transcript = TranscriptParser.fromWhisperJSON(whisperJson);
    assert.strictEqual(transcript.segments.length, 1);
    assert.strictEqual(transcript.segments[0].words?.length, 3);
    assert.strictEqual(transcript.segments[0].words[0].text, "Hola");
    assert.strictEqual(transcript.segments[0].words[2].end, 1.5);
  });

  it("imports transcripts from standard SRT subtitle file string", () => {
    const srt = `1\n00:00:01,000 --> 00:00:03,000\nPrimer subtitulo aqui\n\n2\n00:00:04,000 --> 00:00:06,500\nSegundo bloque de texto`;

    const transcript = TranscriptParser.fromSRT(srt);
    assert.strictEqual(transcript.segments.length, 2);

    assert.strictEqual(transcript.segments[0].start, 1.0);
    assert.strictEqual(transcript.segments[0].end, 3.0);
    assert.strictEqual(transcript.segments[0].text, "Primer subtitulo aqui");
    assert.strictEqual(transcript.segments[0].words?.length, 3);

    assert.strictEqual(transcript.segments[1].start, 4.0);
    assert.strictEqual(transcript.segments[1].end, 6.5);
  });

  it("imports transcripts from WebVTT subtitle format", () => {
    const vtt = `WEBVTT\n\n00:00:00.500 --> 00:00:02.000\nTexto WebVTT de prueba`;

    const transcript = TranscriptParser.fromVTT(vtt);
    assert.strictEqual(transcript.segments.length, 1);
    assert.strictEqual(transcript.segments[0].start, 0.5);
    assert.strictEqual(transcript.segments[0].end, 2.0);
    assert.strictEqual(transcript.segments[0].words?.length, 4);
  });
});
