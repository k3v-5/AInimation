import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import {
  VlogManifestSchema,
  VlogMultilingualProductionOrchestrator,
  VlogProductionConfig,
} from "../../../vlog/index.js";

describe("Milestone 8 — Vlog Multilingual Production Orchestrator Suite", () => {
  const createMockConfig = (): VlogProductionConfig => ({
    projectId: "vlog_jalisco_doc",
    sourceLocale: "es-MX",
    targetLocales: ["en-US", "pt-BR"],
    scriptText: "Bienvenidos a Jalisco, tierra del tequila y el mariachi tradicional.",
    assets: [
      {
        id: "asset_aroll_01",
        name: "Host_Speaking",
        type: "A_ROLL",
        durationSeconds: 12.0,
        filePath: "C:/media/aroll_01.mp4",
      },
      {
        id: "asset_broll_01",
        name: "Agave_Fields",
        type: "B_ROLL",
        durationSeconds: 6.0,
        filePath: "C:/media/broll_01.mp4",
      },
    ],
    aspectRatios: ["16:9", "9:16"],
    geoBadgeData: {
      id: "badge_gdl",
      cityName: "Guadalajara",
      countryName: "México",
    },
    locationCardData: {
      id: "loc_tequila",
      title: "Tequila",
      region: "Jalisco",
      durationSeconds: 4.0,
    },
    polaroidData: {
      freezeTimestampSeconds: 8.0,
      captionText: "Campos de Agave",
    },
  });

  it("executes all 22 phases end-to-end producing a validated VlogManifest", async () => {
    const config = createMockConfig();
    const result = await VlogMultilingualProductionOrchestrator.execute(config);

    assert.equal(result.isSuccess, true);
    assert.equal(result.run.state, "COMPLETED");
    assert.equal(result.run.currentPhase, "P21_COMPLETE");

    // Verificar que las 22 fases fueron completadas
    assert.equal(result.run.phases.length, 22);
    for (const phase of result.run.phases) {
      assert.equal(phase.state, "COMPLETED");
      assert.ok(phase.producedArtifactIds.length >= 1);
    }

    // Verificar manifiesto final
    const manifest = result.manifest;
    assert.equal(manifest.projectId, config.projectId);
    assert.equal(manifest.sourceLocale, "es-MX");
    assert.deepEqual(manifest.targetLocales, ["en-US", "pt-BR"]);
    assert.equal(manifest.validation.passed, true);

    // Verificar entregables multilingües (3 idiomas: es-MX, en-US, pt-BR)
    assert.ok(manifest.deliverables.audioMasters["es-MX"]);
    assert.ok(manifest.deliverables.audioMasters["en-US"]);
    assert.ok(manifest.deliverables.audioMasters["pt-BR"]);

    assert.ok(manifest.deliverables.subtitles["es-MX"]);
    assert.ok(manifest.deliverables.subtitles["en-US"]);
    assert.ok(manifest.deliverables.subtitles["pt-BR"]);

    // Verificar JSX generado para 3 idiomas x 2 aspect ratios = 6 scripts
    assert.ok(manifest.deliverables.jsxScripts["es-MX_16:9"]);
    assert.ok(manifest.deliverables.jsxScripts["es-MX_9:16"]);
    assert.ok(manifest.deliverables.jsxScripts["en-US_16:9"]);
    assert.ok(manifest.deliverables.jsxScripts["en-US_9:16"]);
    assert.ok(manifest.deliverables.jsxScripts["pt-BR_16:9"]);
    assert.ok(manifest.deliverables.jsxScripts["pt-BR_9:16"]);

    // Validar esquema Zod formal del manifiesto
    assert.doesNotThrow(() => VlogManifestSchema.parse(manifest));
  });

  it("handles input validation failure cleanly marking pipeline as FAILED", async () => {
    const invalidConfig: VlogProductionConfig = {
      projectId: "proj_empty",
      sourceLocale: "es-MX",
      targetLocales: [],
      scriptText: "", // Vacío -> debe fallar en P01_VALIDATE_INPUT
      assets: [],
    };

    const result = await VlogMultilingualProductionOrchestrator.execute(invalidConfig);

    assert.equal(result.isSuccess, false);
    assert.equal(result.run.state, "FAILED");
    assert.equal(result.manifest.validation.passed, false);

    const p01 = result.run.phases.find((p) => p.phase === "P01_VALIDATE_INPUT");
    assert.equal(p01?.state, "FAILED");
    assert.ok(p01?.errorMessage?.includes("Validation Error"));
  });

  it("PBT: productionHash is strictly 64 hex characters (SHA-256)", async () => {
    const config = createMockConfig();
    const result = await VlogMultilingualProductionOrchestrator.execute(config);

    assert.equal(result.manifest.productionHash.length, 64);
    assert.match(result.manifest.productionHash, /^[0-9a-f]{64}$/);
  });
});
