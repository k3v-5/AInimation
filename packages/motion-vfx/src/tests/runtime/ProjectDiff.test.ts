import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { ProjectDiffEngine } from "../../runtime/ProjectDiff.js";

describe("Fase 18 — Project Diff & Semantic Diffing Tests", () => {
  it("calculates structural and semantic differences between two revisions", () => {
    const rev1 = {
      projectId: "proj_diff_test",
      revisionId: "rev_000001",
      project: {
        elements: [
          { id: "elem_1", name: "Title", text: "Hola", style: { fontSize: 40 }, startTime: 0, duration: 5 },
          { id: "elem_2", name: "Old Box", startTime: 0, duration: 10 },
        ],
      },
    };

    const rev2 = {
      projectId: "proj_diff_test",
      revisionId: "rev_000002",
      project: {
        elements: [
          { id: "elem_1", name: "Title", text: "Hola Mundo", style: { fontSize: 72 }, startTime: 1, duration: 8 },
          { id: "elem_3", name: "New Sticker", startTime: 2, duration: 4 },
        ],
      },
    };

    const diff = ProjectDiffEngine.diff(rev1, rev2);

    assert.equal(diff.projectId, "proj_diff_test");
    assert.equal(diff.fromRevisionId, "rev_000001");
    assert.equal(diff.toRevisionId, "rev_000002");

    assert.equal(diff.summary.layersAdded, 1); // elem_3
    assert.equal(diff.summary.layersRemoved, 1); // elem_2
    assert.ok(diff.summary.layersModified >= 1); // elem_1 (text, fontSize, timing)
    assert.equal(diff.summary.timingModifications, 1); // elem_1 timing change

    const fontMod = diff.modified.find((m) => m.path.includes("style.fontSize"));
    assert.ok(fontMod);
    assert.equal(fontMod.before, 40);
    assert.equal(fontMod.after, 72);
  });
});
