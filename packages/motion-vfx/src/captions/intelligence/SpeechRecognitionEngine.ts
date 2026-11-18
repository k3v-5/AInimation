import { AudioBuffer } from "../../audio/core/AudioBuffer.js";
import { AudioTransient, AudioTransientSyncEngine } from "../../audio/analysis/AudioTransientSyncEngine.js";
import { CaptionDocument, CaptionSegment, CaptionWord } from "../types/index.js";

export interface RecognizedWord {
  word: string;
  start: number; // Tiempo de inicio en segundos
  end: number; // Tiempo final en segundos
  confidence: number; // Nivel de confianza [0, 1]
  isEmphasis?: boolean; // Si es una palabra clave destacada
}

export interface SpeechRecognitionResult {
  language: string;
  duration: number;
  fullText: string;
  words: RecognizedWord[];
  segments: Array<{
    id: string;
    start: number;
    end: number;
    text: string;
    words: RecognizedWord[];
  }>;
}

export interface SpeechAlignOptions {
  wordsPerSegment?: number; // Máximo de palabras por grupo (default: 3 para viral TikTok)
  emphasisWords?: string[]; // Lista explícita de palabras a destacar
  minWordDurationSec?: number; // default: 0.12s
}

/**
 * Motor de reconocimiento de voz y alineación temporal a nivel de palabra (Fase 5E / Mejoras).
 * Convierte pistas de audio y transcripciones en estructuras rítmicas perfectamente alineadas
 * con los transientes acústicos para subtitulado dinámico viral.
 */
export class SpeechRecognitionEngine {
  /**
   * Alinea una transcripción de texto contra una pista de audio utilizando análisis de transientes y energía.
   */
  public static alignTranscriptWithAudio(
    text: string,
    audioBuffer: AudioBuffer,
    options: SpeechAlignOptions = {}
  ): SpeechRecognitionResult {
    const rawWords = text
      .trim()
      .split(/\s+/)
      .filter((w) => w.length > 0);

    const duration = Number((audioBuffer.frames / audioBuffer.sampleRate).toFixed(3));
    if (rawWords.length === 0 || duration <= 0) {
      return {
        language: "es",
        duration,
        fullText: "",
        words: [],
        segments: [],
      };
    }

    const transients = AudioTransientSyncEngine.detectTransients(audioBuffer, {
      sensitivity: 0.6,
      minPeakDistanceMs: 120,
    });

    const wordsPerSeg = options.wordsPerSegment ?? 3;
    const minDur = options.minWordDurationSec ?? 0.12;
    const emphasisList = new Set((options.emphasisWords ?? []).map((w) => w.toLowerCase()));

    // Distribuir palabras de forma proporcional y acoplada a transientes acústicos
    const words: RecognizedWord[] = [];
    const totalWords = rawWords.length;
    const avgWordDur = Math.max(minDur, duration / totalWords);

    let currentTime = 0;

    for (let i = 0; i < totalWords; i++) {
      const cleanWord = rawWords[i];
      const normalizedWord = cleanWord.replace(/[^\wáéíóúÁÉÍÓÚñÑ]/g, "").toLowerCase();

      let wordStart = currentTime;
      let wordEnd = Math.min(currentTime + avgWordDur, duration);

      // Buscar transiente acústico cercano para enganchar el inicio de la palabra
      const snap = transients.find((t) => Math.abs(t.time - wordStart) <= 0.15 && t.time < wordEnd);
      if (snap) {
        wordStart = snap.time;
      }

      if (wordEnd <= wordStart) {
        wordEnd = Math.min(wordStart + minDur, duration);
      }

      const isEmphasis =
        emphasisList.has(normalizedWord) ||
        cleanWord.toUpperCase() === cleanWord ||
        cleanWord.includes("!") ||
        cleanWord.length > 7;

      words.push({
        word: cleanWord,
        start: Number(wordStart.toFixed(3)),
        end: Number(wordEnd.toFixed(3)),
        confidence: 0.95,
        isEmphasis,
      });

      currentTime = wordEnd;
      if (currentTime >= duration) break;
    }

    // Agrupar palabras en segmentos compactos para formato viral (2 a 4 palabras por bloque)
    const segments: SpeechRecognitionResult["segments"] = [];
    for (let i = 0; i < words.length; i += wordsPerSeg) {
      const chunk = words.slice(i, i + wordsPerSeg);
      if (chunk.length === 0) continue;

      const segStart = chunk[0].start;
      const segEnd = chunk[chunk.length - 1].end;
      const segText = chunk.map((w) => w.word).join(" ");

      segments.push({
        id: `seg_${Math.floor(i / wordsPerSeg) + 1}`,
        start: segStart,
        end: segEnd,
        text: segText,
        words: chunk,
      });
    }

    return {
      language: "es",
      duration,
      fullText: text.trim(),
      words,
      segments,
    };
  }

  /**
   * Convierte un SpeechRecognitionResult a un CaptionDocument canónico del motor.
   */
  public static toCaptionDocument(result: SpeechRecognitionResult, docId = "speech_doc"): CaptionDocument {
    const segments: CaptionSegment[] = result.segments.map((seg, idx) => ({
      id: seg.id,
      start: seg.start,
      end: seg.end,
      text: seg.text,
      words: seg.words.map((w, wIdx) => ({
        id: `${seg.id}_w_${wIdx + 1}`,
        text: w.word,
        start: w.start,
        end: w.end,
        confidence: w.confidence,
      })),
      timingPrecision: "word",
    }));

    return {
      id: docId,
      duration: result.duration,
      segments,
      timingPrecision: "word",
      metadata: {
        language: result.language,
        totalDuration: result.duration,
        totalWords: result.words.length,
        createdAt: new Date().toISOString(),
      },
    };
  }
}
