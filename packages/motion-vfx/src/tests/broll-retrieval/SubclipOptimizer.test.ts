import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { SubclipOptimizer } from "../../broll-retrieval/core/SubclipOptimizer.js";
import { IndexedAsset } from "../../broll-retrieval/types/index.js";

describe("Fase 15 — Subclip Optimizer Tests", () => {
  it("extracts optimal subclip window matching target duration inside long footage", () => {
    const longAsset: IndexedAsset = {
      id: "asset_long",
      uri: "file://clips/interview.mp4",
      fingerprint: "hash_long",
      duration: 18.0,
      orientation: "landscape",
      tags: ["interview"],
      shots: [
        {
          id: "shot_intro",
          start: 0,
          end: 4.0,
          objects: [],
          hasFace: true,
          textSafeSide: "left",
          quality: 0.8,
          energy: 0.5,
        },
        {
          id: "shot_core",
          start: 4.0,
          end: 10.0, // 6s de toma
          objects: ["speaker"],
          hasFace: true,
          textSafeSide: "right",
          quality: 0.95,
          energy: 0.85,
        },
      ],
      license: { source: "user", attributionRequired: false, commercialUse: true },
      usageCount: 0,
    };

    // Extraer 3.0s de subclip
    const subclip = SubclipOptimizer.findBestSubclip(longAsset, 3.0);
    assert.strictEqual(subclip.end - subclip.start, 3.0);
    assert.strictEqual(subclip.start >= 0, true);
    assert.strictEqual(subclip.end <= 18.0, true);
  });
});
