import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MemoryProjectStore } from "../../persistence/MemoryProjectStore.js";
import { ProjectFile } from "../../persistence/schemas/project.schema.js";
import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";
import { RevisionManager } from "../../revisions/RevisionManager.js";
import { RevisionMerge } from "../../revisions/RevisionMerge.js";

describe("Fase 18 — Three-Way Merge & Conflict Detection Tests", () => {
  it("merges non-overlapping branch changes cleanly without conflicts", () => {
    const base = {
      composition: { duration: 10, fps: 30 },
      elements: [
        { id: "elem_title", name: "Title", text: "Base Title" },
        { id: "elem_audio", name: "Audio Track", volume: 1.0 },
      ],
      assets: [],
    };

    // Left branch: updates title text
    const left = {
      ...base,
      elements: [
        { id: "elem_title", name: "Title", text: "Viral Title" },
        { id: "elem_audio", name: "Audio Track", volume: 1.0 },
      ],
    };

    // Right branch: adds a watermark logo asset/element
    const right = {
      ...base,
      elements: [
        { id: "elem_title", name: "Title", text: "Base Title" },
        { id: "elem_audio", name: "Audio Track", volume: 1.0 },
        { id: "elem_logo", name: "Watermark Logo", path: "logo.png" },
      ],
      assets: [{ id: "asset_logo", name: "logo.png" }],
    };

    const mergeRes = RevisionMerge.merge(base, left, right);

    assert.equal(mergeRes.merged, true);
    assert.equal(mergeRes.conflicts.length, 0);

    const merged = mergeRes.result as any;
    assert.equal(merged.elements.length, 3);
    assert.equal(merged.elements.find((e: any) => e.id === "elem_title").text, "Viral Title");
    assert.ok(merged.elements.find((e: any) => e.id === "elem_logo"));
    assert.equal(merged.assets.length, 1);
  });

  it("detects conflicting mutations on the same property and emits RevisionConflict", () => {
    const base = {
      composition: { duration: 10, fps: 30 },
      elements: [{ id: "elem_1", name: "Main Text", text: "Base Text" }],
      assets: [],
    };

    // Branch Left edits text to "Option A"
    const left = {
      composition: { duration: 10, fps: 30 },
      elements: [{ id: "elem_1", name: "Main Text", text: "Option A" }],
      assets: [],
    };

    // Branch Right edits text to "Option B"
    const right = {
      composition: { duration: 10, fps: 30 },
      elements: [{ id: "elem_1", name: "Main Text", text: "Option B" }],
      assets: [],
    };

    const mergeRes = RevisionMerge.merge(base, left, right);

    assert.equal(mergeRes.merged, false);
    assert.equal(mergeRes.conflicts.length, 1);
    assert.equal(mergeRes.conflicts[0].path, "elements.elem_1.text");
    assert.equal(mergeRes.conflicts[0].baseValue, "Base Text");
    assert.equal(mergeRes.conflicts[0].leftValue, "Option A");
    assert.equal(mergeRes.conflicts[0].rightValue, "Option B");
  });

  it("RevisionManager merges multi-agent branches creating a new merge revision", async () => {
    const store = new MemoryProjectStore();
    const revManager = new RevisionManager(store);

    const baseProject = {
      schemaVersion: "1.8.0",
      composition: { duration: 10, fps: 30 },
      elements: [{ id: "l1", name: "Base", text: "Original" }],
      assets: [],
    };

    const projectFile: ProjectFile = {
      schemaVersion: "1.8.0",
      engineVersion: "1.8.0",
      projectId: "proj_merge_multi",
      headRevisionId: "rev_0",
      metadata: { name: "Merge Multi Test" },
      project: baseProject,
      contentHash: ProjectSerializer.hashCanonical(baseProject),
    };

    await store.create(projectFile);

    const rev0 = await revManager.createRevision({
      projectId: "proj_merge_multi",
      parentRevisionId: null,
      project: baseProject,
      author: { type: "system", systemId: "init" },
      message: "Base init",
    });

    // Agent A branch: update text
    const revA = await revManager.createRevision({
      projectId: "proj_merge_multi",
      parentRevisionId: rev0.revisionId,
      project: {
        ...baseProject,
        elements: [{ id: "l1", name: "Base", text: "Edited by Agent A" }],
      },
      author: { type: "agent", agentId: "agent-A" },
      message: "Agent A text change",
    });

    // Agent B branch: add layer 2
    const revB = await revManager.createRevision({
      projectId: "proj_merge_multi",
      parentRevisionId: rev0.revisionId,
      project: {
        ...baseProject,
        elements: [
          { id: "l1", name: "Base", text: "Original" },
          { id: "l2", name: "B-Roll", type: "video" },
        ],
      },
      author: { type: "agent", agentId: "agent-B" },
      message: "Agent B added broll",
    });

    const mergeResult = await revManager.mergeBranches({
      projectId: "proj_merge_multi",
      baseRevisionId: rev0.revisionId,
      leftRevisionId: revA.revisionId,
      rightRevisionId: revB.revisionId,
      author: { type: "system", systemId: "auto-merge" },
    });

    assert.ok(mergeResult.revision);
    assert.equal(mergeResult.mergeResult.merged, true);

    const mergedElements = (mergeResult.revision.project as any).elements;
    assert.equal(mergedElements.length, 2);
    assert.equal(mergedElements[0].text, "Edited by Agent A");
    assert.equal(mergedElements[1].name, "B-Roll");
  });
});
