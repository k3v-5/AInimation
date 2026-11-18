import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import { MemoryProjectStore } from "../../persistence/MemoryProjectStore.js";
import { RevisionDiff } from "../../revisions/RevisionDiff.js";
import { RevisionManager } from "../../revisions/RevisionManager.js";
import { RevisionPatch } from "../../revisions/RevisionPatch.js";
import { ProjectFile } from "../../persistence/schemas/project.schema.js";
import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";

describe("Fase 18 — Diff, Patch, Reverse Patch & Undo/Restore Tests", () => {
  it("RevisionDiff calculates added, removed and modified elements accurately", () => {
    const projectA = {
      composition: { duration: 10, fps: 30 },
      elements: [
        { id: "elem_1", name: "Text Header", text: "Hello" },
        { id: "elem_2", name: "Background", color: "#000" },
      ],
      assets: [],
    };

    const projectB = {
      composition: { duration: 12, fps: 30 },
      elements: [
        { id: "elem_1", name: "Text Header", text: "World" },
        { id: "elem_3", name: "Logo", path: "logo.png" },
      ],
      assets: [{ id: "asset_logo", name: "logo.png" }],
    };

    const diffResult = RevisionDiff.diff(projectA, projectB);

    assert.equal(diffResult.summary.added, 2); // elem_3 + asset_logo
    assert.equal(diffResult.summary.removed, 1); // elem_2
    assert.equal(diffResult.summary.modified, 2); // duration + elem_1 text
  });

  it("RevisionPatch fulfills the reversibility invariant: reversePatch(applyPatch(P, D), D) === P", () => {
    const originalProject = {
      schemaVersion: "1.8.0",
      composition: { duration: 10, fps: 30 },
      elements: [
        { id: "l1", name: "Layer 1", text: "Base Text" },
        { id: "l2", name: "Layer 2", startTime: 0, duration: 5 },
      ],
      assets: [],
    };

    const modifiedProject = {
      schemaVersion: "1.8.0",
      composition: { duration: 15, fps: 30 },
      elements: [
        { id: "l1", name: "Layer 1 Modified", text: "Updated Text" },
        { id: "l3", name: "Layer 3 New", startTime: 2, duration: 4 },
      ],
      assets: [{ id: "a1", name: "audio.mp3" }],
    };

    const diff = RevisionDiff.diff(originalProject, modifiedProject);
    const patched = RevisionPatch.applyPatch(originalProject, diff.changes);
    const reversed = RevisionPatch.reversePatch(patched, diff.changes) as any;

    assert.deepEqual(reversed.composition, originalProject.composition);
    assert.equal(reversed.elements.length, originalProject.elements.length);
    assert.equal(reversed.elements[0].text, "Base Text");
    assert.equal(reversed.elements[0].name, "Layer 1");
    assert.equal(reversed.assets.length, 0);
  });

  it("PBT with fast-check: random structural mutations satisfy patch reversibility", () => {
    fc.assert(
      fc.property(
        fc.record({
          duration: fc.integer({ min: 1, max: 100 }),
          text: fc.string({ minLength: 1, maxLength: 50 }),
        }),
        fc.record({
          duration: fc.integer({ min: 1, max: 100 }),
          text: fc.string({ minLength: 1, maxLength: 50 }),
        }),
        (stateA, stateB) => {
          const projA = {
            composition: { duration: stateA.duration, fps: 30 },
            elements: [{ id: "layer_dyn", name: "Dynamic", text: stateA.text }],
            assets: [],
          };

          const projB = {
            composition: { duration: stateB.duration, fps: 30 },
            elements: [{ id: "layer_dyn", name: "Dynamic", text: stateB.text }],
            assets: [],
          };

          const diff = RevisionDiff.diff(projA, projB);
          const applied = RevisionPatch.applyPatch(projA, diff.changes);
          const reversed = RevisionPatch.reversePatch(applied, diff.changes) as any;

          return (
            reversed.composition.duration === projA.composition.duration &&
            reversed.elements[0].text === projA.elements[0].text
          );
        }
      ),
      { numRuns: 50 }
    );
  });

  it("RevisionManager undo and restore create new revisions without destroying history", async () => {
    const store = new MemoryProjectStore();
    const revManager = new RevisionManager(store);

    const initialProject = {
      schemaVersion: "1.8.0",
      composition: { duration: 10, fps: 30 },
      elements: [{ id: "l1", name: "Initial", text: "V1" }],
      assets: [],
    };

    const projectFile: ProjectFile = {
      schemaVersion: "1.8.0",
      engineVersion: "1.8.0",
      projectId: "proj_undo_test",
      headRevisionId: "rev_1",
      metadata: { name: "Undo Test" },
      project: initialProject,
      contentHash: ProjectSerializer.hashCanonical(initialProject),
    };

    await store.create(projectFile);

    const rev1 = await revManager.createRevision({
      projectId: "proj_undo_test",
      parentRevisionId: null,
      project: initialProject,
      author: { type: "agent", agentId: "agent-1" },
      message: "Version 1",
    });

    const v2Project = {
      ...initialProject,
      elements: [{ id: "l1", name: "Modified", text: "V2" }],
    };

    const rev2 = await revManager.createRevision({
      projectId: "proj_undo_test",
      parentRevisionId: rev1.revisionId,
      project: v2Project,
      author: { type: "agent", agentId: "agent-1" },
      message: "Version 2",
    });

    // Undo rev2 -> Generates rev3 containing V1 content
    const rev3 = await revManager.undoRevision({
      projectId: "proj_undo_test",
      targetRevisionId: rev2.revisionId,
      author: { type: "agent", agentId: "agent-1" },
    });

    assert.notEqual(rev3.revisionId, rev2.revisionId);
    assert.equal(rev3.parentRevisionId, rev2.revisionId);
    assert.equal((rev3.project as any).elements[0].text, "V1");

    // History is fully preserved: 3 distinct revisions
    const allRevs = await revManager.listRevisions("proj_undo_test");
    assert.equal(allRevs.length, 3);
  });
});
