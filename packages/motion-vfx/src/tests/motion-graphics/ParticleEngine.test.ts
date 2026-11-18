import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ParticleEngine } from "../../motion-graphics/core/ParticleEngine.js";

describe("Fase 11 — Particle Engine Tests", () => {
  it("generates deterministic confetti particles and simulates trajectory over time", () => {
    const pT0 = ParticleEngine.generateParticles({ preset: "confetti", count: 20, seed: 99, duration: 2.0 }, 0);
    const pT1 = ParticleEngine.generateParticles({ preset: "confetti", count: 20, seed: 99, duration: 2.0 }, 1.0);

    assert.strictEqual(pT0.length, 20);
    assert.strictEqual(pT1.length, 20);

    // En t=0 la posición inicial en Y es 0
    assert.strictEqual(pT0[0].position.y, 0);

    // En t=1 la partícula se ha desplazado debido a velocidad y gravedad
    assert.ok(pT1[0].position.y !== 0);
    assert.ok(pT1[0].opacity < 1.0); // Opacidad disminuye con la edad
  });
});
