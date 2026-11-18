import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import {
  SafeZoneLayoutEngine,
  SupportedLocale,
  VlogSubtitleEngine,
  VlogTravelOverlayEngine,
  VoiceoverTrack,
} from "../../../vlog/index.js";

describe("Milestone 6-F — Subtitles & Overlays Integrated Pipeline Suite", () => {
  const createMockVoiceover = (locale: SupportedLocale = "es-MX"): VoiceoverTrack => ({
    id: `vo_${locale}_integrated`,
    locale,
    voiceId: "es_MX-ald-medium",
    audioWavPath: "audio/vo.wav",
    durationSeconds: 15.0,
    checksumSha256: "d".repeat(64),
    format: { sampleRateHz: 44100, bitDepth: 16, channels: 1 },
    segments: [
      {
        narrativeSegmentId: "seg_intro",
        speechText: "Bienvenidos a Guadalajara, capital cultural.",
        displayText: "Bienvenidos a Guadalajara, capital cultural.",
        startSeconds: 0.0,
        endSeconds: 5.0,
        durationSeconds: 5.0,
        words: [
          { word: "Bienvenidos", startSeconds: 0.0, endSeconds: 1.2, confidence: 0.99 },
          { word: "a", startSeconds: 1.2, endSeconds: 1.4, confidence: 0.99 },
          { word: "Guadalajara,", startSeconds: 1.4, endSeconds: 2.8, confidence: 0.99 },
          { word: "capital", startSeconds: 2.8, endSeconds: 3.6, confidence: 0.99 },
          { word: "cultural.", startSeconds: 3.6, endSeconds: 5.0, confidence: 0.99 },
        ],
      },
      {
        narrativeSegmentId: "seg_location",
        speechText: "El centro histórico alberga tesoros coloniales.",
        displayText: "El centro histórico alberga tesoros coloniales.",
        startSeconds: 5.0,
        endSeconds: 12.0,
        durationSeconds: 7.0,
        words: [
          { word: "El", startSeconds: 5.0, endSeconds: 5.4, confidence: 0.99 },
          { word: "centro", startSeconds: 5.4, endSeconds: 6.2, confidence: 0.99 },
          { word: "histórico", startSeconds: 6.2, endSeconds: 7.5, confidence: 0.99 },
          { word: "alberga", startSeconds: 7.5, endSeconds: 8.5, confidence: 0.99 },
          { word: "tesoros", startSeconds: 8.5, endSeconds: 9.8, confidence: 0.99 },
          { word: "coloniales.", startSeconds: 9.8, endSeconds: 12.0, confidence: 0.99 },
        ],
      },
    ],
  });

  it("orchestrates subtitles and overlays concurrently without safe zone collisions", () => {
    const vo = createMockVoiceover("es-MX");

    // 1. Generar subtítulos
    const subTrack = VlogSubtitleEngine.generateTrack("sub_track_e2e", vo, {
      aspectRatio: "16:9",
      targetYPosition: 0.85, // Subtítulos abajo
    });

    // 2. Generar overlays
    const geoBadge = VlogTravelOverlayEngine.createGeoBadgeItem(
      {
        id: "badge_gdl",
        cityName: "Guadalajara",
        countryName: "México",
        coordinates: { latitude: 20.6597, longitude: -103.3496 },
      },
      0.5,
      4.0,
      { defaultGeoBadgeSlot: "TOP_LEFT" } // Overlay arriba a la izquierda
    );

    const locCard = VlogTravelOverlayEngine.createLocationCardItem(
      {
        id: "loc_cathedral",
        title: "Catedral Metropolitana",
        region: "Centro Histórico",
        durationSeconds: 5.0,
      },
      6.0,
      { defaultLocationCardSlot: "TOP_RIGHT" }
    );

    const { item: polaroid, shutterSfxBuffer } = VlogTravelOverlayEngine.createPolaroidItem({
      id: "pol_monument",
      freezeTimestampSeconds: 12.5,
      captionText: "Teatro Degollado",
    });

    const overlayTrack = VlogTravelOverlayEngine.buildOverlayTrack("overlay_track_e2e", [
      geoBadge,
      locCard,
      polaroid,
    ]);

    // Verificaciones de subtítulos
    assert.equal(subTrack.locale, "es-MX");
    assert.ok(subTrack.cues.length >= 2);
    assert.equal(subTrack.style.highlightFillColor, "#FF1424");

    // Verificaciones de overlays
    assert.equal(overlayTrack.items.length, 3);
    assert.ok(shutterSfxBuffer.length > 0);

    // Verificar no colisión espacial: subtítulos en Y=0.85 (inferior) no colisionan con slots TOP
    for (const cue of subTrack.cues) {
      assert.ok(cue.position.normalizedY >= 0.80);
    }
  });

  it("strictly enforces social UI exclusion in 9:16 vertical video", () => {
    const vo = createMockVoiceover("en-US");
    const subTrack = VlogSubtitleEngine.generateTrack("sub_9x16", vo, {
      aspectRatio: "9:16",
      targetYPosition: 0.72, // Subtítulos situados sobre la barra de descripción inferior
    });

    const forbidden = SafeZoneLayoutEngine.getForbiddenRegions("9:16");

    // En 9:16, un cue a Y=0.72 (y = 1382px en canvas 1920) no debe tocar la barra inferior (y >= 1600)
    for (const cue of subTrack.cues) {
      const pixelY = cue.position.normalizedY * 1920;
      const subtitleBox = {
        x: 80,
        y: pixelY,
        width: 780, // Margen derecho seguro evitando la barra de botones derecha (x >= 940)
        height: 80,
      };
      assert.equal(
        SafeZoneLayoutEngine.intersectsForbiddenRegions(subtitleBox, forbidden),
        false
      );
    }
  });

  it("PBT: simultaneous execution of subtitles and overlays is 100% deterministic", () => {
    const vo = createMockVoiceover("pt-BR");

    fc.assert(
      fc.property(fc.integer({ min: 1, max: 10 }), () => {
        const sub1 = VlogSubtitleEngine.generateTrack("sub_pt", vo);
        const sub2 = VlogSubtitleEngine.generateTrack("sub_pt", vo);
        assert.equal(sub1.checksumSha256, sub2.checksumSha256);

        const badge = VlogTravelOverlayEngine.createGeoBadgeItem({ id: "b1", cityName: "São Paulo" }, 0, 3);
        const oTrack1 = VlogTravelOverlayEngine.buildOverlayTrack("o_pt", [badge]);
        const oTrack2 = VlogTravelOverlayEngine.buildOverlayTrack("o_pt", [badge]);
        assert.equal(oTrack1.checksumSha256, oTrack2.checksumSha256);
      })
    );
  });
});
