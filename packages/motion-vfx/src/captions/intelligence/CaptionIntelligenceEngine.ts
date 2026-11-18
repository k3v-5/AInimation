import { CaptionDocument, CaptionSegment, CaptionWord } from "../types/index.js";
import { EmphasisScorer, EmphasisScorerOptions } from "./EmphasisScorer.js";

export interface CaptionIntelligenceOptions extends EmphasisScorerOptions {
  maxEmphasizedWordsPerSegment?: number;
  minEmphasisInterval?: number; // segundos mínimos entre dos palabras enfatizadas consecutivas
}

/**
 * Orquestador determinista de inteligencia para análisis, énfasis y enriquecimiento de captions (Fase 16).
 */
export class CaptionIntelligenceEngine {
  private scorer: EmphasisScorer;
  private maxPerSegment: number;
  private minInterval: number;

  constructor(options: CaptionIntelligenceOptions = {}) {
    this.scorer = new EmphasisScorer(options);
    this.maxPerSegment = options.maxEmphasizedWordsPerSegment ?? 3;
    this.minInterval = options.minEmphasisInterval ?? 0.3;
  }

  /**
   * Analiza un CaptionDocument y enriquece cada palabra con decisiones de énfasis y animación.
   */
  public analyzeDocument(doc: CaptionDocument): CaptionDocument {
    const enrichedSegments: CaptionSegment[] = [];

    for (const segment of doc.segments) {
      const wordsCount = segment.words.length;
      let emphasizedCount = 0;
      let lastEmphasizedEnd = -Infinity;

      const scoredWords: CaptionWord[] = segment.words.map((word, wIdx) => {
        const emphasis = this.scorer.evaluateWord(word, wIdx, wordsCount, segment.text);
        return {
          ...word,
          emphasis,
        };
      });

      // Filtrar y regular el presupuesto de énfasis por segmento
      const finalWords: CaptionWord[] = scoredWords.map((word) => {
        let isEmphasized = word.emphasis?.isEmphasized ?? false;

        if (isEmphasized) {
          // Verificar si excede el máximo permitido o si está demasiado pegada a la anterior
          if (
            emphasizedCount >= this.maxPerSegment ||
            word.start - lastEmphasizedEnd < this.minInterval
          ) {
            isEmphasized = false;
          } else {
            emphasizedCount++;
            lastEmphasizedEnd = word.end;
          }
        }

        const emphasisDecision = word.emphasis
          ? {
              ...word.emphasis,
              isEmphasized,
            }
          : undefined;

        // Configuración de animación para palabras enfatizadas
        const animation =
          isEmphasized && emphasisDecision?.recommendedAnimation && emphasisDecision.recommendedAnimation !== "none"
            ? {
                type: emphasisDecision.recommendedAnimation,
                duration: Number((word.end - word.start).toFixed(4)),
                intensity: emphasisDecision.score >= 0.8 ? 1.0 : 0.75,
              }
            : undefined;

        return {
          ...word,
          emphasis: emphasisDecision,
          animation,
        };
      });

      enrichedSegments.push({
        ...segment,
        words: finalWords,
      });
    }

    return {
      ...doc,
      segments: enrichedSegments,
    };
  }
}
