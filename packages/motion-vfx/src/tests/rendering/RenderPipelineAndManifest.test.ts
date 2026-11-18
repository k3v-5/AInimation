import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { RenderPipeline } from "../../rendering/pipeline/RenderPipeline.js";
import { BuiltinOutputProfiles } from "../../rendering/profiles/OutputProfiles.js";
import { RenderJob } from "../../rendering/types/index.js";
import { TimeRange } from "../../timeline/core/TimeRange.js";

describe("Fase 9 — Render Pipeline & Manifest Execution Tests", () => {
  it("executes an end-to-end render job generating frames and manifest", async () => {
    const job: RenderJob = {
      id: "render_job_tiktok_01",
      projectId: "proj_ai_video_01",
      outputProfile: BuiltinOutputProfiles["tiktok-1080x1920"],
      range: new TimeRange(0, 1.0), // 1 segundo = 30 frames
      priority: "normal",
      settings: {
        quality: "final",
        resolutionScale: 1.0,
        enableMotionBlur: false,
        enableEffects: true,
        useProxies: false,
        colorManagement: true,
      },
      state: "queued",
      rendererVersion: "1.0.0",
    };

    const { manifest, frames } = await RenderPipeline.executeJob(job);

    assert.strictEqual(job.state, "completed");
    assert.strictEqual(manifest.framesCompleted, 30);
    assert.strictEqual(manifest.outputProfile.width, 1080);
    assert.strictEqual(manifest.outputProfile.height, 1920);
    assert.strictEqual(frames.length, 30);
    assert.strictEqual(frames[0].width, 1080);
  });
});
