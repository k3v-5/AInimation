import assert from "node:assert/strict";
import { describe, it, beforeEach } from "node:test";
import { MemoryProjectStore } from "../../persistence/MemoryProjectStore.js";
import { ProjectFile } from "../../persistence/schemas/project.schema.js";
import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";
import { RevisionManager } from "../../revisions/RevisionManager.js";
import { WorkflowContext } from "../../workflows/WorkflowContext.js";
import { WorkflowDefinition } from "../../workflows/WorkflowDefinition.js";
import { WorkflowEngine } from "../../workflows/WorkflowEngine.js";
import { StepRegistry } from "../../workflows/WorkflowStep.js";

describe("Fase 18 — Workflow Engine, Checkpoints & Recovery Tests", () => {
  let store: MemoryProjectStore;
  let revManager: RevisionManager;
  let engine: WorkflowEngine;

  beforeEach(async () => {
    store = new MemoryProjectStore();
    revManager = new RevisionManager(store);
    engine = new WorkflowEngine();

    const initialProject = {
      schemaVersion: "1.8.0",
      composition: { duration: 10, fps: 30 },
      elements: [],
      assets: [],
    };

    const projectFile: ProjectFile = {
      schemaVersion: "1.8.0",
      engineVersion: "1.8.0",
      projectId: "proj_wf_test",
      headRevisionId: "rev_0",
      metadata: { name: "Workflow Test" },
      project: initialProject,
      contentHash: ProjectSerializer.hashCanonical(initialProject),
    };

    await store.create(projectFile);
  });

  it("executes steps in DAG topological order and retries transient failures", async () => {
    const executionLog: string[] = [];
    let step2Attempts = 0;

    StepRegistry.register("STEP_A", async (ctx) => {
      executionLog.push("STEP_A");
      ctx.set("data_a", 100);
      return { ok: true };
    });

    StepRegistry.register("STEP_B_RETRY", async (ctx) => {
      executionLog.push("STEP_B");
      step2Attempts++;
      if (step2Attempts < 2) {
        throw new Error("Temporary network glitch");
      }
      ctx.set("data_b", 200);
      return { ok: true };
    });

    StepRegistry.register("STEP_C_DEPENDENT", async (ctx) => {
      executionLog.push("STEP_C");
      const a = ctx.get<number>("data_a");
      const b = ctx.get<number>("data_b");
      return { sum: (a ?? 0) + (b ?? 0) };
    });

    const definition: WorkflowDefinition = {
      id: "wf_dag_test",
      version: "1.0.0",
      steps: [
        { id: "step_c", type: "STEP_C_DEPENDENT", dependsOn: ["step_a", "step_b"], retryPolicy: { maxAttempts: 1, strategy: "none", intervalMs: 0 }, idempotent: true },
        { id: "step_b", type: "STEP_B_RETRY", dependsOn: ["step_a"], retryPolicy: { maxAttempts: 3, strategy: "fixed", intervalMs: 10 }, idempotent: true },
        { id: "step_a", type: "STEP_A", dependsOn: [], retryPolicy: { maxAttempts: 1, strategy: "none", intervalMs: 0 }, idempotent: true },
      ],
    };

    const context = new WorkflowContext({
      workflowId: "wf_dag_test",
      projectId: "proj_wf_test",
      revisionId: "rev_0",
      store,
      revisionManager: revManager,
    });

    const result = await engine.executeWorkflow({ definition, context });

    assert.equal(result.status, "completed");
    assert.deepEqual(executionLog, ["STEP_A", "STEP_B", "STEP_B", "STEP_C"]);
    assert.equal(result.completedSteps.length, 3);
    assert.equal(step2Attempts, 2);
  });

  it("persists checkpoints after each step and resumes from the last valid checkpoint upon recovery", async () => {
    const executedSteps: string[] = [];

    StepRegistry.register("STEP_1", async (ctx) => {
      executedSteps.push("STEP_1");
      ctx.set("stage1", "done");
      return { s1: true };
    });

    StepRegistry.register("STEP_2", async (ctx) => {
      executedSteps.push("STEP_2");
      ctx.set("stage2", "done");
      return { s2: true };
    });

    StepRegistry.register("STEP_3_FAIL_FIRST", async (ctx) => {
      executedSteps.push("STEP_3");
      const shouldFail = ctx.get<boolean>("should_fail");
      if (shouldFail) {
        throw new Error("Simulated process crash");
      }
      ctx.set("stage3", "done");
      return { s3: true };
    });

    StepRegistry.register("STEP_4", async (ctx) => {
      executedSteps.push("STEP_4");
      return { s4: true };
    });

    const definition: WorkflowDefinition = {
      id: "wf_checkpoint_test",
      version: "1.0.0",
      steps: [
        { id: "s1", type: "STEP_1", dependsOn: [], retryPolicy: { maxAttempts: 1, strategy: "none", intervalMs: 0 }, idempotent: true },
        { id: "s2", type: "STEP_2", dependsOn: ["s1"], retryPolicy: { maxAttempts: 1, strategy: "none", intervalMs: 0 }, idempotent: true },
        { id: "s3", type: "STEP_3_FAIL_FIRST", dependsOn: ["s2"], retryPolicy: { maxAttempts: 1, strategy: "none", intervalMs: 0 }, idempotent: true },
        { id: "s4", type: "STEP_4", dependsOn: ["s3"], retryPolicy: { maxAttempts: 1, strategy: "none", intervalMs: 0 }, idempotent: true },
      ],
    };

    const context = new WorkflowContext({
      workflowId: "wf_checkpoint_test",
      projectId: "proj_wf_test",
      revisionId: "rev_0",
      store,
      revisionManager: revManager,
      initialVariables: { should_fail: true },
    });

    // First run: fails on step 3
    const firstResult = await engine.executeWorkflow({ definition, context });
    assert.equal(firstResult.status, "failed");
    assert.deepEqual(firstResult.completedSteps, ["s1", "s2"]);
    assert.deepEqual(executedSteps, ["STEP_1", "STEP_2", "STEP_3"]);

    // Verify checkpoints: should have checkpoints for s1 and s2
    const checkpoints = engine.getCheckpointManager().getCheckpoints("wf_checkpoint_test");
    assert.equal(checkpoints.length, 2);
    assert.equal(checkpoints[1].stepId, "s2");

    // Recovery & Resume: fix the condition and resume
    context.set("should_fail", false);
    executedSteps.length = 0; // reset trace

    const resumeResult = await engine.resumeWorkflow({ definition, context });

    assert.equal(resumeResult.status, "completed");
    assert.deepEqual(resumeResult.completedSteps, ["s1", "s2", "s3", "s4"]);
    // Crucial check: STEP_1 and STEP_2 were NOT re-executed!
    assert.deepEqual(executedSteps, ["STEP_3", "STEP_4"]);
  });

  it("handles cooperative workflow cancellation cleanly", async () => {
    StepRegistry.register("STEP_LONG_1", async () => ({ ok: true }));
    StepRegistry.register("STEP_LONG_2", async () => ({ ok: true }));

    const definition: WorkflowDefinition = {
      id: "wf_cancel_test",
      version: "1.0.0",
      steps: [
        { id: "step_1", type: "STEP_LONG_1", dependsOn: [], retryPolicy: { maxAttempts: 1, strategy: "none", intervalMs: 0 }, idempotent: true },
        { id: "step_2", type: "STEP_LONG_2", dependsOn: ["step_1"], retryPolicy: { maxAttempts: 1, strategy: "none", intervalMs: 0 }, idempotent: true },
      ],
    };

    const context = new WorkflowContext({
      workflowId: "wf_cancel_test",
      projectId: "proj_wf_test",
      revisionId: "rev_0",
      store,
      revisionManager: revManager,
    });

    // Request cancellation before execution starts
    engine.cancelWorkflow("wf_cancel_test");

    const result = await engine.executeWorkflow({ definition, context });
    assert.equal(result.status, "cancelled");
    assert.equal(engine.getWorkflowState("wf_cancel_test"), "cancelled");
  });
});
