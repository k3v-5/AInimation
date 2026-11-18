import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { SceneEntity } from "../../editorial/contracts/knowledge-graph.types.js";
import { NarrativeArcEngine } from "../../editorial/narrative/narrative-arc-engine.js";
import { TrailerGenerator } from "../../editorial/trailer/trailer-generator.js";

describe("Fase 4F — Trailer & Teaser Generator Suite", () => {
  const sampleScenes: SceneEntity[] = [
    { id: "sc_01", name: "The Sudden Crisis", participantIds: [], narrativeImportance: 0.9, estimatedDurationSeconds: 40.0 },
    { id: "sc_02", name: "Historical Context", participantIds: [], narrativeImportance: 0.6, estimatedDurationSeconds: 50.0 },
    { id: "sc_03", name: "The Unanswered Question", participantIds: [], narrativeImportance: 0.7, estimatedDurationSeconds: 45.0 },
    { id: "sc_04", name: "Uncovering the Evidence", participantIds: [], narrativeImportance: 0.8, estimatedDurationSeconds: 60.0 },
    { id: "sc_05", name: "Eyewitness Testimonies", participantIds: [], narrativeImportance: 0.6, estimatedDurationSeconds: 40.0 },
    { id: "sc_06", name: "Emerging Conflict", participantIds: [], narrativeImportance: 0.8, estimatedDurationSeconds: 55.0 },
    { id: "sc_07", name: "Escalation & Tension", participantIds: [], narrativeImportance: 0.9, estimatedDurationSeconds: 65.0 },
    { id: "sc_08", name: "The Hidden Truth Revealed", participantIds: [], narrativeImportance: 1.0, estimatedDurationSeconds: 50.0 },
    { id: "sc_09", name: "Fallout and Resolution", participantIds: [], narrativeImportance: 0.5, estimatedDurationSeconds: 40.0 },
    { id: "sc_10", name: "Final Reflections", participantIds: [], narrativeImportance: 0.4, estimatedDurationSeconds: 35.0 },
  ];

  const narrativePlan = NarrativeArcEngine.buildPlan({
    projectId: "doc_master_trailer_test",
    scenes: sampleScenes,
    totalDurationSeconds: 480.0,
  });

  it("compiles a 15s teaser with contiguous timeline placement and exact duration budget (REQ-028)", () => {
    const plan = TrailerGenerator.compileTrailer({
      projectId: "doc_master_trailer_test",
      narrativePlan,
      format: "15s_teaser",
    });

    assert.equal(plan.format, "15s_teaser");
    assert.equal(plan.targetDurationSeconds, 15.0);
    assert.equal(plan.actualDurationSeconds, 15.0);
    assert.ok(plan.segments.length >= 3);

    // Verify timeline contiguity: seg[i].trailerEndSeconds === seg[i+1].trailerStartSeconds
    for (let i = 0; i < plan.segments.length - 1; i++) {
      const current = plan.segments[i];
      const next = plan.segments[i + 1];
      assert.equal(
        current.trailerEndSeconds,
        next.trailerStartSeconds,
        `Contiguity broken between segment ${i} and ${i + 1}`
      );
    }

    assert.equal(plan.segments[0].trailerStartSeconds, 0.0);
    assert.equal(plan.segments[plan.segments.length - 1].trailerEndSeconds, 15.0);
  });

  it("compiles 30s promo and 60s trailer containing high-energy beats: HOOK, ESCALATION, REVELATION", () => {
    const promo = TrailerGenerator.compileTrailer({
      projectId: "doc_master_trailer_test",
      narrativePlan,
      format: "30s_promo",
    });

    assert.equal(promo.actualDurationSeconds, 30.0);
    const promoBeats = promo.segments.map((s) => s.sourceBeatType);
    assert.ok(promoBeats.includes("HOOK"));
    assert.ok(promoBeats.includes("REVELATION"));

    const trailer60 = TrailerGenerator.compileTrailer({
      projectId: "doc_master_trailer_test",
      narrativePlan,
      format: "60s_trailer",
    });

    assert.equal(trailer60.actualDurationSeconds, 60.0);
    const trailerBeats = trailer60.segments.map((s) => s.sourceBeatType);
    assert.ok(trailerBeats.includes("HOOK"));
    assert.ok(trailerBeats.includes("EVIDENCE"));
    assert.ok(trailerBeats.includes("REVELATION"));
  });

  it("guarantees 100% deterministic SHA-256 plan checksum across runs", () => {
    const run1 = TrailerGenerator.compileTrailer({
      projectId: "doc_master_trailer_test",
      narrativePlan,
      format: "30s_promo",
    });

    const run2 = TrailerGenerator.compileTrailer({
      projectId: "doc_master_trailer_test",
      narrativePlan,
      format: "30s_promo",
    });

    assert.equal(run1.checksumSha256, run2.checksumSha256);
    assert.equal(run1.checksumSha256.length, 64);
  });

  it("PBT: trailer actual duration is strictly equal to target duration within float epsilon", () => {
    fc.assert(
      fc.property(
        fc.constantFrom("15s_teaser", "30s_promo", "60s_trailer", "90s_epic"),
        (format) => {
          const plan = TrailerGenerator.compileTrailer({
            projectId: "pbt_trailer_test",
            narrativePlan,
            format: format as any,
          });

          const diff = Math.abs(plan.actualDurationSeconds - plan.targetDurationSeconds);
          return diff <= 0.05;
        }
      ),
      { numRuns: 30 }
    );
  });
});
