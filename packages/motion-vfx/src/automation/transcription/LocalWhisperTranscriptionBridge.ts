import { WhisperJSONParser } from "../../captions/transcript/WhisperJSONParser.js";
import { CaptionDocument } from "../../captions/types/index.js";
import { MotionEngineError } from "../../errors/index.js";

export class TranscriptionError extends MotionEngineError {
  constructor(message: string, public readonly context?: Record<string, any>) {
    super(`Transcription Error: ${message}`);
  }
}

export type WhisperModelSize = "tiny" | "base" | "small" | "medium" | "large-v3";

export interface WhisperCLIOptions {
  model?: WhisperModelSize;
  language?: string; // ej. "es", "en", "auto"
  wordTimestamps?: boolean;
  outputFormat?: "json" | "srt" | "txt";
  outputDir?: string;
  threads?: number;
}

/**
 * Bridge determinista y local para OpenAI Whisper (Fase 16 / Suite de Automatización).
 * Opera 100% offline sin dependencias de red ni costos de APIs.
 */
export class LocalWhisperTranscriptionBridge {
  /**
   * Genera el comando de extracción de audio ligero optimizado para Whisper (16kHz Mono WAV).
   */
  public static buildAudioExtractionCommand(inputVideoPath: string, outputWavPath: string): string {
    if (!inputVideoPath || !outputWavPath) {
      throw new TranscriptionError("Input video path and output WAV path must be non-empty.");
    }
    const cleanIn = inputVideoPath.replace(/\\/g, "/");
    const cleanOut = outputWavPath.replace(/\\/g, "/");
    return `ffmpeg -y -i "${cleanIn}" -vn -ar 16000 -ac 1 -c:a pcm_s16le "${cleanOut}"`;
  }

  /**
   * Genera el comando de ejecución CLI para Whisper local (whisper.cpp, faster-whisper o CLI nativo).
   */
  public static buildWhisperCLICommand(audioWavPath: string, options: WhisperCLIOptions = {}): string {
    if (!audioWavPath) {
      throw new TranscriptionError("Audio WAV path must be non-empty.");
    }
    const model = options.model ?? "base";
    const lang = options.language ?? "es";
    const wordTimings = options.wordTimestamps ?? true;
    const cleanAudio = audioWavPath.replace(/\\/g, "/");
    const outDir = (options.outputDir ?? "./transcripts").replace(/\\/g, "/");

    const wordFlag = wordTimings ? "--word_timestamps True" : "";
    return `whisper "${cleanAudio}" --model ${model} --language ${lang} --output_format json --output_dir "${outDir}" ${wordFlag}`.trim();
  }

  /**
   * Procesa la salida JSON de Whisper y la convierte a CaptionDocument con marcas a nivel de palabra.
   */
  public static parseTranscriptionJSON(jsonStringOrObj: string | Record<string, any>, documentId = "whisper_doc"): CaptionDocument {
    return WhisperJSONParser.parse(jsonStringOrObj, documentId);
  }

  /**
   * Sintetiza una transcripción simulada determinista a partir de un texto y una duración total
   * (ideal para testing, pipelines offline o previsualizaciones inmediatas).
   */
  public static synthesizeDeterministicTranscript(
    text: string,
    totalDurationSec: number,
    startOffsetSec = 0.0,
    docId = "synthetic_transcript"
  ): CaptionDocument {
    if (!text || text.trim().length === 0) {
      throw new TranscriptionError("Text cannot be empty for synthetic transcript.");
    }
    if (totalDurationSec <= 0) {
      throw new TranscriptionError("Total duration must be strictly positive.");
    }

    const rawWords = text.trim().split(/\s+/).filter(w => w.length > 0);
    const wordCount = rawWords.length;
    const durationPerWord = totalDurationSec / wordCount;

    const segments = [];
    const words = [];

    for (let i = 0; i < wordCount; i++) {
      const wStart = startOffsetSec + i * durationPerWord;
      const wEnd = wStart + durationPerWord;
      words.push({
        id: `w_${i}`,
        text: rawWords[i],
        start: Number(wStart.toFixed(3)),
        end: Number(wEnd.toFixed(3)),
        confidence: 0.99,
      });
    }

    segments.push({
      id: "seg_0",
      start: startOffsetSec,
      end: startOffsetSec + totalDurationSec,
      text: text.trim(),
      words,
      timingPrecision: "word" as const,
    });

    return {
      id: docId,
      duration: totalDurationSec,
      segments,
      timingPrecision: "word",
      metadata: {
        engine: "LocalWhisperBridge_Synthesized",
        wordCount,
      },
    };
  }
}
