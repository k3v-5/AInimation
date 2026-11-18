import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  VlogMultilingualProductionOrchestrator,
  VlogProductionConfig,
} from "../../../vlog/index.js";

describe("Milestone 9 — Determinism & Idempotency Validation Suite", () => {
  const createBaseConfig = (): VlogProductionConfig => ({
    projectId: "proj_determinism_test",
    sourceLocale: "es-MX",
    targetLocales: ["en-US"],
    scriptText: "Determinismo absoluto e idempotencia en la suite de producción multilingüe.",
    assets: [
      {
        id: "clip_01",
        name: "Test_Aroll",
        type: "A_ROLL",
        durationSeconds: 10.0,
        filePath: "C:/media/aroll.mp4",
      },
    ],
    aspectRatios: ["16:9"],
    geoBadgeData: {
      id: "badge_01",
      cityName: "Madrid",
      countryName: "España",
    },
    polaroidData: {
      freezeTimestampSeconds: 5.0,
      captionText: "Momento Determinista",
    },
  });

  it("produces identical configurationHash and artifacts checksum across multiple runs", async () => {
    const config1 = createBaseConfig();
    const config2 = createBaseConfig();

    const res1 = await VlogMultilingualProductionOrchestrator.execute(config1);
    const res2 = await VlogMultilingualProductionOrchestrator.execute(config2);

    assert.equal(res1.isSuccess, true);
    assert.equal(res2.isSuccess, true);

    // Mismo configurationHash
    assert.equal(res1.manifest.configurationHash, res2.manifest.configurationHash);

    // Mismo número de artefactos
    assert.equal(res1.manifest.artifacts.length, res2.manifest.artifacts.length);

    // Cada artefacto debe tener idéntico checksumSha256
    for (let i = 0; i < res1.manifest.artifacts.length; i++) {
      const art1 = res1.manifest.artifacts[i];
      const art2 = res2.manifest.artifacts[i];
      assert.equal(art1.producerPhase, art2.producerPhase);
      assert.equal(art1.checksumSha256, art2.checksumSha256);
    }
  });
});
