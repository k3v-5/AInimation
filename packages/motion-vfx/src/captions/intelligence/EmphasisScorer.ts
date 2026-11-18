import { CaptionWord, EmphasisDecision, ProsodySignals, WordAnimationType } from "../types/index.js";

export interface EmphasisScorerOptions {
  lexicalWeight?: number;
  positionalWeight?: number;
  prosodyWeight?: number;
  emphasisThreshold?: number;
  stopwords?: Set<string>;
  customKeywords?: Map<string, { scoreBonus: number; recommendedAnimation?: WordAnimationType; emojiTag?: string }>;
}

const DEFAULT_STOPWORDS = new Set([
  // Spanish stopwords
  "de", "la", "el", "los", "las", "un", "una", "unos", "unas", "y", "o", "u", "en", "a", "por", "para", "con", "sin", "sobre", "del", "al", "que", "es", "son", "se", "su", "sus", "mi", "mis", "tu", "tus", "pero", "si", "no", "como", "mas", "más", "lo", "le", "les",
  // English stopwords
  "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "from", "up", "down", "of", "off", "over", "under", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "it", "its", "they", "them", "their", "we", "us", "our", "you", "your", "he", "him", "his", "she", "her", "that", "this", "these", "those"
]);

/**
 * Motor determinista de cálculo de énfasis léxico y prosódico (Fase 16).
 */
export class EmphasisScorer {
  private lexicalWeight: number;
  private positionalWeight: number;
  private prosodyWeight: number;
  private emphasisThreshold: number;
  private stopwords: Set<string>;
  private customKeywords: Map<string, { scoreBonus: number; recommendedAnimation?: WordAnimationType; emojiTag?: string }>;

  constructor(options: EmphasisScorerOptions = {}) {
    this.lexicalWeight = options.lexicalWeight ?? 0.45;
    this.positionalWeight = options.positionalWeight ?? 0.25;
    this.prosodyWeight = options.prosodyWeight ?? 0.30;
    this.emphasisThreshold = options.emphasisThreshold ?? 0.55;
    this.stopwords = options.stopwords ?? DEFAULT_STOPWORDS;
    this.customKeywords = options.customKeywords ?? new Map();
  }

  /**
   * Evalúa y puntúa el énfasis de una palabra dentro de su segmento.
   */
  public evaluateWord(
    word: CaptionWord,
    wordIndex: number,
    totalWordsInSegment: number,
    segmentText: string
  ): EmphasisDecision {
    const reasons: string[] = [];
    const cleanWord = word.text.replace(/[^\p{L}\p{N}]/gu, "").toLowerCase();
    const rawWord = word.text.trim();

    // 1. Puntaje Léxico (S_lex)
    let sLex = 0.0;

    // Chequeo de Stopwords
    if (this.stopwords.has(cleanWord)) {
      sLex = 0.0;
    } else {
      sLex += 0.35; // Base para palabras de contenido

      // Longitud de palabra
      if (cleanWord.length >= 7) {
        sLex += 0.25;
        reasons.push("long-content-word");
      }

      // Mayúsculas sostenidas / ALL CAPS
      if (rawWord.length > 1 && rawWord === rawWord.toUpperCase() && /[A-ZÁÉÍÓÚÑ]/.test(rawWord)) {
        sLex += 0.35;
        reasons.push("all-caps-emphasis");
      }

      // Signos de puntuación enfáticos
      if (/[!?]/.test(rawWord)) {
        sLex += 0.30;
        reasons.push("emphatic-punctuation");
      }
    }

    // Regla de keywords personalizadas
    let customBonus = 0.0;
    let customAnimation: WordAnimationType | undefined;
    let customEmojiTag: string | undefined;

    if (this.customKeywords.has(cleanWord)) {
      const match = this.customKeywords.get(cleanWord)!;
      customBonus = match.scoreBonus;
      customAnimation = match.recommendedAnimation;
      customEmojiTag = match.emojiTag;
      reasons.push(`custom-keyword:${cleanWord}`);
    }

    sLex = Math.min(1.0, sLex + customBonus);

    // 2. Puntaje Posicional (S_pos)
    let sPos = 0.0;
    if (totalWordsInSegment > 1) {
      if (wordIndex === 0) {
        sPos = 0.40;
        reasons.push("hook-position");
      } else if (wordIndex === totalWordsInSegment - 1) {
        sPos = 0.50;
        reasons.push("punchline-position");
      } else {
        sPos = 0.20;
      }
    } else {
      sPos = 0.60;
      reasons.push("single-word-segment");
    }

    // 3. Puntaje Prosódico (S_pros)
    let sPros = 0.0;
    const prosody = word.prosody;

    if (prosody) {
      let prosodyFactors = 0;
      let prosodySum = 0;

      if (prosody.energy !== undefined && isFinite(prosody.energy)) {
        prosodySum += Math.max(0, Math.min(1, prosody.energy));
        prosodyFactors++;
        if (prosody.energy > 0.7) reasons.push("high-acoustic-energy");
      }

      if (prosody.pitch !== undefined && isFinite(prosody.pitch)) {
        prosodySum += Math.max(0, Math.min(1, prosody.pitch));
        prosodyFactors++;
        if (prosody.pitch > 0.7) reasons.push("high-vocal-pitch");
      }

      if (prosody.pauseAfter !== undefined && prosody.pauseAfter > 0.2) {
        const pauseScore = Math.min(1.0, prosody.pauseAfter / 0.6);
        prosodySum += pauseScore;
        prosodyFactors++;
        reasons.push("post-vocal-pause");
      }

      if (prosodyFactors > 0) {
        sPros = prosodySum / prosodyFactors;
      }
    } else {
      // Si no hay prosodia disponible, redistribuir peso proporcionalmente hacia léxico y posicional
      sPros = sLex * 0.7 + sPos * 0.3;
    }

    // Ponderación Total
    const rawTotalScore =
      sLex * this.lexicalWeight +
      sPos * this.positionalWeight +
      sPros * this.prosodyWeight;

    const totalScore = Number(Math.max(0, Math.min(1.0, rawTotalScore)).toFixed(3));
    const isEmphasized = totalScore >= this.emphasisThreshold;

    // Determinar prioridad y animación recomendada
    let priority = 5;
    if (totalScore >= 0.70) priority = 1;
    else if (totalScore >= 0.55) priority = 2;
    else if (totalScore >= 0.40) priority = 3;
    else priority = 4;

    let recommendedAnimation: WordAnimationType = "none";
    if (isEmphasized) {
      if (customAnimation) {
        recommendedAnimation = customAnimation;
      } else if (reasons.includes("emphatic-punctuation") || (prosody?.energy ?? 0) > 0.85) {
        recommendedAnimation = "popScale";
      } else if (reasons.includes("high-vocal-pitch") || (prosody?.pitch ?? 0) > 0.80) {
        recommendedAnimation = "colorHighlight";
      } else if (reasons.includes("post-vocal-pause")) {
        recommendedAnimation = "glowPulse";
      } else {
        recommendedAnimation = "popScale";
      }
    }

    return {
      isEmphasized,
      score: totalScore,
      reasons,
      priority,
      recommendedAnimation,
      recommendedEmojiTag: customEmojiTag,
    };
  }
}
