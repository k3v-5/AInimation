import assert from "node:assert/strict";
import { describe, it, beforeEach } from "node:test";
import { AgentSession } from "../../agent/AgentSession.js";
import { MemoryProjectStore } from "../../persistence/MemoryProjectStore.js";
import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";
import { RevisionConflictError } from "../../persistence/errors/persistence-errors.js";
import { ProjectFile } from "../../persistence/schemas/project.schema.js";
import { RevisionManager } from "../../revisions/RevisionManager.js";

describe("Fase 18 — Agent Session & Optimistic Concurrency Tests", () => {
  let store: MemoryProjectStore;
  let revManager: RevisionManager;
  let headRevId: string;

  beforeEach(async () => {
    store = new MemoryProjectStore();
    revManager = new RevisionManager(store);

    const initialProject = {
      schemaVersion: "1.8.0",
      composition: { duration: 10, fps: 30 },
      elements: [{ id: "elem_title", name: "Intro Title", text: "Welcome" }],
      assets: [],
    };

    const projectFile: ProjectFile = {
      schemaVersion: "1.8.0",
      engineVersion: "1.8.0",
      projectId: "proj_concurrency_test",
      headRevisionId: "rev_initial",
      metadata: { name: "Concurrency Test" },
      project: initialProject,
      contentHash: ProjectSerializer.hashCanonical(initialProject),
    };

    await store.create(projectFile);

    const rev0 = await revManager.createRevision({
      projectId: "proj_concurrency_test",
      parentRevisionId: null,
      project: initialProject,
      author: { type: "system", systemId: "init" },
      message: "Init",
    });

    headRevId = rev0.revisionId;
  });

  it("records observations and decisions in AgentSession memory", async () => {
    const session = new AgentSession({
      sessionId: "sess_01",
      agentId: "agent-editor",
      projectId: "proj_concurrency_test",
      initialRevisionId: headRevId,
      store,
      revisionManager: revManager,
    });

    const obs = await session.observe();
    assert.equal(obs.summary.layerCount, 1);
    assert.equal(obs.summary.duration, 10);
    assert.equal(session.memory.getObservations().length, 1);

    const newRev = await session.mutate({
      action: {
        actionId: "act_1",
        type: "modify_layer",
        targetId: "elem_title",
        parameters: { text: "Updated" },
      },
      rationale: "Make title catchy",
      expectedOutcome: "Higher viewer retention",
      mutation: (draft: any) => {
        draft.elements[0].text = "Updated";
        return draft;
      },
    });

    assert.ok(newRev.revisionId.startsWith("rev_"));
    assert.equal(session.memory.getDecisions().length, 1);
    assert.equal(session.expectedRevisionId, newRev.revisionId);
  });

  it("enforces agent policy and blocks unauthorized actions", async () => {
    const session = new AgentSession({
      sessionId: "sess_policy",
      agentId: "agent-restricted",
      projectId: "proj_concurrency_test",
      initialRevisionId: headRevId,
      store,
      revisionManager: revManager,
      policy: {
        maxOperationsPerSession: 10,
        allowedActionTypes: ["modify_layer"],
        allowDestructiveDeletions: false,
        maxDurationSeconds: 60,
      },
    });

    await assert.rejects(async () => {
      await session.mutate({
        action: { actionId: "act_unauthorized", type: "unauthorized_action_type", parameters: {} },
        rationale: "Try forbidden op",
        expectedOutcome: "Fail",
        mutation: (d) => d,
      });
    }, /Agent action rejected by policy/);
  });

  it("throws RevisionConflictError on optimistic concurrency collisions between concurrent agent sessions", async () => {
    // Agent 1 opens project at current HEAD
    const session1 = new AgentSession({
      sessionId: "sess_agent1",
      agentId: "agent-alpha",
      projectId: "proj_concurrency_test",
      initialRevisionId: headRevId,
      store,
      revisionManager: revManager,
    });

    // Agent 2 ALSO opens project at current HEAD concurrently
    const session2 = new AgentSession({
      sessionId: "sess_agent2",
      agentId: "agent-beta",
      projectId: "proj_concurrency_test",
      initialRevisionId: headRevId,
      store,
      revisionManager: revManager,
    });

    // Agent 1 mutates first successfully -> moves project HEAD to rev1
    const rev1 = await session1.mutate({
      action: { actionId: "act_1", type: "modify_layer", parameters: {} },
      rationale: "Agent 1 edits",
      expectedOutcome: "Success",
      mutation: (draft: any) => {
        draft.elements[0].text = "Agent 1 Edit";
        return draft;
      },
    });

    assert.equal(session1.expectedRevisionId, rev1.revisionId);

    // Agent 2 attempts to mutate while still holding stale expectedRevisionId (headRevId)
    await assert.rejects(async () => {
      await session2.mutate({
        action: { actionId: "act_2", type: "modify_layer", parameters: {} },
        rationale: "Agent 2 edits concurrently",
        expectedOutcome: "Fail due to conflict",
        mutation: (draft: any) => {
          draft.elements[0].text = "Agent 2 Edit";
          return draft;
        },
      });
    }, RevisionConflictError);
  });
});
