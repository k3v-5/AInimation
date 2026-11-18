import { generateDeterministicLayerId } from "../../core/id.js";
import {
  Caption,
  CaptionLayoutMode,
  CaptionStyle,
  CaptionWord,
  SemanticPosition,
  Transcript,
  TranscriptWord,
} from "../types/index.js";

export interface SegmentationOptions {
  maxWords?: number; // Máximo de palabras por grupo (ej. 3 o 4)
  maxDuration?: number; // Duración máxima en segundos por bloque (ej. 2.0s)
  style?: CaptionStyle;
  layoutMode?: CaptionLayoutMode;
  position?: SemanticPosition;
}

const DEFAULT_STYLE: CaptionStyle = {
  fontFamily: "Arial",
  fontSize: 64,
  fontWeight: 800,
  color: { r: 1, g: 1, b: 1 },
  alignment: "center",
};

/**
 * Segmentador de transcripciones en bloques de subtítulos cinemáticos (Fase 5E).
 */
export class CaptionSegmenter {
  public static segment(
    transcriptOrWords: Transcript | TranscriptWord[],
    options: SegmentationOptions = {}
  ): Caption[] {
    const maxWords = options.maxWords ?? 4;
    const maxDuration = options.maxDuration ?? 2.0;
    const style = options.style ?? DEFAULT_STYLE;
    const layoutMode = options.layoutMode ?? "karaoke";
    const position = options.position ?? "bottom-center";

    // Extraer array plano de palabras
    let allWords: TranscriptWord[] = [];
    if (Array.isArray(transcriptOrWords)) {
      allWords = transcriptOrWords;
    } else {
      for (const segment of transcriptOrWords.segments) {
        if (segment.words && segment.words.length > 0) {
          allWords.push(...segment.words);
        }
      }
    }

    if (allWords.length === 0) return [];

    const captions: Caption[] = [];
    let currentGroup: CaptionWord[] = [];
    let groupStart = allWords[0].start;

    for (let i = 0; i < allWords.length; i++) {
      const w = allWords[i];
      const wordDuration = w.end - groupStart;

      const shouldBreak =
        currentGroup.length >= maxWords || (currentGroup.length > 0 && wordDuration > maxDuration);

      if (shouldBreak) {
        // Cerrar grupo actual
        const start = currentGroup[0].start;
        const end = currentGroup[currentGroup.length - 1].end;

        captions.push({
          id: `caption_${generateDeterministicLayerId()}`,
          timelineRange: { start, end },
          words: [...currentGroup],
          style: { ...style },
          layoutMode,
          position,
        });

        currentGroup = [];
        groupStart = w.start;
      }

      currentGroup.push({
        id: w.id,
        text: w.text,
        start: w.start,
        end: w.end,
      });
    }

    if (currentGroup.length > 0) {
      const start = currentGroup[0].start;
      const end = currentGroup[currentGroup.length - 1].end;

      captions.push({
        id: `caption_${generateDeterministicLayerId()}`,
        timelineRange: { start, end },
        words: [...currentGroup],
        style: { ...style },
        layoutMode,
        position,
      });
    }

    return captions;
  }
}
