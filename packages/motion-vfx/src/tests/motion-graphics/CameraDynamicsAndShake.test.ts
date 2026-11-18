import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { CameraDynamicsEngine } from "../../motion-graphics/core/CameraDynamicsEngine.js";

describe("Fase 11 — 2D Camera Dynamics & Seeded Shake Tests", () => {
  it("evaluates snap zoom and subtle push with predictable progressive scales", () => {
    // 1. Subtle Push
    const pushT0 = CameraDynamicsEngine.evaluateCamera({ mode: "subtlePush", intensity: 1.0, duration: 2.0 }, 0);
    const pushT2 = CameraDynamicsEngine.evaluateCamera({ mode: "subtlePush", intensity: 1.0, duration: 2.0 }, 2.0);

    assert.strictEqual(pushT0.scale, 1.0);
    assert.strictEqual(Math.abs(pushT2.scale - 1.08) < 1e-6, true);

    // 2. Snap Zoom
    const snapT0 = CameraDynamicsEngine.evaluateCamera({ mode: "snapZoom", intensity: 1.0, duration: 1.0 }, 0);
    assert.strictEqual(snapT0.scale, 1.15);
  });

  it("produces 100% deterministic camera shake given identical random seeds", () => {
    const shakeA = CameraDynamicsEngine.evaluateCamera({ mode: "shake", intensity: 0.8, seed: 1234, duration: 1.0 }, 0.5);
    const shakeB = CameraDynamicsEngine.evaluateCamera({ mode: "shake", intensity: 0.8, seed: 1234, duration: 1.0 }, 0.5);

    assert.strictEqual(shakeA.position.x, shakeB.position.x);
    assert.strictEqual(shakeA.position.y, shakeB.position.y);
    assert.strictEqual(shakeA.rotation, shakeB.rotation);
  });
});
