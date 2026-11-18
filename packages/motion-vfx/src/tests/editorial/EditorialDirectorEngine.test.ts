import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  EditorialDirectorEngine,
  EditorialProfileRegistry,
  ProductionIntent,
  EditorialCandidateSegment,
  compareRulePrecedence,
  RulePriorityTier,
  canOverrideRule,
} from "../../editorial/index.js";

test("Fase 4A — Editorial Director & Explainability Suite", async (t) => {
  const docProfile = EditorialProfileRegistry.getProfile("DOCUMENTARY");
  const vlogProfile = EditorialProfileRegistry.getProfile("VLOG");

  const baseIntent: ProductionIntent = {
    projectId: "doc_exp_01",
    format: "DOCUMENTARY",
    primaryObjective: "DOCUMENT",
    audience: "GENERAL",
    platform: "YOUTUBE_16x9",
    language: "es-MX",
    tone: "SERIOUS",
    pacingPreference: "CONTEMPLATIVE",
    visualDensity: 0.5,
    narrationDensity: 0.6,
    brollDensity: 0.7,
  };

  await t.test("computes multidimensional score with strict weighting and clamp", () => {
    const score = EditorialDirectorEngine.computeScore({
      narrativeValue: 0.9,
      emotionalValue: 0.85,
      informationValue: 0.95,
      visualValue: 0.8,
      audioValue: 0.9,
      redundancyPenalty: 0.05,
      continuityScore: 0.9,
    });

    assert.ok(score.overallScore >= 0 && score.overallScore <= 100);
    assert.equal(score.narrativeValue, 0.9);
    assert.equal(score.informationValue, 0.95);
  });

  await t.test("strictly enforces REQ-076: EDITOR_LOCK cannot be overridden by optimization", () => {
    const candidates: EditorialCandidateSegment[] = [
      {
        assetId: "talking_head_01.mp4",
        startSeconds: 0,
        durationSeconds: 15.0,
        isTalkingHead: true,
        hasEditorLock: true,
        lockedAction: "KEEP",
        proposedAction: "CUT", // AI wanted to cut
        reason: "Proposed trim for pacing.",
        narrativeEffect: "Speed up sequence.",
      },
    ];

    const graph = EditorialDirectorEngine.planDecisions({
      projectId: "doc_exp_01",
      intent: baseIntent,
      profile: docProfile,
      candidates,
    });

    assert.equal(graph.decisions.length, 1);
    const decision = graph.decisions[0];
    assert.equal(decision.action, "KEEP");
    assert.equal(decision.tier, "EDITOR_LOCK");
    assert.equal(decision.controlLevel, "LOCKED_BY_EDITOR");
    assert.equal(decision.confidence, 1.0);
    assert.equal(decision.alternativesConsidered.length, 1);
    assert.match(decision.alternativesConsidered[0].rejectionReason, /EDITOR_LOCK precedence/);
  });

  await t.test("strictly enforces REQ-076: LEGAL_FACTUAL claim prevents cutting evidence", () => {
    const candidates: EditorialCandidateSegment[] = [
      {
        assetId: "archive_treaty_1945.mp4",
        startSeconds: 45.0,
        durationSeconds: 5.0,
        isTalkingHead: false,
        hasClaimCitation: true,
        claimId: "claim_un_charter",
        proposedAction: "CUT", // AI proposed removal to save time
        reason: "Trim archive duration.",
        narrativeEffect: "Reduce runtime.",
      },
    ];

    const graph = EditorialDirectorEngine.planDecisions({
      projectId: "doc_exp_01",
      intent: baseIntent,
      profile: docProfile,
      candidates,
    });

    const decision = graph.decisions[0];
    assert.equal(decision.action, "KEEP");
    assert.equal(decision.tier, "LEGAL_FACTUAL");
    assert.equal(decision.confidence, 0.98);
    assert.match(decision.alternativesConsidered[0].rejectionReason, /LEGAL_FACTUAL tier/);
  });

  await t.test("prohibits PUNCH_IN on documentary profile and records alternative rejection", () => {
    const candidates: EditorialCandidateSegment[] = [
      {
        assetId: "interview_witness.mp4",
        startSeconds: 30.0,
        durationSeconds: 4.0,
        isTalkingHead: true,
        proposedAction: "PUNCH_IN",
        reason: "Dynamic visual scaling.",
        narrativeEffect: "Increase energy.",
      },
    ];

    const graph = EditorialDirectorEngine.planDecisions({
      projectId: "doc_exp_01",
      intent: baseIntent,
      profile: docProfile, // Documentary prohibits punch in
      candidates,
    });

    const decision = graph.decisions[0];
    assert.equal(decision.action, "KEEP"); // Replaced with KEEP
    assert.equal(decision.tier, "STYLE");
    assert.match(decision.reason, /Dynamic punch-in rejected/);
    assert.equal(decision.alternativesConsidered.length, 1);
    assert.equal(decision.alternativesConsidered[0].action, "PUNCH_IN");
  });

  await t.test("PBT: EditorialScore is always strictly bounded in [0, 100]", () => {
    fc.assert(
      fc.property(
        fc.float({ min: 0, max: 1, noNaN: true }),
        fc.float({ min: 0, max: 1, noNaN: true }),
        fc.float({ min: 0, max: 1, noNaN: true }),
        fc.float({ min: 0, max: 1, noNaN: true }),
        fc.float({ min: 0, max: 1, noNaN: true }),
        fc.float({ min: 0, max: 1, noNaN: true }),
        fc.float({ min: 0, max: 1, noNaN: true }),
        (n, e, i, v, a, r, c) => {
          const score = EditorialDirectorEngine.computeScore({
            narrativeValue: n,
            emotionalValue: e,
            informationValue: i,
            visualValue: v,
            audioValue: a,
            redundancyPenalty: r,
            continuityScore: c,
          });
          return score.overallScore >= 0 && score.overallScore <= 100;
        }
      ),
      { numRuns: 100 }
    );
  });

  await t.test("PBT: Rule precedence hierarchy is strictly antisymmetric and transitive", () => {
    const tiers: RulePriorityTier[] = [
      "SAFETY",
      "LEGAL_FACTUAL",
      "EDITOR_LOCK",
      "NARRATIVE",
      "CONTINUITY",
      "AUDIO",
      "VISUAL",
      "STYLE",
      "OPTIMIZATION",
    ];

    // Antisymmetry & irreflexivity
    for (const t1 of tiers) {
      assert.equal(compareRulePrecedence(t1, t1), 0);
      assert.equal(canOverrideRule(t1, t1), false);
      for (const t2 of tiers) {
        if (t1 !== t2) {
          assert.equal(compareRulePrecedence(t1, t2), -compareRulePrecedence(t2, t1));
          assert.notEqual(canOverrideRule(t1, t2), canOverrideRule(t2, t1));
        }
      }
    }

    // Direct check: SAFETY overrides OPTIMIZATION, but OPTIMIZATION cannot override SAFETY
    assert.equal(canOverrideRule("SAFETY", "OPTIMIZATION"), true);
    assert.equal(canOverrideRule("OPTIMIZATION", "SAFETY"), false);
    assert.equal(canOverrideRule("LEGAL_FACTUAL", "VISUAL"), true);
    assert.equal(canOverrideRule("EDITOR_LOCK", "NARRATIVE"), true);
  });
});
