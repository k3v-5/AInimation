import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  ORDERED_VLOG_PHASES,
  OrchestratorStateMachine,
} from "../../../vlog/orchestrator/orchestrator-state-machine.js";

describe("Milestone 8 — Orchestrator State Machine Suite", () => {
  it("initializes all 22 phases in PENDING state", () => {
    const sm = new OrchestratorStateMachine("proj_test", "run_test");
    const run = sm.getRun();

    assert.equal(run.projectId, "proj_test");
    assert.equal(run.state, "PENDING");
    assert.equal(run.phases.length, 22);
    assert.equal(run.currentPhase, "P00_INITIALIZE");

    for (let i = 0; i < 22; i++) {
      assert.equal(run.phases[i].phase, ORDERED_VLOG_PHASES[i]);
      assert.equal(run.phases[i].state, "PENDING");
    }
  });

  it("transitions smoothly through phases updating currentPhase and state", () => {
    const sm = new OrchestratorStateMachine("proj_test", "run_test");

    sm.startPhase("P00_INITIALIZE");
    assert.equal(sm.getState(), "RUNNING");
    assert.equal(sm.getCurrentPhase(), "P00_INITIALIZE");

    sm.completePhase("P00_INITIALIZE", ["art_01"]);
    // Debe haber avanzado a P01_VALIDATE_INPUT
    assert.equal(sm.getCurrentPhase(), "P01_VALIDATE_INPUT");
    assert.equal(sm.getRun().phases[0].state, "COMPLETED");
    assert.deepEqual(sm.getRun().phases[0].producedArtifactIds, ["art_01"]);
  });

  it("handles failure cleanly marking the phase and run as FAILED", () => {
    const sm = new OrchestratorStateMachine("proj_fail", "run_fail");

    sm.startPhase("P00_INITIALIZE");
    sm.completePhase("P00_INITIALIZE");

    sm.startPhase("P01_VALIDATE_INPUT");
    sm.failPhase("P01_VALIDATE_INPUT", "Invalid project assets");

    assert.equal(sm.getState(), "FAILED");
    const p01 = sm.getRun().phases.find((p) => p.phase === "P01_VALIDATE_INPUT");
    assert.equal(p01?.state, "FAILED");
    assert.equal(p01?.errorMessage, "Invalid project assets");
  });

  it("correctly identifies the next phase to resume after checkpoint", () => {
    const sm = new OrchestratorStateMachine("proj_resume", "run_resume");

    sm.startPhase("P00_INITIALIZE");
    sm.completePhase("P00_INITIALIZE");

    sm.startPhase("P02_INGEST_MEDIA"); // Supongamos que P01 ya se completó
    const phase01 = sm.getRun().phases.find((p) => p.phase === "P01_VALIDATE_INPUT")!;
    phase01.state = "COMPLETED";

    // El siguiente no completado debe ser P02
    assert.equal(sm.getResumePhase(), "P02_INGEST_MEDIA");
  });
});
