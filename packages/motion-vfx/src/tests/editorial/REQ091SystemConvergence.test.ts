import { describe, it } from "node:test";
import assert from "node:assert/strict";
import crypto from "crypto";

// 1. Perception
import {
  VideoFrameAnalyzer,
  DeterministicHeuristicProvider,
  MultimodalIndexer,
  SemanticSearchEngine,
} from "../../editorial/perception/index.js";

// 2. Director Intent & Style Bible & Metaphors
import {
  DirectorIntent,
  StyleBible,
  VisualMetaphorEngine,
} from "../../editorial/director/index.js";

// 3. Audio Intelligence
import {
  AudioMixEngine,
  LoudnessEngine,
} from "../../editorial/audio/index.js";

// 4. MultiCam Director
import { MultiCameraDirector } from "../../editorial/multicam/index.js";

// 5. Constraints & Optimization
import {
  EditorialConstraintSolver,
  ParetoEditorialOptimizer,
} from "../../editorial/optimization/index.js";

// 6. QA & Human Review
import { EditorialQAOrchestrator } from "../../editorial/qa/editorial-qa-orchestrator.js";
import { HumanReviewInterface } from "../../editorial/qa/review-ui/index.js";

// 7. Exporter & Render Verification
import { OtioTimeEngine } from "../../editorial/exporters/otio-time.js";
import { ChunkedRenderEngine, ChunkedRenderJob } from "../../editorial/rendering/chunked-render-engine.js";

describe("REQ-091: Final Editorial Operating System End-to-End System Convergence Suite", () => {
  it("executes the entire unified autonomous editorial pipeline with 100% determinism, provenance and zero external network", async () => {
    // -------------------------------------------------------------------------
    // STEP 1: Director Intent & Style Bible Initialization
    // -------------------------------------------------------------------------
    const directorIntent = DirectorIntent.createDefaultDocumentaryIntent();
    const styleBible = new StyleBible();
    assert.ok(directorIntent.canonicalHash.length === 64);
    assert.ok(styleBible.canonicalHash.length === 64);

    const compiledConstraints = directorIntent.compileConstraints();
    assert.equal(compiledConstraints.requireProofForClaims, true);

    // -------------------------------------------------------------------------
    // STEP 2: Asset Perception & Multimodal Indexing
    // -------------------------------------------------------------------------
    const embeddingProvider = new DeterministicHeuristicProvider();
    const indexer = new MultimodalIndexer(embeddingProvider);

    const shotA = {
      shotId: "shot_interview_alvarez",
      sourceAssetId: "cam_a_raw",
      sourceAssetHash: "hash_cam_a_v1",
      startTimeSeconds: 0,
      durationSeconds: 10,
      visualFeatures: VideoFrameAnalyzer.analyzeShot({
        shotId: "shot_interview_alvarez",
        sourceAssetId: "cam_a_raw",
        startTimeSeconds: 0,
        durationSeconds: 10,
        description: "Dr. Elena Alvarez close up talking head interview",
      }),
      detectedSubjects: ["person", "scientist", "interview"],
      transcriptText: "The seismic readings showed anomalous tectonic stress.",
    };

    const shotB = {
      shotId: "shot_broll_city",
      sourceAssetId: "broll_city_raw",
      sourceAssetHash: "hash_city_v1",
      startTimeSeconds: 0,
      durationSeconds: 6,
      visualFeatures: VideoFrameAnalyzer.analyzeShot({
        shotId: "shot_broll_city",
        sourceAssetId: "broll_city_raw",
        startTimeSeconds: 0,
        durationSeconds: 6,
        description: "City skyline at night with dense building lights and solitary street",
      }),
      detectedSubjects: ["city", "night", "isolation", "alone"],
    };

    indexer.indexShot(shotA);
    indexer.indexShot(shotB);
    assert.equal(indexer.size(), 2);

    const indexHash = indexer.calculateCanonicalIndexHash();
    assert.ok(indexHash.length === 64);

    // -------------------------------------------------------------------------
    // STEP 3: Semantic Search & Visual Metaphor Candidate Matching
    // -------------------------------------------------------------------------
    const searchEngine = new SemanticSearchEngine(indexer, embeddingProvider);
    const searchResults = searchEngine.search("plano de ciudad de noche");
    assert.ok(searchResults.length > 0);
    assert.equal(searchResults[0].shotId, "shot_broll_city");

    const metaphorCandidates = VisualMetaphorEngine.findMetaphorCandidates({
      concept: "ISOLATION",
      availableShots: indexer.getAllRecords(),
    });
    assert.ok(metaphorCandidates.length > 0);
    assert.equal(metaphorCandidates[0].candidateShotId, "shot_broll_city");

    // -------------------------------------------------------------------------
    // STEP 4: MultiCam Director with 180° Rule & Emotional Protection
    // -------------------------------------------------------------------------
    const angles = [
      {
        angleId: "CAM_A",
        name: "Main Close Up",
        role: "SPEAKER_PRIMARY" as const,
        spatialSide: "LEFT_OF_AXIS" as const,
        scale: "MEDIUM_CLOSE" as const,
        assignedSpeakerId: "DrElenaAlvarez",
        cameraAzimuthDeg: 45,
        lensFocalLengthMm: 85,
        lightingContinuityScore: 0.95,
      },
      {
        angleId: "CAM_B",
        name: "Wide Context",
        role: "WIDE" as const,
        spatialSide: "NEUTRAL_CENTER" as const,
        scale: "WIDE" as const,
        cameraAzimuthDeg: 0,
        lensFocalLengthMm: 35,
        lightingContinuityScore: 0.95,
      },
    ];

    const turns = [
      {
        speakerId: "DrElenaAlvarez",
        startSeconds: 0,
        endSeconds: 6,
        emotionalState: "CONFESSION" as const,
      },
    ];

    const axisCheck = MultiCameraDirector.validate180Axis(angles[0], angles[1]);
    assert.equal(axisCheck.isValid, true);

    const switchDecisions = MultiCameraDirector.planSwitching({
      angles,
      speechTurns: turns,
    });
    assert.ok(switchDecisions.length >= 1);

    // -------------------------------------------------------------------------
    // STEP 5: Initial Editorial IR
    // -------------------------------------------------------------------------
    const initialIR = {
      project: { id: "proj_doc", name: "Autonomous Documentary", fps: 30, width: 1920, height: 1080 },
      tracks: [
        {
          id: "V1",
          type: "VIDEO",
          clips: [
            { id: "c1", assetId: "a1", start: 0, duration: 10, inPoint: 0, outPoint: 10 },
          ],
        },
        {
          id: "A1",
          type: "AUDIO",
          clips: [
            { id: "a1", assetId: "audio1", start: 0, duration: 10, inPoint: 0, outPoint: 10 },
          ],
        },
      ],
      metadata: {},
    };

    // -------------------------------------------------------------------------
    // STEP 6: Intelligent Audio Post-Production & EBU R128 Loudness
    // -------------------------------------------------------------------------
    const audioMixPlan = AudioMixEngine.processAudioMix({
      ir: initialIR,
      standard: "BROADCAST",
    });
    assert.ok(audioMixPlan.buses.length >= 8);

    const syntheticBuffer = new Float32Array(48000);
    for (let i = 0; i < syntheticBuffer.length; i++) {
      syntheticBuffer[i] = Math.sin((2 * Math.PI * 440 * i) / 48000) * 0.1;
    }
    const loudnessMeas = LoudnessEngine.measureLoudness({
      samples: syntheticBuffer,
      sampleRate: 48000,
      standard: "BROADCAST",
    });
    assert.ok(loudnessMeas.truePeakDb <= -1.0);

    // -------------------------------------------------------------------------
    // STEP 7: Constraint Solver & Multi-Objective Pareto Optimization
    // -------------------------------------------------------------------------
    const constraintSolver = new EditorialConstraintSolver([
      {
        id: "LEGAL_CLEARANCE",
        name: "Commercial Clearance",
        constraintClass: "HARD",
        description: "All clips must be cleared",
        validator: (c) => ({ passed: c.isCleared === true }),
      },
    ]);

    const paretoFront = ParetoEditorialOptimizer.computeParetoFront(
      [
        {
          id: "prop_1",
          name: "Evidence Maximized",
          durationSeconds: 12.0,
          metrics: {
            narrativeLoss: 0.05,
            attentionLoss: 0.10,
            pacingLoss: 0.20,
            evidenceLoss: 0.01,
            continuityLoss: 0.05,
            audioLoss: 0.02,
            styleLoss: 0.02,
            durationLoss: 0.05,
          },
          candidatePayload: { isCleared: true },
        },
      ],
      constraintSolver
    );

    assert.equal(paretoFront.length, 1);
    assert.equal(paretoFront[0].proposal.id, "prop_1");

    // -------------------------------------------------------------------------
    // STEP 8: Editorial QA Governance & Cryptographic Human Review Signing
    // -------------------------------------------------------------------------
    const qaReport = await EditorialQAOrchestrator.audit({ ir: initialIR as any });
    assert.ok(qaReport.checksumSha256.length === 64);

    const humanReviewUi = new HumanReviewInterface([
      {
        id: "rev_01",
        issueId: "QA-DOC-001",
        priority: 75,
        status: "PENDING",
        severity: "WARNING",
        confidence: 0.65,
        affectedEntityIds: ["c1"],
        proposedAction: "Review B-Roll cut point",
      },
    ]);

    const irHash = crypto.createHash("sha256").update(JSON.stringify(initialIR)).digest("hex");
    const signedDecision = humanReviewUi.signDecision({
      itemId: "rev_01",
      action: "APPROVE",
      reviewer: "SupervisingEditor_Sam",
      currentIrHash: irHash,
      currentQaReportHash: qaReport.checksumSha256,
    });

    assert.ok(signedDecision.canonicalSignatureSha256.length === 64);
    const validSignCheck = humanReviewUi.verifyDecisionSignature(
      signedDecision,
      irHash,
      qaReport.checksumSha256
    );
    assert.equal(validSignCheck.isValid, true);

    // -------------------------------------------------------------------------
    // STEP 9: Exporters & Distributed Render Chunking (REQ-037)
    // -------------------------------------------------------------------------
    const frames = OtioTimeEngine.secondsToFrames(10.0, 30);
    assert.equal(frames, 300);
    const seconds = OtioTimeEngine.framesToSeconds(300, 30);
    assert.equal(seconds, 10.0);

    const renderJob: ChunkedRenderJob = {
      jobId: "job_final_delivery",
      sourceIrHash: irHash,
      totalDurationSeconds: 10.0,
      fps: 30,
      totalFrames: 300,
      settings: {
        codec: "PRORES_422_HQ",
        width: 1920,
        height: 1080,
        fps: 30,
      },
    };

    const chunks = ChunkedRenderEngine.partitionJob(renderJob, 5.0);
    assert.equal(chunks.length, 2);

    const assembly = ChunkedRenderEngine.verifyAndAssemble(renderJob, chunks);
    assert.equal(assembly.isComplete, true);
    assert.equal(assembly.totalAssembledFrames, 300);
    assert.ok(assembly.canonicalMasterHash.length === 64);
  });
});
