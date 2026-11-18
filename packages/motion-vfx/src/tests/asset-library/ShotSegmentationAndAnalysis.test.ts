import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { IntelligentAsset } from "../../asset-library/types/index.js";

describe("Fase 10 — Shot Segmentation & Analysis Tests", () => {
  it("structures multi-shot assets with objects, camera movement and quality scores", () => {
    const asset: IntelligentAsset = {
      id: "asset_clip_01",
      type: "video",
      filename: "programming_session.mp4",
      duration: 12.0,
      provenance: {
        source: "local",
        license: "royalty-free",
        importDate: new Date().toISOString(),
        originalPath: "/assets/programming_session.mp4",
      },
      tags: ["technology", "coding", "laptop"],
      userCorrections: {},
      metadata: { width: 1920, height: 1080, fps: 30 },
      shots: [
        {
          id: "shot_01",
          assetId: "asset_clip_01",
          start: 0,
          end: 4.0,
          duration: 4.0,
          description: "Close-up of hands typing code on a mechanical keyboard",
          analysis: {
            objects: ["keyboard", "hands", "laptop"],
            environment: ["office"],
            action: ["typing"],
            camera: { shot: "close-up", movement: "static" },
            qualityScore: 0.95,
          },
        },
        {
          id: "shot_02",
          assetId: "asset_clip_01",
          start: 4.0,
          end: 12.0,
          duration: 8.0,
          description: "Medium shot of developer looking at multi-monitor code setup",
          analysis: {
            objects: ["person", "monitor", "desk"],
            environment: ["office"],
            action: ["coding", "thinking"],
            camera: { shot: "medium", movement: "pan" },
            qualityScore: 0.92,
          },
        },
      ],
    };

    assert.strictEqual(asset.shots.length, 2);
    assert.strictEqual(asset.shots[0].analysis.camera.shot, "close-up");
    assert.strictEqual(asset.shots[1].analysis.objects.includes("monitor"), true);
  });
});
