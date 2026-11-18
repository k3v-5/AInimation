import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MotionEngine } from "../../sdk/MotionEngineSDK.js";
import { TextElement } from "../../elements/TextElement.js";

describe("Fase 27 — Capa 3: Public TypeScript SDK Tests", () => {
  it("creates a composition and exports to After Effects via SDK", () => {
    const comp = MotionEngine.createComposition({
      id: "sdk_comp_01",
      name: "SDK Test Comp",
      width: 1920,
      height: 1080,
      fps: 30,
      duration: 10.0,
    });

    const text = new TextElement({
      id: "sdk_text",
      name: "SDK Title",
      text: "SDK POWERED",
      style: { fontSize: 64, fontFamily: "Inter-Bold" },
    });
    comp.addElement(text);

    const aeExport = MotionEngine.exportToAfterEffects(comp);
    assert.ok(aeExport.jsxContent.includes('addComp("SDK Test Comp"'));
    assert.equal(typeof aeExport.manifest.deterministicHash, "string");
  });

  it("delivers multi-aspect social package and renders deterministically via SDK", async () => {
    const comp = MotionEngine.createComposition({
      id: "sdk_comp_social",
      name: "SDK Social",
      width: 1080,
      height: 1920,
      fps: 30,
      duration: 5.0,
    });

    const socialPkg = MotionEngine.deliverSocialPackage(comp, "proj_sdk_social", "rev_sdk_1", {
      targetAspectRatios: ["9:16", "16:9", "1:1"],
    });

    assert.equal(Object.keys(socialPkg.pkg.variants).length, 3);
    assert.equal(socialPkg.manifest.manifestVersion, "2.5.0");

    const renderRes = await MotionEngine.render(comp);
    assert.equal(renderRes.success, true);
    assert.equal(renderRes.totalFrames, 150);
    assert.equal(typeof renderRes.contentHash, "string");
  });

  it("executes a distributed production job via SDK", async () => {
    const distResult = await MotionEngine.executeDistributed({
      jobId: "sdk_dist_job",
      projectId: "proj_sdk_dist",
      briefHash: "brief_hash_abc",
      baselineRevisionId: "rev_0",
      workerCount: 4,
    });

    assert.equal(distResult.success, true);
    assert.equal(distResult.tasksFailed, 0);
    assert.ok(distResult.tasksCompleted > 0);
  });
});
