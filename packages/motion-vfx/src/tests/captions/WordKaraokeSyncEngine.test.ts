import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { WordKaraokeSyncEngine } from "../../captions/animations/WordKaraokeSyncEngine.js";
import { RecognizedWord } from "../../captions/intelligence/SpeechRecognitionEngine.js";

describe("Captions — WordKaraokeSyncEngine Tests", () => {
  it("generates well-formed karaoke snippet with character range selectors", () => {
    const words: RecognizedWord[] = [
      { word: "RETUMBA", start: 0.5, end: 1.0, confidence: 0.95, isEmphasis: true },
      { word: "EL", start: 1.0, end: 1.2, confidence: 0.98 },
      { word: "PECHO", start: 1.2, end: 1.8, confidence: 0.96 },
    ];

    const snippet = WordKaraokeSyncEngine.generateKaraokeSegmentSnippet(
      "comp",
      "Karaoke_Retumba_01",
      words,
      [540, 960],
      {
        fontSize: 120,
        activeColor: [1.0, 0.78, 0.10],
      }
    );

    assert.ok(snippet.includes('var txtLayer = comp.layers.addText("RETUMBA EL PECHO")'));
    assert.ok(snippet.includes('txtLayer.startTime = 0.5'));
    assert.ok(snippet.includes('txtLayer.outPoint = 1.95'));
    assert.ok(snippet.includes('tDoc.fontSize = 120'));
    assert.ok(snippet.includes('ADBE Text Animator'));
    assert.ok(snippet.includes('Karaoke_Highlight'));
    assert.ok(snippet.includes('selector.property("Offset").setValueAtTime(0.5, -100)'));
    assert.ok(snippet.includes('selector.property("Offset").setValueAtTime(1.8, 100)'));
  });
});
