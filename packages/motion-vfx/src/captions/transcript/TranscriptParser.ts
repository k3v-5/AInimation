import { Transcript, TranscriptSegment, TranscriptWord } from "../types/index.js";
import { SRTParser } from "./SRTParser.js";
import { WhisperJSONParser } from "./WhisperJSONParser.js";

/**
 * Parser de transcripciones unificado para Fase 5E y 16 (JSON nativo, Whisper, SRT y VTT).
 */
export class TranscriptParser {
  public static fromJSON(data: any): Transcript {
    return {
      id: data.id ?? "transcript_1",
      language: data.language ?? "en",
      segments: (data.segments ?? []).map((s: any, idx: number) => ({
        id: s.id ?? `seg_${idx}`,
        start: Number(s.start),
        end: Number(s.end),
        text: String(s.text).trim(),
        words: (s.words ?? []).map((w: any, wIdx: number) => ({
          id: w.id ?? `word_${idx}_${wIdx}`,
          text: String(w.text).trim(),
          start: Number(w.start),
          end: Number(w.end),
          confidence: w.confidence !== undefined ? Number(w.confidence) : undefined,
          prosody: w.prosody,
        })),
      })),
    };
  }

  public static fromWhisperJSON(whisperData: any): Transcript {
    const doc = WhisperJSONParser.parse(whisperData);
    return {
      id: doc.id,
      language: doc.metadata?.language ?? "en",
      segments: doc.segments.map((s) => ({
        id: s.id,
        start: s.start,
        end: s.end,
        text: s.text,
        words: s.words.map((w) => ({
          id: w.id,
          text: w.text,
          start: w.start,
          end: w.end,
          confidence: w.confidence,
          prosody: w.prosody,
        })),
      })),
    };
  }

  public static fromSRT(srtContent: string): Transcript {
    const doc = SRTParser.parse(srtContent);
    return {
      id: doc.id,
      segments: doc.segments.map((s) => ({
        id: s.id,
        start: s.start,
        end: s.end,
        text: s.text,
        words: s.words.map((w) => ({
          id: w.id,
          text: w.text,
          start: w.start,
          end: w.end,
          confidence: w.confidence,
        })),
      })),
    };
  }

  public static fromVTT(vttContent: string): Transcript {
    const cleanContent = vttContent.replace(/^WEBVTT[^\n]*\n/, "").trim();
    return this.fromSRT(cleanContent);
  }
}
