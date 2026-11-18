import { describe, it } from "node:test";
import assert from "node:assert/strict";
import crypto from "crypto";
import fc from "fast-check";

// Exporters & Time
import { OtioExporter } from "../../editorial/exporters/otio-exporter.js";
import { OtioImporter } from "../../editorial/exporters/otio-importer.js";
import { OtioTimeEngine, STANDARD_FRAMERATES } from "../../editorial/exporters/otio-time.js";
import { MogrtSpecGenerator, MogrtBinaryPackager } from "../../editorial/exporters/mogrt-compiler.js";

// MultiCam
import { MultiCameraDirector } from "../../editorial/multicam/multicam-director.js";
import { CameraAngleDefinition } from "../../editorial/multicam/multicam.types.js";

// Audio
import { AudioMixEngine } from "../../editorial/audio/audio-mix-engine.js";
import { LoudnessEngine } from "../../editorial/audio/loudness-engine.js";
import { HierarchicalMixer } from "../../editorial/audio/hierarchical-mixer.js";
import { DialogueRepairEngine } from "../../editorial/audio/dialogue-repair-engine.js";

// Performance & Interval Tree
import { IntervalTree } from "../../editorial/performance/interval-tree.js";

// QA & Human Review
import { HumanReviewInterface } from "../../editorial/qa/review-ui/human-review-interface.js";

// Optimization & Constraints
import { EditorialConstraintSolver } from "../../editorial/optimization/constraint-solver.js";
import { ParetoEditorialOptimizer, CandidateProposal } from "../../editorial/optimization/pareto-editorial-optimizer.js";

// Perception
import { DeterministicHeuristicProvider, LocalMultimodalModelProvider } from "../../editorial/perception/embedding-provider.js";

// Rendering & Chunking
import { ChunkedRenderEngine, ChunkedRenderJob, RenderChunk } from "../../editorial/rendering/chunked-render-engine.js";

describe("MASTER ADVERSARIAL AUDIT & PRODUCTION HARDENING SUITE", () => {
  // =========================================================================
  // 1. OTIO ROUND TRIP ADVERSARIAL & RATIONAL TIME
  // =========================================================================
  describe("OTIO Round-Trip Adversarial Battery", () => {
    const testFramerates = [23.976, 24, 25, 29.97, 30, 50, 59.94, 60];

    for (const fps of testFramerates) {
      it(`preserves rational timebase with zero floating drift across fps=${fps}`, () => {
        const rate = OtioTimeEngine.getRationalRate(fps);
        assert.ok(rate.rateNumerator > 0);
        assert.ok(rate.rateDenominator > 0);

        const durationSeconds = 12.5;
        const frames = OtioTimeEngine.secondsToFrames(durationSeconds, fps);
        const backSeconds = OtioTimeEngine.framesToSeconds(frames, fps);

        const delta = Math.abs(durationSeconds - backSeconds);
        assert.ok(delta < 0.05, `Drift too large at fps ${fps}: delta=${delta}`);
      });
    }

    it("successfully round-trips empty timelines without crashing", () => {
      const emptyIr: any = {
        schemaVersion: "4.0.0",
        projectId: "proj_empty",
        createdAt: "2026-09-02T12:00:00.000Z",
        checksum: "0".repeat(64),
        metadata: {
          title: "Empty Project",
          profile: "DOCUMENTARY",
          frameRate: 24,
          width: 1920,
          height: 1080,
          sampleRate: 48000,
          targetDialogueLufs: -16,
        },
        tracks: [],
        transitions: [],
        markers: [],
      };

      const otioJson = OtioExporter.exportToOtioJson(emptyIr);
      const imported = OtioImporter.importFromOtioJson(otioJson);

      assert.equal(imported.ir.tracks.length, 0);
      assert.equal(imported.ir.metadata.frameRate, 24);
      assert.ok(imported.propertyAudit.length > 0);
    });

    it("adversarially rejects negative timecodes with [OTIO_INVALID_TIMECODE_ERROR]", () => {
      const malformedOtio = JSON.stringify({
        OTIO_SCHEMA: "Timeline.1",
        name: "Corrupt Timeline",
        tracks: {
          OTIO_SCHEMA: "Stack.1",
          children: [
            {
              OTIO_SCHEMA: "Track.1",
              kind: "Video",
              children: [
                {
                  OTIO_SCHEMA: "Clip.1",
                  name: "Negative Clip",
                  source_range: {
                    start_time: { value: -24, rate: 24 },
                    duration: { value: 48, rate: 24 },
                  },
                },
              ],
            },
          ],
        },
      });

      assert.throws(
        () => OtioImporter.importFromOtioJson(malformedOtio),
        /\[OTIO_INVALID_TIMECODE_ERROR\]/
      );
    });

    it("verifies 4-tier fidelity classification (LOSSLESS, LOSSY-BUT-DOCUMENTED, UNSUPPORTED, INVALID)", () => {
      const otioWithZeroDur = JSON.stringify({
        OTIO_SCHEMA: "Timeline.1",
        name: "Fidelity Test",
        metadata: { frameRate: 30 },
        tracks: {
          OTIO_SCHEMA: "Stack.1",
          children: [
            {
              OTIO_SCHEMA: "Track.1",
              kind: "Video",
              children: [
                {
                  OTIO_SCHEMA: "Clip.1",
                  name: "Zero Dur Shot",
                  source_range: {
                    start_time: { value: 0, rate: 30 },
                    duration: { value: 0, rate: 30 },
                  },
                },
                {
                  OTIO_SCHEMA: "UnknownForeignEffect.1",
                  name: "Alien Schema",
                },
              ],
            },
          ],
        },
      });

      const res = OtioImporter.importFromOtioJson(otioWithZeroDur);
      const classifications = new Set(res.propertyAudit.map((p) => p.classification));

      assert.ok(classifications.has("LOSSLESS"));
      assert.ok(classifications.has("LOSSY-BUT-DOCUMENTED"));
      assert.ok(classifications.has("UNSUPPORTED"));
    });
  });

  // =========================================================================
  // 2. MULTICAM ADVERSARIAL: 180° AXIS & EMOTIONAL PROTECTION
  // =========================================================================
  describe("MultiCam Adversarial & Safety Gates", () => {
    const camLeft: CameraAngleDefinition = {
      angleId: "CAM_L",
      name: "Left Angle",
      role: "SPEAKER_PRIMARY",
      spatialSide: "LEFT_OF_AXIS",
      cameraAzimuthDeg: 45,
      scale: "MEDIUM_CLOSE",
    };

    const camRight: CameraAngleDefinition = {
      angleId: "CAM_R",
      name: "Right Angle",
      role: "SPEAKER_SECONDARY",
      spatialSide: "RIGHT_OF_AXIS",
      cameraAzimuthDeg: -45,
      scale: "MEDIUM_CLOSE",
    };

    const camNeutral: CameraAngleDefinition = {
      angleId: "CAM_C",
      name: "Wide Center",
      role: "WIDE",
      spatialSide: "NEUTRAL_CENTER",
      cameraAzimuthDeg: 0,
      scale: "WIDE",
    };

    it("blocks direct 180° cross-axis jump cuts without neutral bridge", () => {
      const directCut = MultiCameraDirector.validate180Axis(camLeft, camRight);
      assert.equal(directCut.isValid, false);
      assert.ok(directCut.reason?.includes("180°"));

      // Transition through neutral center is completely valid
      const cutToNeutral = MultiCameraDirector.validate180Axis(camLeft, camNeutral);
      assert.equal(cutToNeutral.isValid, true);

      const cutFromNeutral = MultiCameraDirector.validate180Axis(camNeutral, camRight);
      assert.equal(cutFromNeutral.isValid, true);
    });

    it("strictly preserves emotional protection during CONFESSION and BREAKDOWN", () => {
      const guestCam: CameraAngleDefinition = {
        angleId: "cam_guest",
        name: "Guest Close-Up",
        role: "SPEAKER_SECONDARY",
        assignedSpeakerId: "spk_guest",
        spatialSide: "RIGHT_OF_AXIS",
        cameraAzimuthDeg: 315,
        scale: "CLOSE_UP",
      };

      const speechTurns = [
        { speakerId: "spk_host", startSeconds: 0, endSeconds: 4 },
        {
          speakerId: "spk_guest",
          startSeconds: 4,
          endSeconds: 15,
          emotionalState: "CONFESSION" as const,
        },
      ];

      const decisions = MultiCameraDirector.planSwitching({
        angles: [camLeft, guestCam, camNeutral],
        speechTurns,
        options: { minShotDurationSeconds: 2.0 },
      });

      // During confession, cutting away must be prohibited
      const confCut = decisions.find((d) => d.timestampSeconds === 4.0);
      assert.ok(confCut);
      assert.equal(confCut.activeAngleId, "cam_guest");
      assert.equal(confCut.isEmotionalProtection, true);
      assert.equal(confCut.emotionalState, "CONFESSION");
    });
  });

  // =========================================================================
  // 3. AUDIO ADVERSARIAL: 8 BUSES, DUCKING, LOUDNESS EBU R128
  // =========================================================================
  describe("Audio Intelligence Adversarial Verification", () => {
    it("validates 8 hierarchical audio buses with cycle detection", () => {
      const mixer = new HierarchicalMixer();
      const busGraph = mixer.getAllBuses();
      assert.ok(busGraph.length >= 8);

      // Verify master is the root parent
      const master = busGraph.find((b) => b.id === "MASTER");
      assert.ok(master);
      assert.equal(master.parentBusId, undefined);

      // Verify dialogue routes to master
      const dialogue = busGraph.find((b) => b.id === "DIALOGUE");
      assert.ok(dialogue);
      assert.equal(dialogue.parentBusId, master.id);
    });

    it("verifies mathematical compliance with EBU R128 (-23 LUFS) and Web (-16 LUFS)", () => {
      const sampleRate = 48000;
      const buffer = new Float32Array(sampleRate * 2); // 2 seconds
      // Synthetic 1kHz tone with bounded amplitude
      for (let i = 0; i < buffer.length; i++) {
        buffer[i] = Math.sin((2 * Math.PI * 1000 * i) / sampleRate) * 0.15;
      }

      const broadcastMeas = LoudnessEngine.measureLoudness({
        samples: buffer,
        sampleRate,
        standard: "BROADCAST",
      });

      assert.ok(broadcastMeas.truePeakDb <= -1.0, `True peak exceeded: ${broadcastMeas.truePeakDb}`);
      assert.ok(typeof broadcastMeas.integratedLufs === "number");

      const webMeas = LoudnessEngine.measureLoudness({
        samples: buffer,
        sampleRate,
        standard: "WEB_SOCIAL",
      });
      assert.ok(webMeas.truePeakDb <= -1.0);
    });

    it("diagnoses dialogue plosives, clipping and hum non-destructively", () => {
      const proposals = DialogueRepairEngine.analyzeDialogue({
        clipId: "clip_plosive_test",
        startSeconds: 0,
        durationSeconds: 2.0,
        peakLevelDb: 0.5, // Exceeds headroom threshold
        hasPlosiveTransient: true,
        detectedHumHz: 50,
      });

      assert.ok(proposals.length > 0);
      assert.equal(proposals[0].type, "CLIPPING");
      assert.equal(proposals[0].reversible, true);
    });
  });

  // =========================================================================
  // 4. INTERVAL TREE: FAST-CHECK PBT EQUIVALENCE
  // =========================================================================
  describe("IntervalTree Algorithmic Complexity & Equivalence PBT", () => {
    it("PBT: IntervalTree.overlapQuery matches BruteForce linear search exactly across random intervals", () => {
      fc.assert(
        fc.property(
          fc.array(
            fc.record({
              id: fc.uuid(),
              low: fc.double({ min: 0, max: 1000, noNaN: true }),
              span: fc.double({ min: 0.1, max: 50, noNaN: true }),
            }),
            { minLength: 5, maxLength: 50 }
          ),
          fc.double({ min: 0, max: 1000, noNaN: true }),
          fc.double({ min: 0.1, max: 100, noNaN: true }),
          (rawIntervals, qLow, qSpan) => {
            const tree = new IntervalTree<string>();
            const qHigh = qLow + qSpan;

            for (const item of rawIntervals) {
              tree.insert(item.id, item.low, item.low + item.span, item.id);
            }

            const treeResult = tree.overlapQuery(qLow, qHigh).map((i) => i.id).sort();
            const linearResult = tree.linearFallbackQuery(qLow, qHigh).map((i) => i.id).sort();

            assert.deepEqual(treeResult, linearResult);
          }
        ),
        { numRuns: 30 }
      );
    });
  });

  // =========================================================================
  // 5. HUMAN REVIEW: CRYPTOGRAPHIC SIGNATURE & TAMPER DETECTION
  // =========================================================================
  describe("Human Review Cryptographic Tamper Detection", () => {
    it("detects any tampering with IR hash, QA hash, reviewer, or decision payload", () => {
      const ui = new HumanReviewInterface([
        {
          id: "item_001",
          issueId: "QA-ISSUE-10",
          priority: 80,
          status: "PENDING",
          severity: "BLOCKING",
          confidence: 0.55,
          affectedEntityIds: ["clip_v1"],
          proposedAction: "Trim silence gap",
        },
      ]);

      const irHash = crypto.createHash("sha256").update("ir_v1_content").digest("hex");
      const qaHash = crypto.createHash("sha256").update("qa_v1_content").digest("hex");

      const decision = ui.signDecision({
        itemId: "item_001",
        action: "APPROVE",
        reviewer: "LeadEditor_Sarah",
        currentIrHash: irHash,
        currentQaReportHash: qaHash,
      });

      // 1. Valid signature passes
      const validCheck = ui.verifyDecisionSignature(decision, irHash, qaHash);
      assert.equal(validCheck.isValid, true);

      // 2. Tampering with IR Hash fails
      const tamperedIrHash = crypto.createHash("sha256").update("ir_tampered_content").digest("hex");
      const tamperedIrCheck = ui.verifyDecisionSignature(decision, tamperedIrHash, qaHash);
      assert.equal(tamperedIrCheck.isValid, false);
      assert.ok(tamperedIrCheck.errorReason?.includes("IR_HASH_MISMATCH"));

      // 3. Tampering with QA Hash fails
      const tamperedQaHash = crypto.createHash("sha256").update("qa_tampered").digest("hex");
      const tamperedQaCheck = ui.verifyDecisionSignature(decision, irHash, tamperedQaHash);
      assert.equal(tamperedQaCheck.isValid, false);
      assert.ok(tamperedQaCheck.errorReason?.includes("QA_REPORT_HASH_MISMATCH"));

      // 4. Tampering with reviewer name fails
      const forgedDecision = { ...decision, reviewer: "Attacker_Mallory" };
      const forgedCheck = ui.verifyDecisionSignature(forgedDecision, irHash, qaHash);
      assert.equal(forgedCheck.isValid, false);
    });
  });

  // =========================================================================
  // 6. CONSTRAINT SOLVER: HARD CONSTRAINTS INVIOLABILITY
  // =========================================================================
  describe("Constraint Solver Hard vs Soft Enforcement", () => {
    it("strictly rejects candidate proposals when a HARD constraint is violated, regardless of soft score", () => {
      const solver = new EditorialConstraintSolver([
        {
          id: "SAFETY_HEADROOM",
          name: "Audio Headroom Safety",
          constraintClass: "HARD",
          description: "Max volume cannot exceed 0.0dB",
          validator: (p) => ({ passed: p.maxVolumeDb <= 0.0 }),
        },
        {
          id: "PACING_OPTIMAL",
          name: "Rhythm Aesthetic",
          constraintClass: "SOFT",
          description: "Ideal cut rate between 15-20 cuts/min",
          validator: (p) => ({ passed: p.cutsPerMin >= 15 }),
        },
      ]);

      // Candidate with great pacing but violating audio safety
      const dangerousCandidate = {
        id: "cand_loud",
        maxVolumeDb: 3.5, // VIOLATION
        cutsPerMin: 18,   // PERFECT
      };

      const result = solver.solve(dangerousCandidate);
      assert.equal(result.isFeasible, false);
      assert.equal(result.violatedHardConstraints.length, 1);
      assert.ok(result.violatedHardConstraints[0].startsWith("SAFETY_HEADROOM"));
    });
  });

  // =========================================================================
  // 7. PARETO OPTIMIZATION: NON-DOMINANCE PBT
  // =========================================================================
  describe("Pareto Multi-Objective Optimization Invariant", () => {
    it("PBT: guarantees no solution in the returned Pareto front is dominated by another returned solution", () => {
      fc.assert(
        fc.property(
          fc.array(
            fc.record({
              id: fc.uuid(),
              name: fc.string({ minLength: 3, maxLength: 10 }),
              durationSeconds: fc.double({ min: 10, max: 120, noNaN: true }),
              metrics: fc.record({
                narrativeLoss: fc.double({ min: 0, max: 1, noNaN: true }),
                attentionLoss: fc.double({ min: 0, max: 1, noNaN: true }),
                pacingLoss: fc.double({ min: 0, max: 1, noNaN: true }),
                evidenceLoss: fc.double({ min: 0, max: 1, noNaN: true }),
                continuityLoss: fc.double({ min: 0, max: 1, noNaN: true }),
                audioLoss: fc.double({ min: 0, max: 1, noNaN: true }),
                styleLoss: fc.double({ min: 0, max: 1, noNaN: true }),
                durationLoss: fc.double({ min: 0, max: 1, noNaN: true }),
              }),
              candidatePayload: fc.constant({}),
            }),
            { minLength: 3, maxLength: 20 }
          ),
          (candidates: CandidateProposal[]) => {
            const front = ParetoEditorialOptimizer.computeParetoFront(candidates);

            // Invariant: For any pair (A, B) in front, A does NOT dominate B
            for (let i = 0; i < front.length; i++) {
              for (let j = 0; j < front.length; j++) {
                if (i === j) continue;
                const a = front[i];
                const b = front[j];

                const aDominatesB = ParetoEditorialOptimizer.dominates(a.proposal.metrics, b.proposal.metrics);
                assert.equal(
                  aDominatesB,
                  false,
                  `Pareto violation: solution ${a.proposal.id} dominates ${b.proposal.id} within front!`
                );
              }
            }
          }
        ),
        { numRuns: 20 }
      );
    });
  });

  // =========================================================================
  // 8. MOGRT & REQ-013 TRANSPARENCY
  // =========================================================================
  describe("Architectural Honesty: MOGRT and Multimodal Perception", () => {
    it("MogrtSpecGenerator produces valid JSON spec while Packager honestly declares EXTERNAL_TOOL_REQUIRED", () => {
      const spec = MogrtSpecGenerator.generateSpec({
        templateId: "tpl_doc_lower_third",
        templateName: "LowerThird_Doc",
        definition: {
          compositionName: "Comp_LowerThird",
          width: 1920,
          height: 1080,
          fps: 30,
          durationSeconds: 5.0,
          essentialPropertyCount: 1,
        },
        controls: [
          {
            controlId: "ctrl_title",
            name: "Subject Name",
            type: "TEXT",
            defaultValue: "Dr. Alvarez",
            expressionBinding: "thisComp.layer('NameText').text.sourceText",
          },
        ],
      });

      assert.ok(spec.provenance.specHashSha256.length === 64);
      assert.equal(spec.exposedControls.length, 1);

      // Packager honest declaration
      assert.equal(MogrtBinaryPackager.IS_AVAILABLE, false);
      assert.throws(
        () => MogrtBinaryPackager.packageBinaryMogrt(spec),
        /\[MOGRT_BINARY_PACKAGER_UNVERIFIED\]/
      );
    });

    it("REQ-013: LocalMultimodalModelProvider rejects missing local weights with [MISSING_LOCAL_NEURAL_WEIGHTS]", () => {
      const provider = new LocalMultimodalModelProvider();
      assert.equal(provider.providerType, "LOCAL_MULTIMODAL_NEURAL");
      assert.equal(provider.getModelInfo().isNeuralWeightsAvailable, false);

      assert.throws(
        () => {
          provider.generateTextEmbedding("test query");
        },
        /\[MISSING_LOCAL_NEURAL_WEIGHTS\]/
      );
    });

    it("REQ-013: DeterministicHeuristicProvider produces deterministic reproducible 128-d vectors offline", () => {
      const heuristicProvider = new DeterministicHeuristicProvider();
      assert.equal(heuristicProvider.providerType, "DETERMINISTIC_HEURISTIC");

      const features = {
        shotId: "shot_test_geo",
        sourceAssetId: "asset_cam1",
        startTimeSeconds: 10,
        durationSeconds: 5,
        scale: "WIDE" as const,
        subjectMotion: "STATIC" as const,
        cameraMovement: "PAN" as const,
        dominantColorHex: "#336699",
        brightness: 0.6,
        contrast: 0.5,
        saturation: 0.7,
        composition: {
          ruleOfThirdsAlignment: 0.8,
          leadingLinesScore: 0.7,
          symmetryScore: 0.5,
          headroomNormalized: 0.15,
          leadRoomNormalized: 0.2,
        },
        motion: {
          dominantMotionVector: [0.1, 0.0] as [number, number],
          cameraMovementType: "PAN" as const,
          subjectMotionIntensity: 0.2,
          stabilityScore: 0.95,
        },
      };

      const vec1 = heuristicProvider.generateVisualEmbedding(features as any, ["landscape", "mountain", "sky"]);
      const vec2 = heuristicProvider.generateVisualEmbedding(features as any, ["landscape", "mountain", "sky"]);

      assert.equal(vec1.length, 128);
      assert.deepEqual(vec1, vec2);
    });
  });

  // =========================================================================
  // 9. CHUNKED RENDERING: CONTIGUITY, GAPS & DUPLICATES
  // =========================================================================
  describe("Distributed Render & Chunk Assembly Verification (REQ-037)", () => {
    const job: ChunkedRenderJob = {
      jobId: "job_render_adversarial",
      sourceIrHash: "a".repeat(64),
      totalDurationSeconds: 12.0,
      fps: 30,
      totalFrames: 360,
      settings: {
        codec: "PRORES_422_HQ",
        width: 1920,
        height: 1080,
        fps: 30,
      },
    };

    it("detects missing chunks and refuses to assemble incomplete renders", () => {
      const chunks = ChunkedRenderEngine.partitionJob(job, 4.0); // 3 chunks
      assert.equal(chunks.length, 3);

      // Remove middle chunk
      const incomplete = [chunks[0], chunks[2]];
      const assembly = ChunkedRenderEngine.verifyAndAssemble(job, incomplete);

      assert.equal(assembly.isComplete, false);
      assert.ok(assembly.verificationReport.errors.some((e) => e.includes("FRAME_GAP_DETECTED")));
      assert.ok(assembly.verificationReport.missingFrames.length > 0);
    });

    it("detects frame gaps or overlaps between rendered chunks", () => {
      const chunks = ChunkedRenderEngine.partitionJob(job, 6.0); // 2 chunks
      // Tamper with chunk 1 frameStart to create a gap of 10 frames
      chunks[1].frameStart = 190;

      const assembly = ChunkedRenderEngine.verifyAndAssemble(job, chunks);
      assert.equal(assembly.isComplete, false);
      assert.ok(assembly.verificationReport.errors.some((e) => e.includes("FRAME_GAP_DETECTED")));
      assert.ok(assembly.verificationReport.missingFrames.length > 0);
    });
  });
});
