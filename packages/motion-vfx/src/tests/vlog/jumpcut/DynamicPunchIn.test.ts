import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import {
  DynamicPunchIn,
  FaceTrack,
  PunchInCandidateTrigger,
} from "../../../vlog/index.js";

describe("Milestone 3 — Dynamic Punch-In Suite", () => {
  it("generates standard 115% punch-in and 112% micro punch-in", () => {
    const triggers: PunchInCandidateTrigger[] = [
      { timeSeconds: 1.0, trigger: "EMPHASIS_KEYWORD", holdDurationSeconds: 1.5 }, // Normal hold => 1.15
      { timeSeconds: 6.0, trigger: "EMPHASIS_KEYWORD", holdDurationSeconds: 0.4 }, // Micro hold (<0.5s) => 1.12
    ];

    const decisions = DynamicPunchIn.generatePunchIns(triggers);
    assert.equal(decisions.length, 2);
    assert.equal(decisions[0].targetScale, 1.15);
    assert.equal(decisions[0].originScale, 1.00);
    assert.equal(decisions[1].targetScale, 1.12);
  });

  it("enforces max scale ceiling of 120%", () => {
    const triggers: PunchInCandidateTrigger[] = [
      { timeSeconds: 2.0, trigger: "EMPHASIS_KEYWORD", holdDurationSeconds: 1.0 },
    ];

    // Solicitando escala abusiva de 1.50
    const decisions = DynamicPunchIn.generatePunchIns(triggers, undefined, {
      standardScale: 1.50,
    });

    assert.equal(decisions.length, 1);
    assert.equal(decisions[0].targetScale, 1.20); // Clamped to 1.20
  });

  it("enforces 3.0s cooldown and resolves conflicts by priority", () => {
    // Tres eventos dentro de una ventana de 2 segundos:
    // t = 1.0s (EMPHASIS, prioridad 1)
    // t = 2.0s (NARRATIVE_CLIMAX, prioridad 3) -> debe reemplazar al de t=1.0s porque tiene mayor jerarquía
    // t = 6.0s (TOPIC_SHIFT, prioridad 2) -> fuera de cooldown (6.0 - 2.0 = 4.0 >= 3.0s) -> se acepta
    const triggers: PunchInCandidateTrigger[] = [
      { timeSeconds: 1.0, trigger: "EMPHASIS_KEYWORD" },
      { timeSeconds: 2.0, trigger: "NARRATIVE_CLIMAX" },
      { timeSeconds: 6.0, trigger: "TOPIC_SHIFT" },
    ];

    const decisions = DynamicPunchIn.generatePunchIns(triggers, undefined, { cooldownSeconds: 3.0 });
    assert.equal(decisions.length, 2);
    assert.equal(decisions[0].trigger, "NARRATIVE_CLIMAX");
    assert.equal(decisions[0].timelineStartSeconds, 2.0);
    assert.equal(decisions[1].trigger, "TOPIC_SHIFT");
    assert.equal(decisions[1].timelineStartSeconds, 6.0);
  });

  it("centers punch-in on EyeAnchor when available", () => {
    const faceTracks: FaceTrack[] = [
      {
        trackId: "face_01",
        sourceMediaId: "media_01",
        isActiveSpeaker: true,
        samples: [
          {
            timeSeconds: 3.0,
            boundingBox: { x: 0.3, y: 0.2, width: 0.4, height: 0.5 },
            eyes: {
              normalizedX: 0.54,
              normalizedY: 0.32,
              interocularDistanceNormalized: 0.08,
              confidence: 0.95,
            },
            confidence: 0.98,
          },
        ],
      },
    ];

    const triggers: PunchInCandidateTrigger[] = [
      { timeSeconds: 3.0, trigger: "TOPIC_SHIFT" },
    ];

    const decisions = DynamicPunchIn.generatePunchIns(triggers, faceTracks);
    assert.equal(decisions.length, 1);
    // Debe orientarse hacia la posición ocular (0.54, 0.32) tras suavizado
    assert.ok(Math.abs(decisions[0].focalPointNormalized.x - 0.50) > 0.001);
  });

  it("defaults to composition center (0.5, 0.5) when face is unavailable", () => {
    const triggers: PunchInCandidateTrigger[] = [
      { timeSeconds: 1.0, trigger: "EMPHASIS_KEYWORD" },
    ];

    const decisions = DynamicPunchIn.generatePunchIns(triggers, undefined);
    assert.equal(decisions.length, 1);
    assert.equal(decisions[0].focalPointNormalized.x, 0.50);
    assert.equal(decisions[0].focalPointNormalized.y, 0.50);
  });

  it("suppresses punch-in when segment is covered by B-Roll (B-Roll Precedence Rule)", () => {
    const triggers: PunchInCandidateTrigger[] = [
      { timeSeconds: 1.0, trigger: "EMPHASIS_KEYWORD", coveredByBRoll: true },
      { timeSeconds: 5.0, trigger: "EMPHASIS_KEYWORD", coveredByBRoll: false },
    ];

    const decisions = DynamicPunchIn.generatePunchIns(triggers);
    assert.equal(decisions.length, 2);
    assert.equal(decisions[0].isSuppressedByBRoll, true);
    assert.equal(decisions[1].isSuppressedByBRoll, false);
  });

  it("PBT: target scale is strictly within (0, 1.20] and focal points within [0, 1]", () => {
    fc.assert(
      fc.property(
        fc.double({ min: -10.0, max: 100.0, noNaN: true }),
        fc.double({ min: 0.0, max: 10.0, noNaN: true }),
        (reqScale, hold) => {
          const triggers: PunchInCandidateTrigger[] = [
            { timeSeconds: 2.0, trigger: "NARRATIVE_CLIMAX", holdDurationSeconds: hold },
          ];

          const decisions = DynamicPunchIn.generatePunchIns(triggers, undefined, {
            standardScale: reqScale,
          });

          if (decisions.length > 0) {
            const dec = decisions[0];
            assert.ok(dec.targetScale > 0.0 && dec.targetScale <= 1.20, `Scale out of bounds: ${dec.targetScale}`);
            assert.ok(dec.focalPointNormalized.x >= 0.0 && dec.focalPointNormalized.x <= 1.0);
            assert.ok(dec.focalPointNormalized.y >= 0.0 && dec.focalPointNormalized.y <= 1.0);
            assert.ok(!isNaN(dec.targetScale));
            assert.ok(isFinite(dec.targetScale));
          }
        }
      )
    );
  });
});
