import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { SwarmCoordinator } from "../../distributed/swarm/SwarmCoordinator.js";
import { createAgentProposal } from "../../distributed/swarm/AgentProposal.js";
import { ThreeWayMergeArbiter } from "../../distributed/swarm/ThreeWayMergeArbiter.js";
import { createTaskDefinition } from "../../distributed/tasks/TaskDefinition.js";
import { ProposalConflictError } from "../../distributed/core/DistributedErrors.js";

describe("Fase 24 — Capa 3: Swarm Coordination & Three-Way Merge Tests", () => {
  it("SwarmCoordinator dispatches tasks to specialized agents and records messages", async () => {
    const coordinator = new SwarmCoordinator();
    const task = createTaskDefinition({
      taskId: "task_editor_01",
      jobId: "job_01",
      type: "edit_timeline",
      requiredRole: "editor",
    });

    const proposal = await coordinator.dispatchTask(task, "rev_01");

    assert.equal(proposal.agentRole, "editor");
    assert.equal(proposal.baseRevisionId, "rev_01");
    assert.ok(proposal.changeSet.operations.length > 0);
    assert.equal(coordinator.messages.length, 2); // task_assigned + proposal_submitted
  });

  it("ThreeWayMergeArbiter merges orthogonal non-conflicting proposals", () => {
    const propDirector = createAgentProposal({
      proposalId: "prop_dir",
      agentRole: "director",
      baseRevisionId: "rev_01",
      changeSet: {
        changeSetId: "cs_dir",
        description: "Director changes",
        operations: [{ type: "set-metadata", targetId: "meta_1", property: "title", value: "My Video" }],
      },
      rationale: "Set title",
    });

    const propAudio = createAgentProposal({
      proposalId: "prop_aud",
      agentRole: "audio",
      baseRevisionId: "rev_01",
      changeSet: {
        changeSetId: "cs_aud",
        description: "Audio changes",
        operations: [{ type: "set-property", targetId: "track_audio_1", property: "volumeDb", value: -3.0 }],
      },
      rationale: "Normalize volume",
    });

    const result = ThreeWayMergeArbiter.merge([propDirector, propAudio], "rev_01");

    assert.equal(result.appliedProposals.length, 2);
    assert.equal(result.mergedChangeSet.operations.length, 2);
    assert.equal(result.conflictCount, 0);
    assert.equal(typeof result.deterministicHash, "string");
  });

  it("ThreeWayMergeArbiter detects conflicting modifications on same property and throws ProposalConflictError", () => {
    const propA = createAgentProposal({
      proposalId: "prop_a",
      agentRole: "motion",
      baseRevisionId: "rev_01",
      changeSet: {
        changeSetId: "cs_a",
        description: "Motion changes A",
        operations: [{ type: "set-property", targetId: "layer_title", property: "color", value: "#FF0000" }],
      },
      rationale: "Red color",
    });

    const propB = createAgentProposal({
      proposalId: "prop_b",
      agentRole: "editor",
      baseRevisionId: "rev_01",
      changeSet: {
        changeSetId: "cs_b",
        description: "Editor changes B",
        operations: [{ type: "set-property", targetId: "layer_title", property: "color", value: "#00FF00" }], // Conflicto!
      },
      rationale: "Green color",
    });

    assert.throws(() => {
      ThreeWayMergeArbiter.merge([propA, propB], "rev_01");
    }, ProposalConflictError);
  });
});
