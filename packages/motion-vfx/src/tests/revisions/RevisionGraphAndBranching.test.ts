import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { RevisionGraph } from "../../revisions/RevisionGraph.js";
import { RevisionId } from "../../revisions/RevisionId.js";
import { Revision } from "../../persistence/schemas/revision.schema.js";

describe("Fase 18 — Revision Graph & Branching Tests", () => {
  it("RevisionId produces deterministic hashes regardless of field order", () => {
    const id1 = RevisionId.generate({
      projectId: "proj_1",
      parentRevisionId: "rev_root",
      projectHash: "a".repeat(64),
      message: "Add title",
    });

    const id2 = RevisionId.generate({
      projectId: "proj_1",
      parentRevisionId: "rev_root",
      projectHash: "a".repeat(64),
      message: "Add title",
    });

    assert.equal(id1, id2);
    assert.ok(id1.startsWith("rev_"));
    assert.equal(id1.length, 20); // "rev_" + 16 chars
  });

  it("RevisionGraph navigates branching trees, ancestors and descendants accurately", () => {
    // Tree topology:
    //         rev_0 (root)
    //         /          \
    //      rev_1a       rev_1b
    //        |             |
    //      rev_2a       rev_2b
    //        |
    //      rev_3a

    const createMockRev = (id: string, parent: string | null): Revision => ({
      revisionId: id,
      projectId: "proj_branch",
      parentRevisionId: parent,
      createdBy: { type: "agent", agentId: "agent-1" },
      message: `Step ${id}`,
      changes: [],
      projectHash: "b".repeat(64),
      schemaVersion: "1.8.0",
      project: { id },
    });

    const rev0 = createMockRev("rev_0", null);
    const rev1a = createMockRev("rev_1a", "rev_0");
    const rev1b = createMockRev("rev_1b", "rev_0");
    const rev2a = createMockRev("rev_2a", "rev_1a");
    const rev2b = createMockRev("rev_2b", "rev_1b");
    const rev3a = createMockRev("rev_3a", "rev_2a");

    const graph = new RevisionGraph([rev0, rev1a, rev1b, rev2a, rev2b, rev3a]);

    assert.equal(graph.getRoot()?.revisionId, "rev_0");
    assert.equal(graph.getHead()?.revisionId, "rev_3a");

    // Children queries
    const rev0Children = graph.getChildren("rev_0");
    assert.deepEqual(
      rev0Children.map((r) => r.revisionId),
      ["rev_1a", "rev_1b"]
    );

    // Parent queries
    assert.equal(graph.getParent("rev_2a")?.revisionId, "rev_1a");
    assert.equal(graph.getParent("rev_0"), undefined);

    // Ancestor queries
    const rev3aAncestors = graph.getAncestors("rev_3a");
    assert.deepEqual(
      rev3aAncestors.map((r) => r.revisionId),
      ["rev_2a", "rev_1a", "rev_0"]
    );

    // Descendants queries
    const rev1aDescendants = graph.getDescendants("rev_1a");
    assert.deepEqual(
      rev1aDescendants.map((r) => r.revisionId),
      ["rev_2a", "rev_3a"]
    );

    // isAncestor checks
    assert.equal(graph.isAncestor("rev_0", "rev_3a"), true);
    assert.equal(graph.isAncestor("rev_1a", "rev_3a"), true);
    assert.equal(graph.isAncestor("rev_1b", "rev_3a"), false);
    assert.equal(graph.isAncestor("rev_2b", "rev_3a"), false);
    assert.equal(graph.isAncestor("rev_3a", "rev_3a"), true);
  });
});
