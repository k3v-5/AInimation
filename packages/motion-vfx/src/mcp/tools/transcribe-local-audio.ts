import { LocalWhisperTranscriptionBridge, WhisperCLIOptions } from "../../automation/transcription/LocalWhisperTranscriptionBridge.js";
import { McpValidationError } from "../errors/mcp-errors.js";

export interface TranscribeLocalAudioArgs {
  audioPath?: string;
  videoPath?: string;
  textFallback?: string;
  totalDurationSec?: number;
  whisperOptions?: WhisperCLIOptions;
}

/**
 * Handler de la herramienta MCP `transcribe_local_audio`.
 * Permite a cualquier agente transcribir audio fonéticamente con Whisper local o sintetizar transcript.
 */
export async function handleTranscribeLocalAudio(rawArgs: unknown) {
  const args = rawArgs as TranscribeLocalAudioArgs;
  if (!args || typeof args !== "object") {
    throw new McpValidationError("Arguments must be a valid object.");
  }

  if (args.textFallback && args.totalDurationSec) {
    const syntheticDoc = LocalWhisperTranscriptionBridge.synthesizeDeterministicTranscript(
      args.textFallback,
      args.totalDurationSec
    );
    return {
      status: "success",
      mode: "synthetic_deterministic",
      document: syntheticDoc,
      wordCount: syntheticDoc.segments[0]?.words.length ?? 0,
    };
  }

  if (args.videoPath && !args.audioPath) {
    const wavOut = args.videoPath.replace(/\.[^/.]+$/, ".wav");
    const extractCmd = LocalWhisperTranscriptionBridge.buildAudioExtractionCommand(args.videoPath, wavOut);
    const cliCmd = LocalWhisperTranscriptionBridge.buildWhisperCLICommand(wavOut, args.whisperOptions);
    return {
      status: "ready_for_execution",
      extractAudioCommand: extractCmd,
      whisperExecutionCommand: cliCmd,
      outputWavPath: wavOut,
      note: "Execute commands locally or provide transcript JSON to parse.",
    };
  }

  if (args.audioPath) {
    const cliCmd = LocalWhisperTranscriptionBridge.buildWhisperCLICommand(args.audioPath, args.whisperOptions);
    return {
      status: "ready_for_execution",
      whisperExecutionCommand: cliCmd,
      audioPath: args.audioPath,
    };
  }

  throw new McpValidationError("Either audioPath, videoPath, or (textFallback + totalDurationSec) must be provided.");
}
