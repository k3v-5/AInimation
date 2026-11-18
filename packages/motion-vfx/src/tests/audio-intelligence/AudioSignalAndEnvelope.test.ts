import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AudioSignal } from "../../audio-intelligence/core/AudioSignal.js";

describe("Fase 5I — Audio Signal & Envelope Follower Tests", () => {
  it("interpolates continuous values linearly between discrete audio samples", () => {
    const signal = new AudioSignal("rms_energy", [
      { time: 0.0, value: 0.0 },
      { time: 2.0, value: 1.0 },
    ]);

    // En t = 1.0s (punto medio) -> valor = 0.5
    assert.strictEqual(signal.sample(1.0), 0.5);
    // Fuera de límites se mantiene en extremos
    assert.strictEqual(signal.sample(-1.0), 0.0);
    assert.strictEqual(signal.sample(3.0), 1.0);
  });

  it("applies attack and release envelope smoothing to raw transient spikes", () => {
    // Señal con un pico instantáneo en t = 0.5s
    const signal = new AudioSignal("snare_spike", [
      { time: 0.0, value: 0.0 },
      { time: 0.5, value: 1.0 },
      { time: 0.6, value: 0.0 },
      { time: 2.0, value: 0.0 },
    ]);

    const envelopeValue = signal.sampleEnvelope(0.7, 0.05, 0.3);
    // Debido al release lento, en t=0.7s (después del pico de 0.5s) todavía debe mantener energía > 0.1
    assert.ok(envelopeValue > 0.1);
  });
});
