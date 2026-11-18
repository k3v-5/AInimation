import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { createDistributedJob, computeDistributedJobHash } from "../../distributed/core/DistributedJob.js";
import { createTaskDefinition, computeTaskHash } from "../../distributed/tasks/TaskDefinition.js";
import { createTaskLease } from "../../distributed/tasks/TaskLease.js";
import { createTaskResult } from "../../distributed/tasks/TaskResult.js";
import { createAgentProposal } from "../../distributed/swarm/AgentProposal.js";
import { createAgentMessage } from "../../distributed/swarm/AgentMessage.js";

describe("Fase 24 — Capa 1: Distributed Job, Tasks & Swarm Models Tests", () => {
  it("creates a DistributedJob with deterministic identity and hash", () => {
    const job = createDistributedJob({
      jobId: "djob_test_01",
      projectId: "proj_01",
      briefHash: "hash_brief_abc",
      baselineRevisionId: "rev_01",
      allocatedWorkers: 4,
    });

    assert.equal(job.jobId, "djob_test_01");
    assert.equal(job.status, "created");
    assert.equal(job.allocatedWorkers, 4);
    assert.equal(typeof job.deterministicHash, "string");
    assert.equal(job.deterministicHash.length, 64);
  });

  it("creates a TaskDefinition with deterministic hash and idempotencyKey", () => {
    const taskA = createTaskDefinition({
      taskId: "task_01",
      jobId: "djob_01",
      type: "plan_story",
      dependencies: ["dep_b", "dep_a"],
      payload: { key: "val" },
    });

    const taskB = createTaskDefinition({
      taskId: "task_01",
      jobId: "djob_01",
      type: "plan_story",
      dependencies: ["dep_a", "dep_b"], // permutado
      payload: { key: "val" },
    });

    // Hashes deben ser idénticos independientemente del orden de entrada de dependencias
    assert.equal(taskA.deterministicHash, taskB.deterministicHash);
    assert.equal(taskA.idempotencyKey, taskB.idempotencyKey);
  });

  it("creates a TaskLease with deterministic leaseId and expiration ticks", () => {
    const lease = createTaskLease({
      taskId: "task_01",
      workerId: "worker_01",
      attemptNumber: 1,
      acquiredAtLogical: 10,
      leaseDurationTicks: 5,
    });

    assert.ok(lease.leaseId.startsWith("lease_"));
    assert.equal(lease.expiresAtLogical, 15);
    assert.equal(lease.active, true);
    assert.equal(typeof lease.deterministicHash, "string");
  });

  it("creates TaskResult and AgentProposal with validated hashes", () => {
    const res = createTaskResult({
      taskId: "task_01",
      workerId: "worker_01",
      success: true,
      outputPayload: { out: 123 },
    });

    assert.equal(res.success, true);
    assert.equal(res.durationTicks, 1);

    const prop = createAgentProposal({
      proposalId: "prop_01",
      agentRole: "motion",
      baseRevisionId: "rev_01",
      changeSet: {
        changeSetId: "cs_01",
        description: "add motion",
        operations: [{ type: "set-property", targetId: "elem_1", property: "opacity", value: 1 }],
      },
      rationale: "Optimized motion dynamics",
    });

    assert.equal(prop.agentRole, "motion");
    assert.equal(prop.confidence, 1.0);
    assert.equal(typeof prop.deterministicHash, "string");
  });
});
