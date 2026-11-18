import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import {
  VlogJumpCutEngine,
  VlogTranscript,
  VlogTranscriptWord,
} from "../../../vlog/index.js";

describe("Milestone 3 — Vlog Jump Cut Engine Suite", () => {
  const createTranscript = (words: Array<{ word: string; start: number; end: number }>): VlogTranscript => ({
    id: "tr_test",
    language: "es",
    locale: "es-MX",
    durationSeconds: 10.0,
    confidence: 0.95,
    rawText: words.map((w) => w.word).join(" "),
    segments: [
      {
        id: "seg_1",
        startSeconds: words[0]?.start ?? 0,
        endSeconds: words[words.length - 1]?.end ?? 0,
        text: words.map((w) => w.word).join(" "),
        confidence: 0.95,
        words: words.map((w) => ({
          word: w.word,
          startSeconds: w.start,
          endSeconds: w.end,
          confidence: 0.95,
        })),
      },
    ],
  });

  it("keeps silences <= 0.25s and removes silences > 0.25s", () => {
    // Palabra 1: [1.0, 2.0]
    // Gap 1: [2.0, 2.20] (0.20s <= 0.25s => KEEP)
    // Palabra 2: [2.20, 3.0]
    // Gap 2: [3.0, 4.0] (1.00s > 0.25s => REMOVE candidate, unless narrative)
    // Palabra 3: [4.0, 5.0]
    const words = [
      { word: "Hola", start: 1.0, end: 2.0 },
      { word: "amigos", start: 2.20, end: 3.0 },
      { word: "bienvenidos", start: 4.0, end: 5.0 },
    ];
    const transcript = createTranscript(words);

    const plan = VlogJumpCutEngine.createJumpCutPlan(
      "proj_test",
      "asset_01",
      6.0,
      transcript,
      undefined,
      undefined,
      undefined,
      { preserveNarrativePauses: false } // Forzar corte para probar umbral
    );

    assert.ok(plan.decisions.length > 0);
    const cuts = plan.decisions.filter((d) => d.action === "CUT_SILENCE");
    const keeps = plan.decisions.filter((d) => d.action === "KEEP_TRANSITION");

    assert.ok(keeps.some((k) => k.reason.includes("<= threshold")));
    assert.ok(cuts.length >= 1);
  });

  it("preserves explicit narrative pauses >= 0.80s", () => {
    // Pausa dramática de 1.2s entre oraciones
    const words = [
      { word: "Silencio", start: 0.5, end: 1.5 },
      { word: "dramático", start: 2.7, end: 3.5 }, // Pausa de 1.2s
    ];
    const transcript = createTranscript(words);

    const plan = VlogJumpCutEngine.createJumpCutPlan(
      "proj_test",
      "asset_01",
      4.0,
      transcript,
      undefined,
      [{ id: "p1", startSeconds: 1.5, endSeconds: 2.7, durationSeconds: 1.2, type: "NARRATIVE", confidence: 0.9, isRemovable: false }],
      undefined,
      { preserveNarrativePauses: true }
    );

    const preserved = plan.decisions.filter((d) => d.action === "PRESERVE_NARRATIVE_PAUSE");
    assert.ok(preserved.length >= 1);
    assert.equal(plan.statistics.pausesPreservedCount, 1);
  });

  it("attenuates breaths by -6 dB without cutting them out", () => {
    const words = [
      { word: "Frase", start: 0.5, end: 1.5 },
      { word: "siguiente", start: 2.2, end: 3.0 },
    ];
    const transcript = createTranscript(words);

    const plan = VlogJumpCutEngine.createJumpCutPlan(
      "proj_test",
      "asset_01",
      4.0,
      transcript,
      undefined,
      undefined,
      [{ id: "b1", startSeconds: 1.6, endSeconds: 2.0, durationSeconds: 0.4, confidence: 0.85, peakDb: -18, attenuationDb: -6.0, retain: true }]
    );

    const attenuated = plan.decisions.filter((d) => d.action === "ATTENUATE_BREATH");
    assert.ok(attenuated.length >= 1);
    assert.equal(plan.statistics.breathsAttenuatedCount, 1);
  });

  it("guarantees absolute word boundary protection: no cut inside words", () => {
    // Supongamos que se propone un corte en [1.5, 2.5], pero la palabra está en [2.0, 2.6]
    const words = [
      { word: "Primera", start: 0.5, end: 1.4 },
      { word: "Intocable", start: 2.0, end: 2.8 },
      { word: "Tercera", start: 3.8, end: 4.5 },
    ];
    const transcript = createTranscript(words);

    const rawSilences = [
      { startSeconds: 1.4, endSeconds: 2.5, durationSeconds: 1.1, averageEnergyRms: 0.0 }, // Invade a "Intocable"
    ];

    const plan = VlogJumpCutEngine.createJumpCutPlan(
      "proj_test",
      "asset_01",
      5.0,
      transcript,
      rawSilences,
      undefined,
      undefined,
      { wordBoundarySafetySeconds: 0.015 }
    );

    // Ningún corte puede penetrar [2.0 - 0.015, 2.8 + 0.015]
    for (const dec of plan.decisions) {
      if (dec.action === "CUT_SILENCE") {
        const cutEnd = dec.sourceCutTimeSeconds + dec.silenceDurationRemovedSeconds;
        assert.ok(
          cutEnd <= 2.0 - 0.015 || dec.sourceCutTimeSeconds >= 2.8 + 0.015,
          `Cut [${dec.sourceCutTimeSeconds}, ${cutEnd}] violated word boundary [2.0, 2.8]`
        );
      }
    }
  });

  it("applies 10ms micro-crossfade to audio cuts", () => {
    const words = [
      { word: "Uno", start: 0.5, end: 1.0 },
      { word: "Dos", start: 2.0, end: 2.5 },
    ];
    const transcript = createTranscript(words);

    const plan = VlogJumpCutEngine.createJumpCutPlan("proj_test", "asset_01", 3.5, transcript, undefined, undefined, undefined, {
      preserveNarrativePauses: false,
      microCrossfadeSeconds: 0.010,
    });

    const cuts = plan.decisions.filter((d) => d.action === "CUT_SILENCE");
    assert.ok(cuts.length >= 1);
    for (const cut of cuts) {
      assert.equal(cut.microCrossfadeSeconds, 0.010);
    }
  });

  it("verifies duration accounting invariant: resultDuration = originalDuration - removedDuration", () => {
    const words = [
      { word: "Start", start: 1.0, end: 2.0 },
      { word: "Middle", start: 3.5, end: 4.5 },
      { word: "End", start: 6.0, end: 7.0 },
    ];
    const transcript = createTranscript(words);

    const plan = VlogJumpCutEngine.createJumpCutPlan("proj_test", "asset_01", 8.0, transcript, undefined, undefined, undefined, {
      preserveNarrativePauses: false,
    });

    const original = plan.statistics.originalDurationSeconds;
    const removed = plan.statistics.totalTimeSavedSeconds;
    const edited = plan.statistics.editedDurationSeconds;

    assert.ok(Math.abs(edited - (original - removed)) < 0.01, `Accounting mismatch: ${edited} != ${original} - ${removed}`);

    // Invariante de segmentos retenidos contiguos
    for (let i = 0; i < plan.retainedSegments.length - 1; i++) {
      const current = plan.retainedSegments[i];
      const next = plan.retainedSegments[i + 1];
      assert.equal(current.timelineEndSeconds, next.timelineStartSeconds);
      assert.ok(current.timelineEndSeconds > current.timelineStartSeconds);
    }
  });

  it("handles empty transcript and edge cases safely", () => {
    const planEmpty = VlogJumpCutEngine.createJumpCutPlan("proj_test", "asset_01", 5.0, undefined);
    assert.equal(planEmpty.retainedSegments.length, 1);
    assert.equal(planEmpty.retainedSegments[0].durationSeconds, 5.0);
  });

  it("PBT: for any valid sequence of words, no cut ever penetrates a word's boundary", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 1.0, max: 5.0, noNaN: true }),
        fc.double({ min: 0.5, max: 2.0, noNaN: true }),
        fc.double({ min: 0.3, max: 3.0, noNaN: true }),
        (w1Start, w1Dur, gap) => {
          const w1End = w1Start + w1Dur;
          const w2Start = w1End + gap;
          const w2End = w2Start + 1.0;
          const totalDur = w2End + 2.0;

          const transcript = createTranscript([
            { word: "WordA", start: w1Start, end: w1End },
            { word: "WordB", start: w2Start, end: w2End },
          ]);

          const plan = VlogJumpCutEngine.createJumpCutPlan("proj_test", "asset_pbt", totalDur, transcript);

          for (const dec of plan.decisions) {
            if (dec.action === "CUT_SILENCE") {
              const cutStart = dec.sourceCutTimeSeconds;
              const cutEnd = cutStart + dec.silenceDurationRemovedSeconds;

              // El corte no puede solaparse con WordA ni WordB
              const overlapsW1 = cutStart < w1End && cutEnd > w1Start;
              const overlapsW2 = cutStart < w2End && cutEnd > w2Start;

              assert.ok(!overlapsW1, `Cut overlapped WordA: [${cutStart}, ${cutEnd}] vs [${w1Start}, ${w1End}]`);
              assert.ok(!overlapsW2, `Cut overlapped WordB: [${cutStart}, ${cutEnd}] vs [${w2Start}, ${w2End}]`);
            }
          }
        }
      )
    );
  });
});
