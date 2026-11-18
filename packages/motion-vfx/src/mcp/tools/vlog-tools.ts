import path from "node:path";
import { LocalWhisperTranscriptionBridge } from "../../automation/transcription/LocalWhisperTranscriptionBridge.js";
import { IngestedMediaFile } from "../../vlog/contracts/ingestion.types.js";
import { SupportedLocale } from "../../vlog/contracts/language.types.js";
import { VlogAspectRatio } from "../../vlog/contracts/vlog.constants.js";
import { VlogFootageClassifier } from "../../vlog/classifier/vlog-footage-classifier.js";
import { VlogBRollMatcher } from "../../vlog/classifier/vlog-broll-matcher.js";
import { VlogJumpCutEngine } from "../../vlog/jumpcut/vlog-jumpcut-engine.js";
import {
  VlogAssetInput,
  VlogMultilingualProductionOrchestrator,
  VlogProductionConfig,
} from "../../vlog/orchestrator/vlog-orchestrator.js";
import { McpValidationError } from "../errors/mcp-errors.js";

export interface VlogJumpCutArgs {
  videoPath: string;
  transcriptText?: string;
  totalDurationSec?: number;
  silenceThresholdSec?: number;
  punchInScale?: number;
}

export interface VlogClassifyArgs {
  filePath: string;
  durationSeconds: number;
  hasSpeech?: boolean;
  hasFace?: boolean;
  hasCameraMotion?: boolean;
}

export interface VlogMatchBRollArgs {
  intentText: string;
  targetDurationSeconds: number;
  availableMedia: {
    id: string;
    filePath: string;
    durationSeconds: number;
    hasAudio?: boolean;
  }[];
}

export interface VlogProduceArgs {
  projectId: string;
  sourceLocale?: SupportedLocale;
  targetLocales?: SupportedLocale[];
  scriptText: string;
  assets: VlogAssetInput[];
  aspectRatios?: VlogAspectRatio[];
  outputDirectory?: string;
}

export interface VlogGetStatusArgs {
  runId?: string;
  projectId?: string;
}

/**
 * In-memory status store for runs executed via MCP
 */
const runStatusRegistry = new Map<string, any>();

/**
 * Handler for `vlog_generate_jump_cut_plan`.
 * Computes deterministic silence removal, word boundary protection, and punch-in events.
 */
export async function handleVlogGenerateJumpCutPlan(rawArgs: unknown) {
  const args = rawArgs as VlogJumpCutArgs;
  if (!args || typeof args !== "object" || !args.videoPath) {
    throw new McpValidationError("Argument 'videoPath' is required.");
  }

  const duration = args.totalDurationSec ?? 60.0;
  const scriptText = args.transcriptText ?? "Sample speech segment for autonomous vlog montage.";

  const captionDoc = LocalWhisperTranscriptionBridge.synthesizeDeterministicTranscript(scriptText, duration);

  const vlogTranscript = {
    id: "transcript_01",
    language: "es",
    locale: "es-MX",
    durationSeconds: duration,
    confidence: 0.95,
    rawText: scriptText,
    segments: captionDoc.segments.map((seg, sIdx) => ({
      id: `seg_${sIdx + 1}`,
      startSeconds: seg.start,
      endSeconds: seg.end,
      text: seg.text,
      confidence: 0.95,
      words: seg.words.map((w) => ({
        word: w.text,
        startSeconds: w.start,
        endSeconds: w.end,
        confidence: w.confidence ?? 0.95,
      })),
    })),
  };

  const plan = VlogJumpCutEngine.createJumpCutPlan(
    "mcp_vlog_project",
    path.basename(args.videoPath),
    duration,
    vlogTranscript,
    undefined,
    undefined,
    undefined,
    {
      silenceThresholdSeconds: args.silenceThresholdSec ?? 0.25,
    }
  );

  return {
    status: "success",
    projectId: plan.projectId,
    sourceDuration: plan.statistics.originalDurationSeconds,
    editedDuration: plan.statistics.editedDurationSeconds,
    timeSavedSeconds: plan.statistics.totalTimeSavedSeconds,
    totalSilencesRemoved: plan.statistics.cutsCount,
    totalRetainedSegments: plan.retainedSegments.length,
    plan,
  };
}

/**
 * Handler for `vlog_classify_footage`.
 * Classifies media into A-Roll, B-Roll, Action, Timelapse, Photo, or Screen.
 */
export async function handleVlogClassifyFootage(rawArgs: unknown) {
  const args = rawArgs as VlogClassifyArgs;
  if (!args || typeof args !== "object" || !args.filePath) {
    throw new McpValidationError("Argument 'filePath' is required.");
  }

  const ext = path.extname(args.filePath);
  const filenameTags = path.basename(args.filePath, ext).toLowerCase().split(/[_\-\s]+/);
  const mockMedia: IngestedMediaFile = {
    id: `asset_${path.basename(args.filePath, ext)}`,
    absolutePath: args.filePath,
    filename: path.basename(args.filePath),
    extension: ext,
    mimeType: "video/mp4",
    fingerprint: {
      checksumSha256: "0".repeat(64),
      sizeBytes: 1024 * 1024 * 25,
      lastModifiedTimestamp: Date.now(),
      durationSeconds: args.durationSeconds ?? 10.0,
    },
    videoStream: {
      codec: "h264",
      width: 1920,
      height: 1080,
      aspectRatio: "16:9",
      fps: 30,
      frameRateMode: "CFR",
      durationSeconds: args.durationSeconds ?? 10.0,
      orientation: "LANDSCAPE",
    },
    audioStream: args.hasSpeech
      ? {
          codec: "aac",
          sampleRateHz: 44100,
          channels: 2,
          durationSeconds: args.durationSeconds ?? 10.0,
        }
      : undefined,
    isReadOnly: true,
    ingestedAtTimestamp: Date.now(),
  };

  const classification = VlogFootageClassifier.classify(mockMedia, {
    hasVoiceActivity: args.hasSpeech ?? false,
    hasDominantFace: args.hasFace ?? false,
    averageOpticalFlow: args.hasCameraMotion ? 0.35 : 0.15,
    detectedTags: filenameTags,
  });

  return {
    status: "success",
    mediaId: classification.mediaId,
    primaryType: classification.primaryType,
    confidence: classification.confidence,
    scores: classification.scores,
    evidence: classification.evidence,
  };
}

/**
 * Handler for `vlog_match_broll`.
 * Matches and ranks available B-roll footage against a spoken concept or narrative topic.
 */
export async function handleVlogMatchBRoll(rawArgs: unknown) {
  const args = rawArgs as VlogMatchBRollArgs;
  if (!args || typeof args !== "object" || !args.intentText) {
    throw new McpValidationError("Argument 'intentText' is required.");
  }

  const mediaList: IngestedMediaFile[] = (args.availableMedia ?? []).map((m, idx) => {
    const ext = path.extname(m.filePath) || ".mp4";
    return {
      id: m.id ?? `broll_${idx + 1}`,
      absolutePath: m.filePath,
      filename: path.basename(m.filePath),
      extension: ext,
      mimeType: "video/mp4",
      fingerprint: {
        checksumSha256: "0".repeat(64),
        sizeBytes: 1024 * 1024 * 10,
        lastModifiedTimestamp: Date.now(),
        durationSeconds: m.durationSeconds,
      },
      videoStream: {
        codec: "h264",
        width: 1920,
        height: 1080,
        aspectRatio: "16:9",
        fps: 30,
        frameRateMode: "CFR",
        durationSeconds: m.durationSeconds,
        orientation: "LANDSCAPE",
      },
      audioStream: m.hasAudio
        ? {
            codec: "aac",
            sampleRateHz: 44100,
            channels: 2,
            durationSeconds: m.durationSeconds,
          }
        : undefined,
      isReadOnly: true,
      ingestedAtTimestamp: Date.now(),
    };
  });

  const classifications = new Map();
  for (const m of mediaList) {
    const ext = path.extname(m.filename);
    const filenameTags = path.basename(m.filename, ext).toLowerCase().split(/[_\-\s]+/);
    classifications.set(
      m.id,
      VlogFootageClassifier.classify(m, {
        hasVoiceActivity: false,
        detectedTags: filenameTags,
      })
    );
  }

  const match = VlogBRollMatcher.matchBRoll(
    {
      narrativeSegmentId: "segment_1",
      intentText: args.intentText,
      targetDurationSeconds: args.targetDurationSeconds ?? 4.0,
      timelineStartSeconds: 0.0,
      timelineEndSeconds: args.targetDurationSeconds ?? 4.0,
    },
    mediaList,
    classifications
  );

  return {
    status: "success",
    matchFound: match !== null,
    bestMatch: match
      ? {
          mediaId: match.selectedCandidate.mediaId,
          score: match.selectedCandidate.score.total,
          selectedRange: match.selectedCandidate.subclipRange,
        }
      : null,
    totalCandidatesEvaluated: mediaList.length,
  };
}

/**
 * Handler for `vlog_produce`.
 * Orchestrates full multi-lingual autonomous vlog production pipeline.
 */
export async function handleVlogProduce(rawArgs: unknown) {
  const args = rawArgs as VlogProduceArgs;
  if (!args || typeof args !== "object" || !args.projectId || !args.scriptText) {
    throw new McpValidationError("Arguments 'projectId' and 'scriptText' are required.");
  }

  const config: VlogProductionConfig = {
    projectId: args.projectId,
    sourceLocale: args.sourceLocale ?? "es-MX",
    targetLocales: args.targetLocales ?? ["es-MX", "en-US"],
    scriptText: args.scriptText,
    assets: args.assets ?? [
      {
        id: "aroll_01",
        name: "TalkingHead.mp4",
        type: "A_ROLL",
        durationSeconds: 30.0,
        filePath: "/mock/aroll.mp4",
      },
    ],
    aspectRatios: args.aspectRatios ?? ["16:9", "9:16"],
    outputDirectory: args.outputDirectory ?? `./output/${args.projectId}`,
  };

  const result = await VlogMultilingualProductionOrchestrator.execute(config);

  // Store run in registry for status queries
  runStatusRegistry.set(result.run.runId, result);
  runStatusRegistry.set(args.projectId, result);

  return {
    status: "success",
    runId: result.run.runId,
    projectId: result.run.projectId,
    engineVersion: result.run.engineVersion,
    isSuccess: result.isSuccess,
    totalDurationSeconds: result.manifest.validation.metrics.totalDurationSeconds,
    deliveredLanguages: result.manifest.targetLocales,
    totalArtifactsEmitted: result.manifest.artifacts.length,
    manifestPath: `output/${result.run.projectId}/manifest.json`,
  };
}

/**
 * Handler for `vlog_get_status`.
 * Retrieves execution metrics, artifacts, and health of an autonomous vlog run.
 */
export async function handleVlogGetStatus(rawArgs: unknown) {
  const args = rawArgs as VlogGetStatusArgs;
  const key = args.runId ?? args.projectId;
  if (!key) {
    throw new McpValidationError("Either 'runId' or 'projectId' must be provided.");
  }

  const result = runStatusRegistry.get(key);
  if (!result) {
    return {
      status: "not_found",
      message: `No active or completed vlog production found for '${key}'.`,
    };
  }

  return {
    status: "success",
    runId: result.run.runId,
    projectId: result.run.projectId,
    phases: result.run.phases.map((p: any) => ({ phase: p.phase, state: p.state })),
    languages: result.manifest.targetLocales,
    artifacts: result.manifest.artifacts.map((a: any) => ({
      id: a.artifactId,
      type: a.type,
      checksum: a.checksumSha256,
    })),
  };
}
