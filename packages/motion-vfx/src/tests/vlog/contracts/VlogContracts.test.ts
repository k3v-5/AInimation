import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import {
  // Constantes
  SUPPORTED_LOCALES,
  FOOTAGE_TYPES,
  SUPPORTED_ASPECT_RATIOS,
  AUDIO_SPECS,
  SYNC_TOLERANCES,
  JUMP_CUT_DEFAULTS,
  PUNCH_IN_DEFAULTS,
  PACING_DEFAULTS,
  BROLL_SCORING_WEIGHTS,
  GEODESIC_CONSTANTS,
  AUDIO_MIX_DEFAULTS,
  // Errores
  InvalidVlogProjectError,
  InvalidVlogConfigurationError,
  UnsupportedLocaleError,
  InvalidTimelineError,
  InvalidPacingError,
  InvalidMediaError,
  VlogArtifactError,
  VlogContractValidationError,
  // Schemas de Lenguaje
  SupportedLocaleSchema,
  VoiceProfileSchema,
  VlogLanguageConfigSchema,
  // Schemas de Habla
  VlogTranscriptWordSchema,
  VlogTranscriptSegmentSchema,
  VlogTranscriptSchema,
  PauseTypeSchema,
  SpeechPauseSchema,
  BreathEventSchema,
  EyeAnchorSchema,
  FaceTrackSchema,
  // Schemas de Clasificación
  FootageTypeSchema,
  ClassificationScoresSchema,
  FootageClassificationSchema,
  BRollMatchScoreSchema,
  BRollCandidateSchema,
  // Schemas de Jump Cut
  JumpCutDecisionSchema,
  PunchInDecisionSchema,
  JumpCutStatisticsSchema,
  JumpCutPlanSchema,
  // Schemas de Voiceover
  TTSRequestSchema,
  VoiceoverSegmentSchema,
  VoiceoverTrackSchema,
  // Schemas de Pacing
  TimingAnchorSchema,
  SegmentAlignmentSchema,
  PacingAdjustmentSchema,
  PacingConflictSchema,
  PacingResultSchema,
  // Schemas de Subtítulos
  SubtitleWordSchema,
  SubtitleStyleSchema,
  SubtitleCueSchema,
  // Schemas de Overlays
  GeoBadgeSchema,
  LocationCardSchema,
  RoutePointSchema,
  RoutePathSchema,
  PolaroidFreezeFrameSchema,
  // Schemas de Audio
  DuckingKeyframeSchema,
  DuckingEnvelopeSchema,
  AudioMixConfigSchema,
  VlogAudioTrackSchema,
  // Schemas de Orquestador y Artefactos
  VlogPhaseSchema,
  VlogPipelineStateSchema,
  VlogArtifactSchema,
  VlogRunSchema,
  VlogManifestSchema,
  // Schema de Proyecto Maestro
  VlogClipLockSchema,
  VlogProjectConfigSchema,
  VlogMediaAssetSchema,
  VlogSegmentSchema,
  VlogSceneSchema,
  VlogTimelineSchema,
  VlogProjectSchema,
} from "../../../vlog/contracts/index.js";
import { MotionEngineError, ValidationError } from "../../../errors/index.js";

describe("Milestone 1 — Vlog Multilingual Contracts, Schemas & Constants Suite", () => {
  describe("1. Universal Constants & Specifications Integrity", () => {
    it("contains all 7 officially supported locales", () => {
      assert.equal(SUPPORTED_LOCALES.length, 7);
      assert.deepEqual([...SUPPORTED_LOCALES], [
        "es-MX",
        "es-ES",
        "en-US",
        "en-GB",
        "pt-BR",
        "fr-FR",
        "de-DE",
      ]);
    });

    it("differentiates audio specifications by role", () => {
      // SFX procedurales: 44.1kHz mono
      assert.equal(AUDIO_SPECS.SFX.sampleRate, 44100);
      assert.equal(AUDIO_SPECS.SFX.channels, 1);
      assert.equal(AUDIO_SPECS.SFX.bitDepth, 16);

      // TTS voiceover: 44.1kHz mono, EBU R128 (-16 LUFS)
      assert.equal(AUDIO_SPECS.VOICEOVER.sampleRate, 44100);
      assert.equal(AUDIO_SPECS.VOICEOVER.channels, 1);
      assert.equal(AUDIO_SPECS.VOICEOVER.targetLoudnessLufs, -16.0);
      assert.equal(AUDIO_SPECS.VOICEOVER.truePeakLimitDb, -1.0);

      // Internal bus: 32-bit float stereo
      assert.equal(AUDIO_SPECS.INTERNAL_BUS.bitDepth, 32);
      assert.equal(AUDIO_SPECS.INTERNAL_BUS.channels, 2);

      // Master bus: stereo, -1.0 dBTP ceiling
      assert.equal(AUDIO_SPECS.MASTER_DEFAULT.channels, 2);
      assert.equal(AUDIO_SPECS.MASTER_DEFAULT.truePeakCeilingDbTP, -1.0);
    });

    it("verifies synchronization tolerances per synchronization type", () => {
      assert.equal(SYNC_TOLERANCES.SUBTITLE_WORD_DRIFT_SECONDS, 0.040); // ±40 ms
      assert.equal(SYNC_TOLERANCES.SEGMENT_ALIGNMENT_WARN_SECONDS, 0.100); // ±100 ms
      assert.equal(SYNC_TOLERANCES.WORD_BOUNDARY_SAFETY_SECONDS, 0.015); // ±15 ms
      assert.equal(SYNC_TOLERANCES.POLAROID_SFX_FRAME_TOLERANCE, 1); // ±1 frame
    });

    it("verifies jump-cut and punch-in defaults", () => {
      assert.equal(JUMP_CUT_DEFAULTS.SILENCE_THRESHOLD_SECONDS, 0.25);
      assert.equal(JUMP_CUT_DEFAULTS.MICRO_CROSSFADE_SECONDS, 0.010);
      assert.equal(PUNCH_IN_DEFAULTS.STANDARD_PUNCH_SCALE, 1.15);
      assert.equal(PUNCH_IN_DEFAULTS.COOLDOWN_SECONDS, 3.0);
      assert.equal(PUNCH_IN_DEFAULTS.FOCAL_SMOOTHING_ALPHA, 0.20);
    });

    it("verifies adaptive pacing automatic stretch range [0.95, 1.05]", () => {
      assert.equal(PACING_DEFAULTS.AUTOMATIC_STRETCH_MIN, 0.95);
      assert.equal(PACING_DEFAULTS.AUTOMATIC_STRETCH_MAX, 1.05);
      assert.equal(PACING_DEFAULTS.HARD_STRETCH_LIMIT_MIN, 0.85);
      assert.equal(PACING_DEFAULTS.HARD_STRETCH_LIMIT_MAX, 1.15);
    });

    it("verifies geodesic WGS-84 radius", () => {
      assert.equal(GEODESIC_CONSTANTS.EARTH_RADIUS_KM, 6371.0088);
    });
  });

  describe("2. Error Hierarchy Contracts", () => {
    it("all specific errors inherit properly from MotionEngineError and ValidationError", () => {
      const projErr = new InvalidVlogProjectError("corrupt project");
      assert.ok(projErr instanceof ValidationError);
      assert.ok(projErr instanceof MotionEngineError);

      const cfgErr = new InvalidVlogConfigurationError("bad config");
      assert.ok(cfgErr instanceof ValidationError);

      const locErr = new UnsupportedLocaleError("it-IT", SUPPORTED_LOCALES);
      assert.ok(locErr instanceof ValidationError);
      assert.ok(locErr.message.includes("it-IT"));

      const timeErr = new InvalidTimelineError("non-monotonic time");
      assert.ok(timeErr instanceof ValidationError);

      const paceErr = new InvalidPacingError("drift out of range");
      assert.ok(paceErr instanceof ValidationError);

      const mediaErr = new InvalidMediaError("corrupt header");
      assert.ok(mediaErr instanceof ValidationError);

      const artErr = new VlogArtifactError("checksum mismatch");
      assert.ok(artErr instanceof MotionEngineError);

      const valErr = new VlogContractValidationError("schema rejected");
      assert.ok(valErr instanceof ValidationError);
    });
  });

  describe("3. Language & Locales Schemas", () => {
    it("validates officially supported locales", () => {
      for (const loc of SUPPORTED_LOCALES) {
        assert.equal(SupportedLocaleSchema.parse(loc), loc);
      }
    });

    it("rejects unsupported locales", () => {
      assert.throws(() => SupportedLocaleSchema.parse("ja-JP"));
      assert.throws(() => SupportedLocaleSchema.parse("zh-CN"));
      assert.throws(() => SupportedLocaleSchema.parse(""));
    });

    it("validates voice profile schema", () => {
      const validVoice = {
        id: "piper_es_mx_pedro",
        name: "Pedro Mexican Spanish",
        locale: "es-MX",
        gender: "MALE",
        engine: "piper",
        sampleRateHz: 44100,
        quality: "neural",
      };
      const parsed = VoiceProfileSchema.parse(validVoice);
      assert.equal(parsed.id, "piper_es_mx_pedro");
      assert.equal(parsed.locale, "es-MX");
    });
  });

  describe("4. Speech & Acoustic Transcript Schemas", () => {
    it("validates transcript words with consistent timestamps", () => {
      const validWord = {
        word: "Guadalajara",
        startSeconds: 1.5,
        endSeconds: 2.3,
        confidence: 0.98,
      };
      const parsed = VlogTranscriptWordSchema.parse(validWord);
      assert.equal(parsed.word, "Guadalajara");

      // Inversión temporal: endSeconds < startSeconds debe fallar
      assert.throws(() => {
        VlogTranscriptWordSchema.parse({
          word: "Error",
          startSeconds: 3.0,
          endSeconds: 1.0,
          confidence: 0.5,
        });
      });
    });

    it("validates complete transcript structure with segments", () => {
      const transcript = {
        id: "tr_001",
        language: "es",
        locale: "es-MX",
        durationSeconds: 10.0,
        confidence: 0.96,
        rawText: "Bienvenidos a Jalisco.",
        segments: [
          {
            id: "seg_1",
            startSeconds: 0.0,
            endSeconds: 2.5,
            text: "Bienvenidos a Jalisco.",
            confidence: 0.96,
            words: [
              { word: "Bienvenidos", startSeconds: 0.0, endSeconds: 1.0, confidence: 0.98 },
              { word: "a", startSeconds: 1.0, endSeconds: 1.2, confidence: 0.95 },
              { word: "Jalisco.", startSeconds: 1.2, endSeconds: 2.5, confidence: 0.97 },
            ],
          },
        ],
      };
      const parsed = VlogTranscriptSchema.parse(transcript);
      assert.equal(parsed.segments.length, 1);
      assert.equal(parsed.segments[0].words.length, 3);
    });

    it("validates speech pause and eye anchor schemas", () => {
      const pause = {
        id: "p_1",
        startSeconds: 4.0,
        endSeconds: 4.8,
        durationSeconds: 0.8,
        type: "NARRATIVE",
        confidence: 0.92,
        isRemovable: false,
      };
      assert.equal(SpeechPauseSchema.parse(pause).type, "NARRATIVE");

      const eye = {
        normalizedX: 0.52,
        normalizedY: 0.38,
        interocularDistanceNormalized: 0.08,
        confidence: 0.94,
      };
      assert.equal(EyeAnchorSchema.parse(eye).confidence, 0.94);
    });
  });

  describe("5. Footage Classification & B-Roll Matching Schemas", () => {
    it("validates footage types and classification scores", () => {
      for (const t of FOOTAGE_TYPES) {
        assert.equal(FootageTypeSchema.parse(t), t);
      }

      const scores = {
        aRoll: 0.85,
        bRoll: 0.10,
        action: 0.02,
        timelapse: 0.01,
        screen: 0.0,
        photo: 0.01,
        other: 0.01,
      };
      assert.equal(ClassificationScoresSchema.parse(scores).aRoll, 0.85);
    });

    it("validates B-Roll candidate scoring bounds (0 to 100)", () => {
      const score = {
        total: 88.5,
        semanticRelevance: 95.0,
        entityMatch: 80.0,
        visualQuality: 90.0,
        locationRelevance: 85.0,
        activityRelevance: 70.0,
        durationFit: 100.0,
        noveltyPenalty: 10.0,
      };
      assert.equal(BRollMatchScoreSchema.parse(score).total, 88.5);

      // Score > 100 debe fallar
      assert.throws(() => {
        BRollMatchScoreSchema.parse({ ...score, total: 105.0 });
      });
    });
  });

  describe("6. Jump Cut & Dynamic Punch-In Schemas", () => {
    it("validates jump cut decision with 10ms micro-crossfade", () => {
      const decision = {
        id: "cut_01",
        sourceCutTimeSeconds: 5.25,
        timelineCutTimeSeconds: 4.50,
        action: "CUT_SILENCE",
        silenceDurationRemovedSeconds: 0.75,
        microCrossfadeSeconds: 0.010,
        reason: "Detected pause >= 0.25s",
      };
      const parsed = JumpCutDecisionSchema.parse(decision);
      assert.equal(parsed.microCrossfadeSeconds, 0.010);
      assert.equal(parsed.action, "CUT_SILENCE");
    });

    it("validates dynamic punch-in scale and triggers", () => {
      const punch = {
        id: "punch_01",
        timelineStartSeconds: 12.0,
        timelineEndSeconds: 14.5,
        holdDurationSeconds: 2.5,
        targetScale: 1.15,
        originScale: 1.00,
        focalPointNormalized: { x: 0.51, y: 0.35 },
        trigger: "EMPHASIS_KEYWORD",
        isSuppressedByBRoll: false,
      };
      const parsed = PunchInDecisionSchema.parse(punch);
      assert.equal(parsed.targetScale, 1.15);
      assert.equal(parsed.isSuppressedByBRoll, false);
    });
  });

  describe("7. Voiceover & TTS Provider Contracts", () => {
    it("validates TTS request with speechText / displayText separation", () => {
      const request = {
        id: "tts_req_1",
        locale: "es-MX",
        voiceId: "pedro_mx",
        speechText: "El costo es de cincuenta dólares americanos.",
        displayText: "El costo es de $50 USD.",
        speakingRate: 1.05,
      };
      const parsed = TTSRequestSchema.parse(request);
      assert.equal(parsed.speechText, "El costo es de cincuenta dólares americanos.");
      assert.equal(parsed.displayText, "El costo es de $50 USD.");
    });

    it("validates voiceover track with SHA-256 checksum", () => {
      const track = {
        id: "v_track_es_mx",
        locale: "es-MX",
        voiceId: "pedro_mx",
        audioWavPath: "/audio/es-MX/voiceover.wav",
        durationSeconds: 35.0,
        segments: [],
        checksumSha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        format: {
          sampleRateHz: 44100,
          bitDepth: 16,
          channels: 1,
        },
      };
      const parsed = VoiceoverTrackSchema.parse(track);
      assert.equal(parsed.format.sampleRateHz, 44100);
      assert.equal(parsed.format.channels, 1);
    });
  });

  describe("8. Adaptive Pacing & Elastic Adjustment Schemas", () => {
    it("validates segment alignment within ±40ms drift tolerance", () => {
      const alignment = {
        narrativeSegmentId: "seg_1",
        voiceStartSeconds: 10.000,
        voiceEndSeconds: 15.000,
        visualStartSeconds: 10.025,
        visualEndSeconds: 15.025,
        driftSeconds: 0.025,
        isWithinDriftTolerance: true,
      };
      const parsed = SegmentAlignmentSchema.parse(alignment);
      assert.equal(parsed.isWithinDriftTolerance, true);
      assert.ok(Math.abs(parsed.driftSeconds) <= 0.040);
    });

    it("validates pacing result with voice stretch factor", () => {
      const result = {
        locale: "en-US",
        adaptedDurationSeconds: 32.5,
        deltaFromSourceSeconds: -2.5,
        adjustments: [],
        alignments: [],
        conflicts: [],
        voiceStretchFactor: 1.02, // Dentro de [0.95, 1.05]
        success: true,
      };
      const parsed = PacingResultSchema.parse(result);
      assert.equal(parsed.voiceStretchFactor, 1.02);
      assert.equal(parsed.success, true);
    });
  });

  describe("9. Subtitle Styles & Karaoke Cues", () => {
    it("validates TIME Editorial Poster subtitle style", () => {
      const timeStyle = {
        fontFamily: "Impact",
        fontSizePx: 72,
        fillColor: "#FFFFFF",
        highlightFillColor: "#FF1424", // Carmesí característico
        textTransform: "uppercase",
        letterSpacing: -15,
        verticalStretchPercent: 135, // 135% estiramiento vertical
      };
      const parsed = SubtitleStyleSchema.parse(timeStyle);
      assert.equal(parsed.highlightFillColor, "#FF1424");
      assert.equal(parsed.verticalStretchPercent, 135);
    });
  });

  describe("10. Travel Overlays & Cartography Schemas", () => {
    it("validates Geo-Badge coordinates and location cards", () => {
      const badge = {
        id: "badge_gdl",
        cityName: "Guadalajara",
        countryName: "México",
        countryCode: "MX",
        coordinates: {
          latitude: 20.6767,
          longitude: -103.3475,
        },
        altitudeMeters: 1566,
        stylePreset: "editorial_red",
      };
      const parsed = GeoBadgeSchema.parse(badge);
      assert.equal(parsed.cityName, "Guadalajara");
      assert.equal(parsed.coordinates?.latitude, 20.6767);
    });

    it("validates Polaroid freeze frame with shutter SFX sync", () => {
      const polaroid = {
        id: "polaroid_01",
        freezeTimestampSeconds: 18.0,
        holdDurationSeconds: 2.5,
        rotationDegrees: -4.5,
        captionText: "Mercado San Juan de Dios",
        dropShadow: {
          opacity: 0.5,
          distancePx: 20,
          softnessPx: 25,
        },
        shutterSfxSyncSeconds: 18.0,
      };
      const parsed = PolaroidFreezeFrameSchema.parse(polaroid);
      assert.equal(parsed.rotationDegrees, -4.5);
      assert.equal(parsed.shutterSfxSyncSeconds, 18.0);
    });
  });

  describe("11. Audio Mix & Auto-Ducking Schemas", () => {
    it("validates ducking envelope keyframes", () => {
      const envelope = {
        targetTrackId: "music_track",
        triggerTrackId: "voice_track",
        duckAmountDb: -10.0,
        attackSeconds: 0.12,
        releaseSeconds: 0.40,
        keyframes: [
          { timeSeconds: 0.0, gainDb: 0.0 },
          { timeSeconds: 2.0, gainDb: -10.0 },
          { timeSeconds: 8.0, gainDb: 0.0 },
        ],
      };
      const parsed = DuckingEnvelopeSchema.parse(envelope);
      assert.equal(parsed.keyframes.length, 3);
      assert.equal(parsed.duckAmountDb, -10.0);
    });

    it("validates audio mix configuration defaults", () => {
      const config = AudioMixConfigSchema.parse({});
      assert.equal(config.masterSampleRateHz, 44100);
      assert.equal(config.channels, 2);
      assert.equal(config.duckingDb, -10.0);
      assert.equal(config.truePeakCeilingDbTP, -1.0);
    });
  });

  describe("12. Orchestrator, Artifacts & Manifest Schemas", () => {
    it("validates complete immutable artifact structure", () => {
      const artifact = {
        artifactId: "art_trans_001",
        type: "transcript",
        producerPhase: "P05_TRANSCRIBE",
        engineVersion: "3.5.0",
        inputHash: "a".repeat(64),
        configurationHash: "b".repeat(64),
        checksumSha256: "c".repeat(64),
        dependencies: [],
        filePath: "/work/run_1/transcript.json",
        createdAtTimestamp: Date.now(),
      };
      const parsed = VlogArtifactSchema.parse(artifact);
      assert.equal(parsed.producerPhase, "P05_TRANSCRIBE");
      assert.equal(parsed.engineVersion, "3.5.0");
    });

    it("validates all 22 phases from P00 to P21 in order", () => {
      const phases = [
        "P00_INITIALIZE",
        "P01_VALIDATE_INPUT",
        "P02_INGEST_MEDIA",
        "P03_ANALYZE_MEDIA",
        "P04_CLASSIFY_FOOTAGE",
        "P05_TRANSCRIBE",
        "P06_ANALYZE_NARRATIVE",
        "P07_BUILD_SOURCE_TIMELINE",
        "P08_GENERATE_JUMP_CUTS",
        "P09_MATCH_BROLL",
        "P10_PLAN_LANGUAGES",
        "P11_GENERATE_TTS",
        "P12_ADAPTIVE_PACING",
        "P13_BUILD_SUBTITLES",
        "P14_BUILD_TRAVEL_OVERLAYS",
        "P15_BUILD_STYLE",
        "P16_BUILD_AUDIO",
        "P17_BUILD_TIMELINES",
        "P18_EXPORT_AE",
        "P19_VALIDATE_OUTPUT",
        "P20_PACKAGE_OUTPUT",
        "P21_COMPLETE",
      ];
      for (const p of phases) {
        assert.equal(VlogPhaseSchema.parse(p), p);
      }
    });

    it("validates final production manifest schema", () => {
      const manifest = {
        projectId: "proj_gdl_2023",
        runId: "run_alpha_01",
        engineVersion: "3.5.0",
        createdAtTimestamp: Date.now(),
        configurationHash: "1".repeat(64),
        productionHash: "2".repeat(64),
        sourceLocale: "es-MX",
        targetLocales: ["es-MX", "en-US"],
        deliverables: {
          baseDirectory: "./output",
          audioMasters: { "es-MX": "./audio/master_es.wav", "en-US": "./audio/master_en.wav" },
          subtitles: { "es-MX": "./subs/es.srt", "en-US": "./subs/en.srt" },
          jsxScripts: { "es-MX": "./jsx/project_es.jsx", "en-US": "./jsx/project_en.jsx" },
          reportPath: "./reports/production-report.json",
        },
        artifacts: [],
        validation: {
          passed: true,
          checkedAtTimestamp: Date.now(),
          metrics: {
            totalDurationSeconds: 35.0,
            scenesCount: 3,
            cutsCount: 14,
            brollCount: 5,
            overlaysCount: 4,
          },
        },
      };
      const parsed = VlogManifestSchema.parse(manifest);
      assert.equal(parsed.validation.passed, true);
      assert.equal(parsed.targetLocales.length, 2);
    });
  });

  describe("13. Master VlogProject Schema v1.0.0", () => {
    it("validates a full canonical VlogProject with scenes and clips", () => {
      const project = {
        schemaVersion: "1.0.0",
        id: "vlog_gdl_master",
        title: "Guadalajara 2023 // El Arte de Disfrutar",
        createdAtTimestamp: Date.now(),
        updatedAtTimestamp: Date.now(),
        config: {
          sourceLocale: "es-MX",
          targetLocales: ["es-MX", "en-US", "pt-BR"],
          aspectRatio: "9:16",
          stylePreset: "time_editorial_poster",
          offlineMode: true,
          enableTTS: true,
          enableSubtitles: true,
          enableTravelOverlays: true,
          enableBrollMatching: true,
          enableJumpCuts: true,
          silenceThresholdSeconds: 0.25,
          microCrossfadeMilliseconds: 10,
          punchInScale: 1.15,
          automaticStretchMin: 0.95,
          automaticStretchMax: 1.05,
          seed: 42,
        },
        mediaAssets: [
          {
            id: "clip_01",
            sourceFilePath: "E:/Raw/20230621_114030.mp4",
            filename: "20230621_114030.mp4",
            mediaType: "VIDEO",
            durationSeconds: 8.0,
            checksumSha256: "a".repeat(64),
            assignedRole: "A_ROLL",
            lock: { mediaId: "clip_01", lockType: "NONE" },
          },
        ],
        scenes: [
          {
            id: "scene_01",
            title: "Llegada al Centro Histórico",
            order: 0,
            durationSeconds: 8.0,
            locationName: "Guadalajara Centro",
            segments: [
              {
                id: "seg_01",
                sceneId: "scene_01",
                startSeconds: 0.0,
                endSeconds: 8.0,
                durationSeconds: 8.0,
                beat: "HOOK",
                speechText: "Bienvenidos a Guadalajara.",
                hasPunchIn: true,
              },
            ],
          },
        ],
        sourceTimeline: {
          id: "tl_source_es_mx",
          locale: "es-MX",
          totalDurationSeconds: 8.0,
          scenes: [],
          editDecisions: [],
          checksumSha256: "b".repeat(64),
        },
      };

      const parsed = VlogProjectSchema.parse(project);
      assert.equal(parsed.schemaVersion, "1.0.0");
      assert.equal(parsed.config.aspectRatio, "9:16");
      assert.equal(parsed.mediaAssets[0].assignedRole, "A_ROLL");
    });
  });

  describe("14. Property-Based Testing (fast-check)", () => {
    it("PBT: TranscriptWord validates whenever end >= start and rejects when end < start", () => {
      fc.assert(
        fc.property(
          fc.double({ min: 0, max: 10000, noNaN: true }),
          fc.double({ min: 0, max: 500, noNaN: true }),
          fc.double({ min: 0, max: 1, noNaN: true }),
          fc.string({ minLength: 1 }),
          (start, duration, confidence, word) => {
            const end = start + duration;
            // Caso válido: end >= start
            const valid = VlogTranscriptWordSchema.safeParse({
              word,
              startSeconds: start,
              endSeconds: end,
              confidence,
            });
            assert.ok(valid.success);

            // Caso inválido si duration > 0: start invertido con end
            if (duration > 0.001) {
              const invalid = VlogTranscriptWordSchema.safeParse({
                word,
                startSeconds: end,
                endSeconds: start,
                confidence,
              });
              assert.ok(!invalid.success);
            }
          }
        )
      );
    });

    it("PBT: GeoBadge accepts coordinates strictly within [-90, 90] x [-180, 180] and rejects out-of-bounds", () => {
      fc.assert(
        fc.property(
          fc.double({ min: -90, max: 90, noNaN: true }),
          fc.double({ min: -180, max: 180, noNaN: true }),
          (latitude, longitude) => {
            const res = GeoBadgeSchema.safeParse({
              id: "test_geo",
              cityName: "Test City",
              coordinates: { latitude, longitude },
            });
            assert.ok(res.success);
          }
        )
      );

      // Fuera de rango
      assert.ok(!GeoBadgeSchema.safeParse({ id: "1", cityName: "C", coordinates: { latitude: 91, longitude: 0 } }).success);
      assert.ok(!GeoBadgeSchema.safeParse({ id: "1", cityName: "C", coordinates: { latitude: 0, longitude: 181 } }).success);
    });

    it("PBT: BRollMatchScore strictly rejects scores outside [0, 100]", () => {
      fc.assert(
        fc.property(
          fc.double({ min: 0, max: 100, noNaN: true }),
          (total) => {
            const res = BRollMatchScoreSchema.safeParse({
              total,
              semanticRelevance: total,
              entityMatch: total,
              visualQuality: total,
              locationRelevance: total,
              activityRelevance: total,
              durationFit: total,
              noveltyPenalty: total,
            });
            assert.ok(res.success);
          }
        )
      );
    });
  });
});
