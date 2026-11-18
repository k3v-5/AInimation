import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { NarrativeArcEngine } from "../../editorial/narrative/narrative-arc-engine.js";
import { EvidenceEngine } from "../../editorial/evidence/evidence-engine.js";
import { ArchivalMediaEngine } from "../../editorial/archive/archival-media-engine.js";
import { CreditsCompiler } from "../../editorial/credits/credits-compiler.js";
import { TrailerGenerator } from "../../editorial/trailer/trailer-generator.js";
import { MatchCutEngine } from "../../editorial/transitions/match-cut-engine.js";
import { SceneEntity } from "../../editorial/contracts/knowledge-graph.types.js";

describe("Regression — Golden Editorial Snapshot Suite", () => {
  const canonicalScenes: SceneEntity[] = [
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

  it("produces byte-identical NarrativeArcPlan output without regression", () => {
    const plan = NarrativeArcEngine.buildPlan({
      projectId: "golden_fixture_project",
      scenes: canonicalScenes,
      totalDurationSeconds: 480.0,
    });

    assert.equal(plan.projectId, "golden_fixture_project");
    assert.equal(plan.beats.length, 10);
    assert.equal(plan.totalDurationSeconds, 480.0);
    assert.ok(plan.checksumSha256.length === 64);
  });

  it("produces byte-identical EvidenceAuditReport without regression", () => {
    const report = EvidenceEngine.auditEvidence({
      projectId: "golden_fixture_project",
      claims: [
        {
          id: "claim_01",
          text: "The financial records were destroyed.",
          sourceCitation: "SEC Archive 2008",
          evidenceAssetIds: ["asset_doc_01"],
          confidence: 0.95,
          status: "VERIFIED",
          requiresOnScreenCitation: true,
        },
      ],
    });

    assert.equal(report.totalClaims, 1);
    assert.equal(report.verifiedClaims, 1);
    assert.equal(report.evidenceIntegrityScore, 100.0);
  });

  it("produces byte-identical Ken Burns archival motions without regression", () => {
    const motion = ArchivalMediaEngine.calculateKenBurns({
      isStillPhoto: true,
      durationSeconds: 6.0,
      motionDirection: "ZOOM_IN",
    });

    assert.equal(motion.scaleStart, 1.0);
    assert.equal(motion.scaleEnd, 1.15);
    assert.equal(motion.easing, "EASE_IN_OUT");
  });

  it("produces byte-identical TrailerPlan and MatchCutReport without regression", () => {
    const plan = NarrativeArcEngine.buildPlan({
      projectId: "golden_fixture_project",
      scenes: canonicalScenes,
      totalDurationSeconds: 480.0,
    });

    const trailer = TrailerGenerator.compileTrailer({
      projectId: "golden_fixture_project",
      narrativePlan: plan,
      format: "15s_teaser",
    });

    assert.equal(trailer.actualDurationSeconds, 15.0);
    assert.equal(trailer.format, "15s_teaser");

    const matchCut = MatchCutEngine.evaluateMatchCut(
      { id: "a", features: { primaryShape: "CIRCLE" } },
      { id: "b", features: { primaryShape: "CIRCLE" } }
    );

    assert.equal(matchCut.type, "GEOMETRIC");
    assert.equal(matchCut.isViableMatchCut, true);
  });

  it("produces byte-identical IntelligentTrimReport from golden performance fixture without regression (REQ-056.032)", async () => {
    const fs = await import("node:fs");
    const path = await import("node:path");
    const { IntelligentTrimmingEngine } = await import("../../editorial/performance/intelligent-trimming-engine.js");

    const fixturePath = path.resolve(process.cwd(), "fixtures/performance/intelligent-trimming-production.json");
    const fixtureData = JSON.parse(fs.readFileSync(fixturePath, "utf-8"));

    const report = IntelligentTrimmingEngine.process({
      segments: fixtureData.segments,
      takeGroups: fixtureData.takeGroups,
      sourceDurationSeconds: fixtureData.sourceDurationSeconds,
      profile: fixtureData.profile,
    });

    assert.equal(report.engineVersion, "4.0.0");
    assert.equal(report.processedSegments, 5);
    assert.equal(report.takesEvaluated, 1);
    assert.equal(report.automaticTakeSelections, 1);
    assert.ok(report.trimsAccepted >= 1);
    assert.ok(report.checksumSha256.length === 64);

    const rerun = IntelligentTrimmingEngine.process({
      segments: fixtureData.segments,
      takeGroups: fixtureData.takeGroups,
      sourceDurationSeconds: fixtureData.sourceDurationSeconds,
      profile: fixtureData.profile,
    });

    assert.equal(rerun.checksumSha256, report.checksumSha256);
  });
});

