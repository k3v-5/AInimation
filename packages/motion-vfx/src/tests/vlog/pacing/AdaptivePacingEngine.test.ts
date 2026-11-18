import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import {
  NarrativeAnchor,
  PacingRequest,
  PacingResultSchema,
  SupportedLocale,
  VlogAdaptivePacingEngine,
  VoiceoverTrack,
} from "../../../vlog/index.js";

describe("Milestone 5 — Adaptive Pacing Engine End-to-End Suite", () => {
  const createMockTrack = (locale: SupportedLocale = "es-MX"): VoiceoverTrack => ({
    id: `vo_${locale}_test`,
    locale,
    voiceId: "es_MX-ald-medium",
    audioWavPath: `audio/vo_${locale}.wav`,
    durationSeconds: 12.0,
    checksumSha256: "a".repeat(64),
    format: {
      sampleRateHz: 44100,
      bitDepth: 16,
      channels: 1,
    },
    segments: [
      {
        narrativeSegmentId: "seg_1",
        speechText: "Bienvenidos a este recorrido.",
        displayText: "Bienvenidos a este recorrido.",
        startSeconds: 0.0,
        endSeconds: 4.0,
        durationSeconds: 4.0,
        words: [
          { word: "Bienvenidos", startSeconds: 0.0, endSeconds: 1.2, confidence: 0.99 },
          { word: "a", startSeconds: 1.2, endSeconds: 1.4, confidence: 0.99 },
          { word: "este", startSeconds: 1.4, endSeconds: 2.0, confidence: 0.99 },
          { word: "recorrido", startSeconds: 2.0, endSeconds: 4.0, confidence: 0.99 },
        ],
      },
      {
        narrativeSegmentId: "seg_2",
        speechText: "Aquí comienza la historia.",
        displayText: "Aquí comienza la historia.",
        startSeconds: 4.0,
        endSeconds: 12.0,
        durationSeconds: 8.0,
        words: [
          { word: "Aquí", startSeconds: 4.0, endSeconds: 5.5, confidence: 0.99 },
          { word: "comienza", startSeconds: 5.5, endSeconds: 8.0, confidence: 0.99 },
          { word: "la", startSeconds: 8.0, endSeconds: 9.0, confidence: 0.99 },
          { word: "historia", startSeconds: 9.0, endSeconds: 12.0, confidence: 0.99 },
        ],
      },
    ],
  });

  it("plans automatic voice stretch when disparity is within [0.95, 1.05]", () => {
    const request: PacingRequest = {
      projectId: "proj_pacing_01",
      locale: "es-MX",
      sourceTimelineDurationSeconds: 10.0,
      voiceDurationSeconds: 10.3, // 1.03x (dentro de [0.95, 1.05])
    };

    const result = VlogAdaptivePacingEngine.plan(request);

    assert.equal(result.success, true);
    assert.equal(result.voiceStretchFactor, 1.03);
    assert.equal(result.conflicts.length, 0);
    assert.equal(result.adjustments.length, 1);
    assert.equal(result.adjustments[0].strategy, "VOICE_MICRO_STRETCH");
    assert.doesNotThrow(() => PacingResultSchema.parse(result));
  });

  it("adapts multi-segment voiceover with retiming and B-Roll", () => {
    const track = createMockTrack("es-MX");
    const request: PacingRequest = {
      projectId: "proj_multi",
      locale: "es-MX",
      sourceTimelineDurationSeconds: 11.5,
      voiceDurationSeconds: 12.0,
    };

    const anchors: NarrativeAnchor[] = [
      {
        id: "anchor_hook",
        type: "HOOK",
        sourceTimeSeconds: 4.0,
        targetTimeSeconds: 4.0,
        priority: 5,
        locked: true,
      },
    ];

    const result = VlogAdaptivePacingEngine.plan(request, track, anchors, [
      {
        mediaId: "seg_1",
        sourceStartSeconds: 0.0,
        sourceEndSeconds: 3.5,
        targetStartSeconds: 0.0,
        targetEndSeconds: 4.0,
        assetDurationSeconds: 8.0,
        lockMode: "PREFERRED",
      },
    ]);

    assert.equal(result.locale, "es-MX");
    assert.equal(result.alignments.length, 2);
    assert.equal(result.adaptedDurationSeconds, 12.0);
    assert.doesNotThrow(() => PacingResultSchema.parse(result));
  });

  it("guarantees 100% idempotency: running twice produces byte-equivalent JSON", () => {
    const request: PacingRequest = {
      projectId: "proj_idempotence",
      locale: "en-US",
      sourceTimelineDurationSeconds: 15.0,
      voiceDurationSeconds: 15.4,
    };

    const track = createMockTrack("en-US");

    const res1 = VlogAdaptivePacingEngine.plan(request, track);
    const res2 = VlogAdaptivePacingEngine.plan(request, track);

    // Descartar instancia de timeMapper antes de comparar serialización JSON pura
    const { timeMapper: _t1, ...data1 } = res1;
    const { timeMapper: _t2, ...data2 } = res2;

    assert.equal(JSON.stringify(data1), JSON.stringify(data2));
  });

  it("PBT: PacingResult always satisfies Zod schema and duration bounds", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 5.0, max: 60.0, noNaN: true }),
        fc.double({ min: 0.951, max: 1.049, noNaN: true }),
        (srcDur, stretch) => {
          const voiceDur = srcDur * stretch;
          const req: PacingRequest = {
            projectId: "pbt_pacing",
            locale: "es-MX",
            sourceTimelineDurationSeconds: srcDur,
            voiceDurationSeconds: voiceDur,
          };

          const result = VlogAdaptivePacingEngine.plan(req);
          assert.ok(result.adaptedDurationSeconds > 0);
          assert.ok(!isNaN(result.adaptedDurationSeconds));
          assert.ok(isFinite(result.adaptedDurationSeconds));
          assert.doesNotThrow(() => PacingResultSchema.parse(result));
        }
      )
    );
  });
});
