import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Scene } from "../../scenes/core/Scene.js";
import { SceneSequence } from "../../scenes/core/SceneSequence.js";
import { registerBuiltinTransitions } from "../../transitions/builtins/index.js";

describe("Fase 5C — Scene Sequence & Transition Overlap Pipeline Tests", () => {
  registerBuiltinTransitions();

  it("calculates transition overlap window and evaluates active states correctly", () => {
    const sequence = new SceneSequence();

    const sceneA = new Scene({ id: "scene_a", duration: 5.0, metadata: { semanticRole: "hook" } });
    const sceneB = new Scene({ id: "scene_b", duration: 5.0, metadata: { semanticRole: "explanation" } });

    // Transición de 1.0s de A hacia B
    sequence.addScene(sceneA, { type: "crossfade", duration: 1.0 });
    sequence.addScene(sceneB);

    // Duración total = 5 + 5 - 1 = 9s
    assert.strictEqual(sequence.getTotalDuration(), 9.0);

    const ranges = sequence.calculateTimelineRanges();
    // Scene A: [0, 5)
    assert.strictEqual(ranges[0].start, 0);
    assert.strictEqual(ranges[0].end, 5);

    // Scene B: [4, 9)
    assert.strictEqual(ranges[1].start, 4);
    assert.strictEqual(ranges[1].end, 9);

    // 1. En t = 2.0s -> solo Scene A activa
    const stateAt2 = sequence.evaluate(2.0);
    assert.strictEqual(stateAt2.activeScenes.length, 1);
    assert.strictEqual(stateAt2.activeScenes[0].scene.id, "scene_a");
    assert.strictEqual(stateAt2.activeScenes[0].localTime, 2.0);
    assert.strictEqual(stateAt2.transition, undefined);

    // 2. En t = 4.5s -> en plena transición entre A y B
    const stateAt45 = sequence.evaluate(4.5);
    assert.strictEqual(stateAt45.activeScenes.length, 2);
    assert.strictEqual(stateAt45.activeScenes[0].scene.id, "scene_a");
    assert.strictEqual(stateAt45.activeScenes[0].localTime, 4.5);
    assert.strictEqual(stateAt45.activeScenes[1].scene.id, "scene_b");
    assert.strictEqual(stateAt45.activeScenes[1].localTime, 0.5); // 4.5 - 4.0

    assert.ok(stateAt45.transition !== undefined);
    assert.strictEqual(stateAt45.transition?.type, "crossfade");
    assert.strictEqual(stateAt45.transition?.rawProgress, 0.5);
    assert.strictEqual(stateAt45.transition?.result.fromOpacity, 0.5);
    assert.strictEqual(stateAt45.transition?.result.toOpacity, 0.5);

    // 3. En t = 7.0s -> solo Scene B activa
    const stateAt7 = sequence.evaluate(7.0);
    assert.strictEqual(stateAt7.activeScenes.length, 1);
    assert.strictEqual(stateAt7.activeScenes[0].scene.id, "scene_b");
    assert.strictEqual(stateAt7.activeScenes[0].localTime, 3.0);
    assert.strictEqual(stateAt7.transition, undefined);
  });
});
