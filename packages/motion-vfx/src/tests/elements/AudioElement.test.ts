import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AudioElement } from "../../elements/AudioElement.js";

describe("Fase 2B — AudioElement & Volume Animation Tests", () => {
  it("animates audio volume using Property<number> for fade-out effects", () => {
    const audio = new AudioElement({
      assetId: "bg_music",
      startTime: 0,
      duration: 10,
      sourceStartTime: 30,
    });

    // Fade out de 8s a 10s
    audio.volume.setValue(1);
    audio.volume.addKeyframe(8, 1, "linear");
    audio.volume.addKeyframe(10, 0);

    const evalAt5 = audio.evaluate(5);
    assert.strictEqual(evalAt5.active, true);
    assert.strictEqual(evalAt5.volume, 1);
    assert.strictEqual(evalAt5.sourceTime, 35);

    const evalAt9 = audio.evaluate(9);
    assert.strictEqual(evalAt9.volume, 0.5);

    const evalAt10 = audio.evaluate(10);
    assert.strictEqual(evalAt10.active, false); // [0, 10)
    assert.strictEqual(evalAt10.volume, 0);
  });
});
