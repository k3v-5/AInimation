import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AutoSFXSoundDesignEngine, VisualTrigger } from "../../audio/mixer/AutoSFXSoundDesignEngine.js";

describe("Audio — AutoSFXSoundDesignEngine Tests", () => {
  it("maps visual triggers to corresponding sound effects accurately", () => {
    const triggers: VisualTrigger[] = [
      { type: "transition", time: 2.4 },
      { type: "text_pop", time: 4.8 },
      { type: "hud_element", time: 0.5 },
    ];

    const sfxEvents = AutoSFXSoundDesignEngine.mapVisualsToSFX(triggers);

    assert.equal(sfxEvents.length, 3);
    assert.equal(sfxEvents[0].type, "whoosh");
    assert.ok(sfxEvents[0].time < 2.4, "Expected whoosh to start slightly before transition");
    assert.equal(sfxEvents[1].type, "impact_boom");
    assert.equal(sfxEvents[2].type, "ui_tick");
  });

  it("generates continuous auto-ducking gain envelope during high-energy impacts", () => {
    const sfxEvents = [
      { id: "sfx_1", time: 2.0, type: "impact_boom" as const, volumeDb: 0, duration: 0.5 },
    ];

    const ducking = AutoSFXSoundDesignEngine.generateDuckingEnvelope(sfxEvents, 10.0, -4.0, 0.2);

    assert.ok(ducking.length >= 4);
    assert.equal(ducking[0].gainDb, 0);

    const minGain = Math.min(...ducking.map((d) => d.gainDb));
    assert.equal(minGain, -4.0);

    const lastPoint = ducking[ducking.length - 1];
    assert.equal(lastPoint.time, 10.0);
    assert.equal(lastPoint.gainDb, 0);
  });
});
