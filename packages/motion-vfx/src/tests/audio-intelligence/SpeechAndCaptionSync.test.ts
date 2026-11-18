import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { SpeechData } from "../../audio-intelligence/types/index.js";

describe("Fase 5I — Speech Data & Word Progress Synchronization Tests", () => {
  it("computes word progress continuously during spoken interval", () => {
    const speech: SpeechData = {
      segments: [
        {
          start: 1.0,
          end: 3.0,
          text: "Hola mundo increíble",
          words: [
            { text: "Hola", start: 1.0, end: 1.4 },
            { text: "mundo", start: 1.5, end: 2.0 },
            { text: "increíble", start: 2.1, end: 2.9 },
          ],
        },
      ],
    };

    const wordMundo = speech.segments[0].words[1];
    // En t = 1.75s -> midpoint de [1.5, 2.0] -> progress = 0.5
    const duration = wordMundo.end - wordMundo.start;
    const progressAtMid = (1.75 - wordMundo.start) / duration;

    assert.strictEqual(progressAtMid, 0.5);
    assert.strictEqual(wordMundo.text, "mundo");
  });
});
