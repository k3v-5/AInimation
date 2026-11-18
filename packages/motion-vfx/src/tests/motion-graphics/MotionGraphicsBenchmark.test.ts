import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { CameraDynamicsEngine } from "../../motion-graphics/core/CameraDynamicsEngine.js";
import { KineticTypographyEngine } from "../../motion-graphics/core/KineticTypographyEngine.js";
import { MotionCompiler } from "../../motion-graphics/core/MotionCompiler.js";
import { ParticleEngine } from "../../motion-graphics/core/ParticleEngine.js";

describe("Fase 11 — Motion Graphics Benchmark Suite", () => {
  it("benchmarks 5,000 particle evaluations, 1,000 stagger calculations and 500 macro compilations", () => {
    // 1. Benchmark Particles (50 particles x 100 frames = 5,000 particle updates)
    const t0 = performance.now();
    for (let f = 0; f < 100; f++) {
      ParticleEngine.generateParticles({ preset: "confetti", count: 50, seed: 100, duration: 2.0 }, f / 30);
    }
    const partElapsed = performance.now() - t0;

    // 2. Benchmark Kinetic Typography Staggers (1,000 segmentations)
    const t1 = performance.now();
    for (let i = 0; i < 1000; i++) {
      KineticTypographyEngine.segmentText("ESTO ES UNA PRUEBA CINÉTICA DE RENDIMIENTO", {
        direction: "center",
        emphasizedWords: ["PRUEBA", "RENDIMIENTO"],
      });
    }
    const stagElapsed = performance.now() - t1;

    // 3. Benchmark Motion Macro Compilations (500 compilations)
    const t2 = performance.now();
    for (let i = 0; i < 500; i++) {
      MotionCompiler.compileMacro("high-impact-hook", { text: "HOOK TEST", accentWord: "TEST" });
    }
    const macroElapsed = performance.now() - t2;

    // Presupuestos: < 100ms para cada tarea
    assert.ok(partElapsed < 100, `Particles took ${partElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(stagElapsed < 100, `Staggers took ${stagElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(macroElapsed < 100, `Macro compilations took ${macroElapsed.toFixed(2)}ms (budget: <100ms)`);
  });
});
