import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  VisualMetaphorEngine,
  DirectorIntent,
  StyleBible,
} from "../../editorial/director/index.js";
import { VideoFrameAnalyzer } from "../../editorial/perception/video-frame-analyzer.js";
import { ShotIndexRecord } from "../../editorial/perception/perception.types.js";

describe("P4 — Visual Metaphor, Director Intent & Style Bible (REQ-015, REQ-070, REQ-071)", () => {
  // Test shots
  const shotVastDesert: ShotIndexRecord = {
    shotId: "shot_desert_01",
    sourceAssetId: "asset_01",
    sourceAssetHash: "hash_01",
    startTimeSeconds: 0,
    durationSeconds: 5,
    visualFeatures: VideoFrameAnalyzer.analyzeShot({
      shotId: "shot_desert_01",
      sourceAssetId: "asset_01",
      startTimeSeconds: 0,
      durationSeconds: 5,
      description: "Solitary person alone in vast empty desert distance",
      tags: ["solitary", "alone", "empty"],
    }),
    detectedSubjects: ["solitary", "alone", "desert"],
    embedding: new Array(128).fill(0),
    modelProvenance: {
      providerType: "DETERMINISTIC_HEURISTIC",
      modelId: "test",
      modelVersion: "1.0",
      modelHash: "hash",
      runtime: "test",
    },
  };

  const shotSunrise: ShotIndexRecord = {
    shotId: "shot_sunrise_01",
    sourceAssetId: "asset_02",
    sourceAssetHash: "hash_02",
    startTimeSeconds: 0,
    durationSeconds: 4,
    visualFeatures: VideoFrameAnalyzer.analyzeShot({
      shotId: "shot_sunrise_01",
      sourceAssetId: "asset_02",
      startTimeSeconds: 0,
      durationSeconds: 4,
      description: "Golden hour sunrise over horizon with open sky",
      tags: ["sunrise", "horizon", "dawn", "golden hour"],
    }),
    detectedSubjects: ["sunrise", "dawn", "horizon"],
    embedding: new Array(128).fill(0),
    modelProvenance: {
      providerType: "DETERMINISTIC_HEURISTIC",
      modelId: "test",
      modelVersion: "1.0",
      modelHash: "hash",
      runtime: "test",
    },
  };

  it("REQ-015: translates abstract concepts (ISOLATION, HOPE) into visual metaphor candidates with structured explanations", () => {
    // 1. Metaphor for ISOLATION
    const isolationCandidates = VisualMetaphorEngine.findMetaphorCandidates({
      concept: "ISOLATION",
      availableShots: [shotVastDesert, shotSunrise],
    });

    assert.ok(isolationCandidates.length >= 1);
    assert.equal(isolationCandidates[0].candidateShotId, "shot_desert_01");
    assert.ok(isolationCandidates[0].semanticScore >= 60.0);
    assert.ok(isolationCandidates[0].explanation.includes("ISOLATION"));

    // 2. Metaphor for HOPE
    const hopeCandidates = VisualMetaphorEngine.findMetaphorCandidates({
      concept: "HOPE",
      availableShots: [shotVastDesert, shotSunrise],
    });

    assert.ok(hopeCandidates.length >= 1);
    assert.equal(hopeCandidates[0].candidateShotId, "shot_sunrise_01");
    assert.ok(hopeCandidates[0].semanticScore >= 60.0);
    assert.ok(hopeCandidates[0].explanation.includes("HOPE"));
  });

  it("REQ-015: enforces repetition penalty and flags low confidence for Human Review", () => {
    // Repeated shot should have lower continuityFit
    const repeatedCandidates = VisualMetaphorEngine.findMetaphorCandidates({
      concept: "ISOLATION",
      availableShots: [shotVastDesert],
      recentShotIds: ["shot_desert_01"], // already recently used!
    });

    assert.ok(repeatedCandidates.length >= 1);
    assert.ok(repeatedCandidates[0].continuityFit < 0.8);

    // Candidate with low confidence requires human review
    const lowConfCandidate = VisualMetaphorEngine.findMetaphorCandidates({
      concept: "ISOLATION",
      availableShots: [shotVastDesert],
      confidenceThreshold: 0.99, // very strict threshold
    });

    assert.equal(lowConfCandidate[0].requiresHumanReview, true);
  });

  it("REQ-070: creates declarative, versioned Director's Intent and compiles constraints", () => {
    const intent = DirectorIntent.createDefaultDocumentaryIntent();
    assert.equal(intent.config.tone, "INVESTIGATIVE");
    assert.ok(intent.canonicalHash.length === 64);

    const constraints = intent.compileConstraints();
    assert.equal(constraints.requireProofForClaims, true);
    assert.equal(constraints.preferredJCutLcut, true);
    assert.ok(constraints.minShotDuration >= 1.5);
  });

  it("REQ-071: audits Style Bible compliance and flags STYLE_VIOLATION findings", () => {
    const bible = new StyleBible();
    assert.ok(bible.canonicalHash.length === 64);

    // Audit valid items
    const cleanAudit = bible.auditEditorialStyle({
      usedFonts: ["Impact", "Arial Black"],
      usedTransitions: ["HARD_CUT"],
    });
    assert.equal(cleanAudit.length, 0);

    // Audit disallowed font and kitsch transition
    const violatedAudit = bible.auditEditorialStyle({
      usedFonts: ["Comic Sans MS", "Impact"],
      usedTransitions: ["STAR_WIPE"],
    });

    assert.equal(violatedAudit.length, 2);
    assert.ok(violatedAudit.some((f) => f.ruleId === "STYLE_VIOLATION_FONT" && f.severity === "BLOCKING"));
    assert.ok(violatedAudit.some((f) => f.ruleId === "STYLE_VIOLATION_TRANSITION" && f.severity === "WARNING"));
  });
});
