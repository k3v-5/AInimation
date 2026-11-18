import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AIDirector } from "../../ai-director/core/AIDirector.js";

describe("Fase 8 — AI Director Benchmark Suite", () => {
  it("benchmarks 500 full multi-agent directing sessions", async () => {
    const director = new AIDirector();
    const brief = {
      objective: "AI Benchmark Plan",
      platform: "tiktok" as const,
      targetDuration: 30.0,
      styleId: "fast-tiktok",
    };

    const t0 = performance.now();
    for (let i = 0; i < 500; i++) {
      await director.directSession(brief, { sessionId: `sess_${i}` });
    }
    const elapsed = performance.now() - t0;

    // Presupuesto: < 250ms para 500 sesiones multi-agente
    assert.ok(elapsed < 250, `Multi-agent directing took ${elapsed.toFixed(2)}ms (budget: <250ms)`);
  });
});
