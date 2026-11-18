import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  SupportedLocale,
  VlogAspectRatio,
  VlogManifestSchema,
  VlogMultilingualProductionOrchestrator,
  VlogProductionConfig,
} from "../../../vlog/index.js";

describe("Milestone 9 — E2E Multilingual Production Suite (5 Locales x 5 Aspects)", () => {
  const createFullE2EConfig = (): VlogProductionConfig => ({
    projectId: "vlog_guadalajara_master",
    sourceLocale: "es-MX",
    targetLocales: ["en-US", "pt-BR", "fr-FR", "de-DE"],
    scriptText: "Bienvenidos a Guadalajara, cuna del mariachi y la arquitectura colonial más impresionante de México.",
    assets: [
      {
        id: "clip_host_intro",
        name: "Host_Intro",
        type: "A_ROLL",
        durationSeconds: 15.0,
        filePath: "C:/footage/aroll_intro.mp4",
      },
      {
        id: "clip_broll_cathedral",
        name: "Cathedral_Aerial",
        type: "B_ROLL",
        durationSeconds: 8.0,
        filePath: "C:/footage/broll_cathedral.mp4",
      },
      {
        id: "audio_music_folk",
        name: "Mexican_Guitar_Acoustic",
        type: "AUDIO_MUSIC",
        durationSeconds: 30.0,
        filePath: "C:/audio/mexican_guitar.wav",
      },
    ],
    aspectRatios: ["16:9", "9:16", "1:1", "4:5", "21:9"],
    geoBadgeData: {
      id: "badge_gdl",
      cityName: "Guadalajara",
      countryName: "México",
      countryCode: "MX",
      coordinates: { latitude: 20.6597, longitude: -103.3496 },
    },
    locationCardData: {
      id: "card_degollado",
      title: "Teatro Degollado",
      subtitle: "Centro Histórico",
      region: "Jalisco",
      durationSeconds: 4.5,
    },
    routePathData: {
      id: "route_tequila_express",
      points: [
        { id: "p1", name: "Guadalajara", latitude: 20.6597, longitude: -103.3496 },
        { id: "p2", name: "Tequila", latitude: 20.8863, longitude: -103.8372 },
      ],
      travelMode: "train",
      animationDurationSeconds: 4.0,
      trimPathsStart: 0,
      trimPathsEnd: 100,
    },
    polaroidData: {
      freezeTimestampSeconds: 9.0,
      captionText: "Recuerdos de Jalisco",
    },
  });

  it("orchestrates a full production run for 5 official locales across all 5 aspect ratios", async () => {
    const config = createFullE2EConfig();
    const result = await VlogMultilingualProductionOrchestrator.execute(config);

    assert.equal(result.isSuccess, true);
    assert.equal(result.run.state, "COMPLETED");
    assert.equal(result.run.currentPhase, "P21_COMPLETE");

    const manifest = result.manifest;
    assert.equal(manifest.projectId, "vlog_guadalajara_master");
    assert.equal(manifest.validation.passed, true);

    // 1. Verificar entrega de audio masters en los 5 idiomas
    const expectedLocales: SupportedLocale[] = ["es-MX", "en-US", "pt-BR", "fr-FR", "de-DE"];
    for (const loc of expectedLocales) {
      assert.ok(manifest.deliverables.audioMasters[loc], `Missing audio master for ${loc}`);
      assert.ok(manifest.deliverables.subtitles[loc], `Missing subtitles for ${loc}`);
    }

    // 2. Verificar generación de scripts JSX (5 idiomas x 5 aspect ratios = 25 scripts)
    const expectedAspects: VlogAspectRatio[] = ["16:9", "9:16", "1:1", "4:5", "21:9"];
    for (const loc of expectedLocales) {
      for (const aspect of expectedAspects) {
        const key = `${loc}_${aspect}`;
        assert.ok(manifest.deliverables.jsxScripts[key], `Missing JSX script for ${key}`);
      }
    }

    // 3. Verificar métricas del reporte de validación
    assert.ok(manifest.validation.metrics.totalDurationSeconds > 0);
    assert.equal(manifest.validation.metrics.cutsCount, 3);
    assert.equal(manifest.validation.metrics.brollCount, 1);
    assert.equal(manifest.validation.metrics.overlaysCount, 4); // GeoBadge, LocationCard, RoutePath, Polaroid

    // 4. Validar cumplimiento formal del esquema de producción
    assert.doesNotThrow(() => VlogManifestSchema.parse(manifest));
  });
});
