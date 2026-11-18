import { SupportedLocale } from "../contracts/language.types.js";
import { TextNormalizer } from "./text-normalizer.js";

/** Unidad de texto segmentada para síntesis individual */
export interface SynthesizableTextSegment {
  segmentIndex: number;
  sourceText: string;
  normalizedText: string;
  locale: SupportedLocale;
  wordCount: number;
  words: string[];
}

/**
 * Segmentador Lingüístico para Síntesis de Voz (Milestone 4-08).
 * Divide un guion o texto largo en unidades oracionales o sintácticas
 * garantizando que ningún segmento quede vacío y preservando mapeos de palabras.
 */
export class TextSegmenter {
  /**
   * Divide un texto en segmentos sintetizables respetando puntuación y longitud máxima.
   */
  public static segment(
    text: string,
    locale: SupportedLocale,
    maxSegmentChars = 140
  ): SynthesizableTextSegment[] {
    if (!text || typeof text !== "string" || text.trim().length === 0) {
      return [];
    }

    // 1. Dividir primero por oraciones (puntos, signos de interrogación, exclamación, saltos de línea)
    const rawSentences = text
      .split(/(?<=[.!?;\n])\s+/)
      .map((s) => s.trim())
      .filter((s) => s.length > 0);

    const resultSegments: SynthesizableTextSegment[] = [];
    let segmentIndex = 0;

    for (const sentence of rawSentences) {
      if (sentence.length <= maxSegmentChars) {
        const norm = TextNormalizer.normalize(sentence, locale);
        const words = norm.normalizedText.split(/\s+/).filter((w) => w.length > 0);
        if (words.length > 0) {
          resultSegments.push({
            segmentIndex: segmentIndex++,
            sourceText: sentence,
            normalizedText: norm.normalizedText,
            locale,
            wordCount: words.length,
            words,
          });
        }
      } else {
        // Dividir por cláusulas (comas, dos puntos, guiones) si la oración es muy larga
        const clauses = sentence
          .split(/(?<=[,:\-])\s+/)
          .map((c) => c.trim())
          .filter((c) => c.length > 0);

        for (const clause of clauses) {
          const norm = TextNormalizer.normalize(clause, locale);
          const words = norm.normalizedText.split(/\s+/).filter((w) => w.length > 0);
          if (words.length > 0) {
            resultSegments.push({
              segmentIndex: segmentIndex++,
              sourceText: clause,
              normalizedText: norm.normalizedText,
              locale,
              wordCount: words.length,
              words,
            });
          }
        }
      }
    }

    return resultSegments;
  }
}
