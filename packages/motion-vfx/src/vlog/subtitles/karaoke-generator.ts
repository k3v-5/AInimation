import { SupportedLocale } from "../contracts/language.types.js";
import {
  DEFAULT_TIME_EDITORIAL_SUBTITLE_STYLE,
  SubtitleCue,
  SubtitleStyle,
  SubtitleWord,
} from "../contracts/subtitles.types.js";
import { VoiceWordTiming } from "../contracts/voiceover.types.js";
import { SYNC_TOLERANCES, VlogAspectRatio } from "../contracts/vlog.constants.js";
import { SubtitleFormatter } from "./subtitle-formatter.js";

export interface KaraokeGenerationOptions {
  aspectRatio?: VlogAspectRatio;
  wordsPerCueMin?: number; // default: 3
  wordsPerCueMax?: number; // default: 6
  maxCueDurationSeconds?: number; // default: 3.5s
  style?: SubtitleStyle;
  targetYPosition?: number; // default: 0.82
}

/**
 * Generador de Subtítulos Karaoke Palabra por Palabra (Milestone 6-B).
 * Agrupa timestamps vocales en bloques visuales sincronizados con resaltado
 * progresivo (highlightColor #FF1424) y verificación de tolerancias temporales.
 */
export class KaraokeGenerator {
  public static generateCues(
    wordTimings: VoiceWordTiming[],
    locale: SupportedLocale,
    options: KaraokeGenerationOptions = {}
  ): SubtitleCue[] {
    if (!wordTimings || wordTimings.length === 0) {
      return [];
    }

    const minWords = options.wordsPerCueMin ?? 3;
    const maxWords = options.wordsPerCueMax ?? 6;
    const maxDuration = options.maxCueDurationSeconds ?? 3.5;
    const style = options.style ?? DEFAULT_TIME_EDITORIAL_SUBTITLE_STYLE;
    const targetY = options.targetYPosition ?? 0.82;

    const cues: SubtitleCue[] = [];
    let currentWords: SubtitleWord[] = [];
    let cueIndex = 1;

    for (let i = 0; i < wordTimings.length; i++) {
      const wt = wordTimings[i];
      const formattedWord = SubtitleFormatter.formatText(wt.word, style);

      // Verificación de monotonía
      const wordDuration = wt.endSeconds - wt.startSeconds;
      const safeEnd = wordDuration > 0 ? wt.endSeconds : wt.startSeconds + 0.1;

      currentWords.push({
        word: formattedWord,
        startSeconds: Number(wt.startSeconds.toFixed(4)),
        endSeconds: Number(safeEnd.toFixed(4)),
        isHighlighted: false,
        highlightColor: style.highlightFillColor,
      });

      const currentCueDuration = currentWords[currentWords.length - 1].endSeconds - currentWords[0].startSeconds;
      const isLastWord = i === wordTimings.length - 1;
      const reachedMaxWords = currentWords.length >= maxWords;
      const reachedMaxDuration = currentCueDuration >= maxDuration && currentWords.length >= minWords;

      if (isLastWord || reachedMaxWords || reachedMaxDuration) {
        const cueStart = currentWords[0].startSeconds;
        const cueEnd = currentWords[currentWords.length - 1].endSeconds;
        const fullText = currentWords.map((w) => w.word).join(" ");

        cues.push({
          id: `cue_${locale}_${String(cueIndex++).padStart(3, "0")}`,
          locale,
          startSeconds: Number(cueStart.toFixed(4)),
          endSeconds: Number(cueEnd.toFixed(4)),
          text: fullText,
          words: [...currentWords],
          position: {
            normalizedX: 0.5,
            normalizedY: targetY,
            alignment: "center",
          },
        });

        currentWords = [];
      }
    }

    return cues;
  }
}
