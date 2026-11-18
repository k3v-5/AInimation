import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  OrchestratorStateMachine,
  VlogMultilingualProductionOrchestrator,
} from "../../../vlog/index.js";

describe("Milestone 9 — Failure Injection & Recovery Suite", () => {
  it("safely intercepts empty script input and reports graceful failure in P01", async () => {
    const result = await VlogMultilingualProductionOrchestrator.execute({
      projectId: "proj_err",
      sourceLocale: "es-MX",
      targetLocales: ["en-US"],
      scriptText: "   ", // Solo espacios -> debe fallar de inmediato
      assets: [],
    });

    assert.equal(result.isSuccess, false);
    assert.equal(result.run.state, "FAILED");
    assert.equal(result.run.currentPhase, "P01_VALIDATE_INPUT");
    assert.equal(result.manifest.validation.passed, false);
  });

  it("recovers and identifies resume phase after simulated crash at P12", () => {
    const sm = new OrchestratorStateMachine("proj_crash", "run_crash");

    // Simular que las fases P00 a P11 se completaron con éxito
    const phasesToComplete = [
      "P00_INITIALIZE",
      "P01_VALIDATE_INPUT",
      "P02_INGEST_MEDIA",
      "P03_ANALYZE_MEDIA",
      "P04_CLASSIFY_FOOTAGE",
      "P05_TRANSCRIBE",
      "P06_ANALYZE_NARRATIVE",
      "P07_BUILD_SOURCE_TIMELINE",
      "P08_GENERATE_JUMP_CUTS",
      "P09_MATCH_BROLL",
      "P10_PLAN_LANGUAGES",
      "P11_GENERATE_TTS",
    ] as const;

    for (const p of phasesToComplete) {
      sm.startPhase(p);
      sm.completePhase(p);
    }

    // P12_ADAPTIVE_PACING falló
    sm.startPhase("P12_ADAPTIVE_PACING");
    sm.failPhase("P12_ADAPTIVE_PACING", "Simulated out of memory error");

    // Verificar que el gestor de recuperación señala reanudar desde P12
    assert.equal(sm.getState(), "FAILED");
    assert.equal(sm.getResumePhase(), "P12_ADAPTIVE_PACING");
  });
});
