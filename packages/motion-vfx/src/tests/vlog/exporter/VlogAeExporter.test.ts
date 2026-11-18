import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import {
  VlogAeExportParams,
  VlogAfterEffectsExporter,
  VlogAudioMixer,
  VlogSubtitleEngine,
  VlogTravelOverlayEngine,
} from "../../../vlog/index.js";

describe("Milestone 7 — Vlog After Effects JSX Exporter Suite", () => {
  const createMockExportParams = (): VlogAeExportParams => {
    // 1. Audio mix plan
    const audioPlan = VlogAudioMixer.createMixPlan(
      "proj_ae",
      "es-MX",
      [
        {
          id: "m1",
          name: "Music",
          type: "MUSIC",
          audioFilePath: "C:/media/music.wav",
          timelineStartSeconds: 0,
          timelineEndSeconds: 15,
        },
      ],
      [{ startSeconds: 2.0, endSeconds: 5.0 }]
    );

    // 2. Subtitle track
    const subTrack = VlogSubtitleEngine.generateTrack("sub_01", {
      id: "vo_01",
      locale: "es-MX",
      voiceId: "v1",
      audioWavPath: "a.wav",
      durationSeconds: 10,
      checksumSha256: "e".repeat(64),
      format: { sampleRateHz: 44100, bitDepth: 16, channels: 1 },
      segments: [
        {
          narrativeSegmentId: "s1",
          speechText: "HOLA MUNDO",
          displayText: "HOLA MUNDO",
          startSeconds: 1.0,
          endSeconds: 3.0,
          durationSeconds: 2.0,
          words: [
            { word: "HOLA", startSeconds: 1.0, endSeconds: 1.8, confidence: 0.99 },
            { word: "MUNDO", startSeconds: 1.8, endSeconds: 3.0, confidence: 0.99 },
          ],
        },
      ],
    });

    // 3. Overlays
    const badge = VlogTravelOverlayEngine.createGeoBadgeItem(
      { id: "b1", cityName: "Guadalajara" },
      0.5,
      3.0
    );

    const { item: polaroid } = VlogTravelOverlayEngine.createPolaroidItem({
      id: "pol_test",
      freezeTimestampSeconds: 4.0,
    });

    return {
      projectId: "proj_vlog_01",
      compositionName: "Vlog_Master_es-MX",
      durationSeconds: 15.0,
      fps: 30,
      aspectRatio: "16:9",
      aRollClips: [
        {
          id: "clip_aroll_1",
          name: "Interview_01",
          filePath: "C:/media/aroll.mp4",
          timelineStartSeconds: 0.0,
          timelineEndSeconds: 6.0,
          punchInScalePercent: 115,
          punchInCenterNormalized: [0.5, 0.45],
        },
      ],
      bRollClips: [
        {
          id: "clip_broll_1",
          name: "Broll_City",
          filePath: "C:/media/broll.mp4",
          timelineStartSeconds: 6.0,
          timelineEndSeconds: 12.0,
        },
      ],
      subtitleTrack: subTrack,
      overlayItems: [badge, polaroid],
      audioMixPlan: audioPlan,
    };
  };

  it("compiles full vlog project to valid ExtendScript JSX adhering to design preferences", () => {
    const params = createMockExportParams();
    const result = VlogAfterEffectsExporter.exportToJsx(params);

    const jsx = result.jsxContent;

    // 1. Verificación de Motion Blur obligatorio
    assert.ok(jsx.includes("comp.motionBlur = true;"));
    assert.ok(jsx.includes(".motionBlur = true;"));

    // 2. Verificación de Justificación Centrada obligatoria
    assert.ok(jsx.includes("ParagraphJustification.CENTER_JUSTIFY;"));

    // 3. Verificación de Tipografía TIME y estiramiento vertical
    assert.ok(jsx.includes("Impact"));
    assert.ok(jsx.includes(".property('ADBE Scale').setValue([100, 135]);"));

    // 4. Verificación de Dynamic Punch-In (115% de escala)
    assert.ok(jsx.includes(".property('ADBE Scale').setValue([115, 115]);"));

    // 5. Verificación de Audio Ducking keyframes
    assert.ok(jsx.includes("setValueAtTime"));
    assert.ok(jsx.includes("Audio Levels"));

    // 6. Verificación de Polaroid y rotación
    assert.ok(jsx.includes("Polaroid_pol_test"));
    assert.ok(jsx.includes("ADBE Rotation"));

    // 7. Estructura de Undo Group
    assert.ok(jsx.includes("app.beginUndoGroup"));
    assert.ok(jsx.includes("app.endUndoGroup"));
    assert.equal(result.checksumSha256.length, 64);
  });

  it("guarantees 100% determinism: same params generate byte-identical JSX and checksum", () => {
    const params = createMockExportParams();
    const res1 = VlogAfterEffectsExporter.exportToJsx(params);
    const res2 = VlogAfterEffectsExporter.exportToJsx(params);

    assert.equal(res1.checksumSha256, res2.checksumSha256);
    assert.equal(res1.jsxContent, res2.jsxContent);
  });

  it("PBT: JSX export always generates non-empty script with matching dimensions", () => {
    fc.assert(
      fc.property(
        fc.constantFrom("16:9", "9:16", "1:1", "4:5", "21:9"),
        fc.integer({ min: 5, max: 60 }),
        (aspectRatio: any, duration) => {
          const res = VlogAfterEffectsExporter.exportToJsx({
            projectId: "pbt_proj",
            compositionName: "PBT_Comp",
            durationSeconds: duration,
            aspectRatio,
          });

          assert.ok(res.jsxContent.length > 500);
          assert.equal(res.durationSeconds, duration);
          assert.equal(res.aspectRatio, aspectRatio);
          assert.ok(res.width > 0 && res.height > 0);
        }
      )
    );
  });
});
