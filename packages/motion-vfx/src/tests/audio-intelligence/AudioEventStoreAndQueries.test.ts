import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AudioEventStore } from "../../audio-intelligence/core/AudioEventStore.js";
import { AudioEvent } from "../../audio-intelligence/types/index.js";

describe("Fase 5I — Audio Event Store & Range Queries Tests", () => {
  it("indexes audio events and queries by timestamp tolerance, time range and event type", () => {
    const store = new AudioEventStore();

    const e1: AudioEvent = { id: "e_beat_1", type: "beat", time: 1.0, strength: 0.9 };
    const e2: AudioEvent = { id: "e_word_1", type: "word", time: 1.2, metadata: { text: "hola" } };
    const e3: AudioEvent = { id: "e_beat_2", type: "beat", time: 2.0, strength: 0.8 };
    const e4: AudioEvent = { id: "e_onset_1", type: "onset", time: 3.5, strength: 1.0 };

    store.addEvent(e1).addEvent(e2).addEvent(e3).addEvent(e4);

    assert.strictEqual(store.size, 4);

    // Consulta en rango [0.8, 1.5] -> e1 y e2
    const rangeEvents = store.getBetween(0.8, 1.5);
    assert.strictEqual(rangeEvents.length, 2);

    // Consulta por tipo 'beat' -> e1 y e3
    const beatEvents = store.getByType("beat");
    assert.strictEqual(beatEvents.length, 2);

    // Búsqueda del evento más cercano a t = 1.95s -> e3 (en t=2.0)
    const nearest = store.findNearest(1.95);
    assert.strictEqual(nearest?.id, "e_beat_2");
  });
});
