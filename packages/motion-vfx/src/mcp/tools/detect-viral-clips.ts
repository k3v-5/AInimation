import { AudioEnergySample, ViralMomentDetector } from "../../automation/clipping/ViralMomentDetector.js";
import { LocalWhisperTranscriptionBridge } from "../../automation/transcription/LocalWhisperTranscriptionBridge.js";
import { CaptionDocument } from "../../captions/types/index.js";
import { McpValidationError } from "../errors/mcp-errors.js";

export interface DetectViralClipsArgs {
  transcript?: CaptionDocument;
  transcriptText?: string;
  totalDurationSec?: number;
  energySamples?: AudioEnergySample[];
  targetDurationRangeSec?: [number, number];
  topK?: number;
}

/**
 * Handler de la herramienta MCP `detect_viral_clips`.
 * Extrae los mejores momentos virales con scoring de retención (0-100) para Shorts/TikTok.
 */
export async function handleDetectViralClips(rawArgs: unknown) {
  const args = rawArgs as DetectViralClipsArgs;
  if (!args || typeof args !== "object") {
    throw new McpValidationError("Arguments must be a valid object.");
  }

  let doc: CaptionDocument;
  if (args.transcript) {
    doc = args.transcript;
  } else if (args.transcriptText && args.totalDurationSec) {
    doc = LocalWhisperTranscriptionBridge.synthesizeDeterministicTranscript(
      args.transcriptText,
      args.totalDurationSec
    );
  } else {
    throw new McpValidationError("Either transcript (CaptionDocument) or (transcriptText + totalDurationSec) must be provided.");
  }

  const clips = ViralMomentDetector.detectViralMoments(
    doc,
    args.energySamples ?? [],
    args.targetDurationRangeSec ?? [30.0, 50.0],
    args.topK ?? 3
  );

  return {
    status: "success",
    totalCandidatesFound: clips.length,
    viralClips: clips,
  };
}
