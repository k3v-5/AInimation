import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { SoundDesignMacroEngine } from "../../audio-design/core/SoundDesignMacroEngine.js";
import { SyncEventGraph } from "../../audio-design/core/SyncEventGraph.js";

describe("Fase 13 — Sync Event Graph & Sound Macros Tests", () => {
  it("creates sync groups unifying visual impact, camera punch and audio triggers", () => {
    const graph = new SyncEventGraph();
    const group = graph.createSyncGroup("sync_01", 1.5, "Hook Emphasis Point", [
      { time: 1.5, type: "text_pop", strength: 1.0, source: "motion" },
      { time: 1.5, type: "camera_punch", strength: 0.8, source: "motion" },
      { time: 1.5, type: "sfx_trigger", strength: 0.9, source: "audio" },
    ]);

    assert.strictEqual(group.events.length, 3);
    const events = graph.getEventsAt(1.5);
    assert.strictEqual(events.length, 3);
  });

  it("resolves sound design macros into concrete SFX and ducking amounts", () => {
    const hookMacro = SoundDesignMacroEngine.resolveMacro("social-hook");
    assert.strictEqual(hookMacro.macro.sfxCategory, "impact");
    assert.strictEqual(hookMacro.macro.duckAmount, 0.4);
    assert.strictEqual(hookMacro.sfxId, "sfx_impact_deep");
  });
});
