import crypto from "node:crypto";
import { PerformanceMarker, TakeCandidate } from "./performance-types.js";

/**
 * RF-056: Scoring, Similarity & Hashing Utilities for Performance Engine
 */
export class PerformanceScoring {
  // Canonical serialization & SHA-256
  public static canonicalize(obj: unknown): unknown {
    if (obj === null || obj === undefined) return null;
    if (typeof obj === "number") {
      if (!Number.isFinite(obj)) {
        throw new Error(`PerformanceScoring: Non-finite number (${obj}) cannot be serialized`);
      }
      const rounded = Number(obj.toFixed(4));
      return rounded === 0 ? 0 : rounded;
    }
    if (typeof obj === "string" || typeof obj === "boolean") return obj;
    if (Array.isArray(obj)) return obj.map((item) => this.canonicalize(item));
    if (typeof obj === "object") {
      const rec = obj as Record<string, unknown>;
      const keys = Object.keys(rec)
        .filter((k) => k !== "checksumSha256" && rec[k] !== undefined)
        .sort((a, b) => a.localeCompare(b, "en", { numeric: true }));
      const sorted: Record<string, unknown> = {};
      for (const k of keys) sorted[k] = this.canonicalize(rec[k]);
      return sorted;
    }
    return String(obj);
  }

  public static canonicalStringify(obj: unknown): string {
    return JSON.stringify(this.canonicalize(obj));
  }

  public static computeCanonicalSha256(obj: unknown): string {
    const canonical = this.canonicalStringify(obj);
    return crypto.createHash("sha256").update(canonical, "utf8").digest("hex");
  }

  /**
   * REQ-056.013: Normalización léxica determinista.
   */
  public static tokenize(text: string): string[] {
    const normalized = text
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "") // remove accents for comparison
      .replace(/[^\w\s]/g, " ")
      .trim();

    if (!normalized) return [];
    return normalized.split(/\s+/);
  }

  private static STOPWORDS = new Set([
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "a", "al", "en", "con", "por", "para",
    "y", "o", "pero", "que", "es", "son", "fue", "era", "se", "su", "sus", "the", "a", "an", "and", "or", "but",
    "in", "on", "at", "to", "for", "of", "with", "is", "are", "was", "were", "it", "that", "this",
  ]);

  /**
   * REQ-056.013: Similitud léxica basada en tokens de contenido.
   */
  public static calculateSemanticSimilarity(textA: string, textB: string): number {
    const tokensA = this.tokenize(textA).filter((t) => !this.STOPWORDS.has(t));
    const tokensB = this.tokenize(textB).filter((t) => !this.STOPWORDS.has(t));

    if (tokensA.length === 0 && tokensB.length === 0) return 1.0;
    if (tokensA.length === 0 || tokensB.length === 0) return 0.0;

    const setA = new Set(tokensA);
    const setB = new Set(tokensB);

    let intersectionCount = 0;
    for (const t of setA) {
      if (setB.has(t)) intersectionCount++;
    }

    const unionCount = new Set([...setA, ...setB]).size;
    const jaccard = unionCount > 0 ? intersectionCount / unionCount : 0.0;
    return Number(Math.max(0.0, Math.min(1.0, jaccard)).toFixed(4));
  }

  /**
   * REQ-056.011: Solapamiento de información (Overlap Coefficient).
   */
  public static calculateInformationOverlap(textA: string, textB: string): number {
    const tokensA = this.tokenize(textA).filter((t) => !this.STOPWORDS.has(t));
    const tokensB = this.tokenize(textB).filter((t) => !this.STOPWORDS.has(t));
    if (tokensA.length === 0 && tokensB.length === 0) return 1.0;
    if (tokensA.length === 0 || tokensB.length === 0) return 0.0;

    const setA = new Set(tokensA);
    const setB = new Set(tokensB);

    let intersectionCount = 0;
    for (const t of setA) {
      if (setB.has(t)) intersectionCount++;
    }

    const minSize = Math.min(setA.size, setB.size);
    const overlap = minSize > 0 ? intersectionCount / minSize : 0.0;
    return Number(Math.max(0.0, Math.min(1.0, overlap)).toFixed(4));
  }

  /**
   * REQ-056.020: Detecta si textB contiene hechos, cifras o fuentes no presentes en textA.
   */
  public static hasNewInformationalValue(textA: string, textB: string): boolean {
    const numRegex = /\b\d+(?:[.,]\d+)?\b/g;
    const numbersA = new Set(textA.match(numRegex) ?? []);
    const numbersB = new Set(textB.match(numRegex) ?? []);

    // Check if B has numbers/dates that A lacks
    for (const n of numbersB) {
      if (!numbersA.has(n)) return true;
    }

    // Check citation/source keywords in B
    const sourceKeywords = ["segun", "informe", "fuente", "estudio", "oficial", "report", "according", "data"];
    const tokensB = this.tokenize(textB);
    const tokensA = new Set(this.tokenize(textA));
    for (const kw of sourceKeywords) {
      if (tokensB.includes(kw) && !tokensA.has(kw)) return true;
    }

    return false;
  }

  /**
   * REQ-056.012: Score de redundancia compuesto [0, 1].
   * redundancyScore = 0.40 * semanticSimilarity + 0.30 * informationOverlap + 0.15 * temporalProximity + 0.15 * narrativeRoleOverlap
   */
  public static calculateRedundancyScore(params: {
    semanticSimilarity: number;
    informationOverlap: number;
    temporalDistanceSeconds: number;
    narrativeRoleA?: string;
    narrativeRoleB?: string;
  }): number {
    const sem = Math.max(0.0, Math.min(1.0, params.semanticSimilarity));
    const info = Math.max(0.0, Math.min(1.0, params.informationOverlap));
    const temporalProximity = Math.max(0.0, Math.min(1.0, 1.0 - params.temporalDistanceSeconds / 60.0));
    const narrativeOverlap =
      params.narrativeRoleA && params.narrativeRoleB && params.narrativeRoleA === params.narrativeRoleB ? 1.0 : 0.5;

    const raw = 0.4 * sem + 0.3 * info + 0.15 * temporalProximity + 0.15 * narrativeOverlap;
    return Number(Math.max(0.0, Math.min(1.0, raw)).toFixed(4));
  }

  /**
   * REQ-056.040: Score ponderado de toma [0, 1].
   */
  public static calculateTakeScore(take: TakeCandidate): number {
    const duration = take.endSeconds - take.startSeconds;
    // Optimal duration efficiency: ideal around 3-8s
    const durEfficiency = duration > 0 ? Math.max(0.0, Math.min(1.0, 1.0 - Math.abs(duration - 5.0) / 10.0)) : 0.0;

    const raw =
      0.2 * take.semanticIntegrity +
      0.15 * take.phoneticClarity +
      0.15 * take.vocalEnergy +
      0.1 * take.visualStability +
      0.1 * take.eyeContact +
      0.1 * take.naturalPerformance +
      0.1 * take.continuity +
      0.05 * take.audioQuality +
      0.05 * durEfficiency;

    return Number(Math.max(0.0, Math.min(1.0, raw)).toFixed(4));
  }

  /**
   * REQ-056.040: Desempate determinista entre tomas.
   */
  public static breakTakeTie(takeA: TakeCandidate, takeB: TakeCandidate): { winner: TakeCandidate; reason: string } {
    if (takeA.semanticIntegrity !== takeB.semanticIntegrity) {
      return {
        winner: takeA.semanticIntegrity > takeB.semanticIntegrity ? takeA : takeB,
        reason: "Mayor integridad semántica",
      };
    }
    if (takeA.naturalPerformance !== takeB.naturalPerformance) {
      return {
        winner: takeA.naturalPerformance > takeB.naturalPerformance ? takeA : takeB,
        reason: "Mayor naturalidad",
      };
    }
    if (takeA.phoneticClarity !== takeB.phoneticClarity) {
      return {
        winner: takeA.phoneticClarity > takeB.phoneticClarity ? takeA : takeB,
        reason: "Mayor claridad fonética",
      };
    }
    if (takeA.continuity !== takeB.continuity) {
      return {
        winner: takeA.continuity > takeB.continuity ? takeA : takeB,
        reason: "Mejor continuidad",
      };
    }
    const durA = takeA.endSeconds - takeA.startSeconds;
    const durB = takeB.endSeconds - takeB.startSeconds;
    if (Math.abs(durA - durB) > 1e-4) {
      return {
        winner: durA < durB ? takeA : takeB,
        reason: "Menor duración",
      };
    }
    return {
      winner: takeA.id.localeCompare(takeB.id) < 0 ? takeA : takeB,
      reason: "ID lexicográficamente menor",
    };
  }

  /**
   * REQ-056.030, REQ-056.031, REQ-056.032: Evaluación de preservación de marcadores humanos.
   */
  public static evaluateMarkerPreservation(marker: PerformanceMarker): {
    action: "PRESERVE" | "TRIM" | "REVIEW";
    preservationScore: number;
    authenticityScore: number;
    technicalDefectScore: number;
    reason: string;
    confidence: number;
  } {
    switch (marker) {
      case "BREATH":
        return {
          action: "PRESERVE",
          preservationScore: 0.85,
          authenticityScore: 0.9,
          technicalDefectScore: 0.1,
          reason: "Respiración expresiva humana preservada.",
          confidence: 0.95,
        };
      case "LAUGH":
        return {
          action: "PRESERVE",
          preservationScore: 0.95,
          authenticityScore: 0.98,
          technicalDefectScore: 0.05,
          reason: "Risa espontánea protegida por valor de autenticidad.",
          confidence: 0.98,
        };
      case "REFLECTIVE_PAUSE":
      case "EMPHATIC_PAUSE":
        return {
          action: "PRESERVE",
          preservationScore: 0.88,
          authenticityScore: 0.85,
          technicalDefectScore: 0.15,
          reason: "Pausa reflexiva/enfática protegida para mantener ritmo orgánico.",
          confidence: 0.92,
        };
      case "EMOTIONAL_REACTION":
        return {
          action: "PRESERVE",
          preservationScore: 0.92,
          authenticityScore: 0.95,
          technicalDefectScore: 0.1,
          reason: "Reacción emocional genuina preservada.",
          confidence: 0.94,
        };
      case "FALSE_START":
        return {
          action: "TRIM",
          preservationScore: 0.15,
          authenticityScore: 0.2,
          technicalDefectScore: 0.88,
          reason: "Falso inicio técnico propuesto para eliminación.",
          confidence: 0.92,
        };
      case "TECHNICAL_ERROR":
        return {
          action: "TRIM",
          preservationScore: 0.0,
          authenticityScore: 0.0,
          technicalDefectScore: 1.0,
          reason: "Error técnico eliminable categóricamente.",
          confidence: 1.0,
        };
      case "WORD_REPETITION":
      case "STUTTER":
        return {
          action: "TRIM",
          preservationScore: 0.25,
          authenticityScore: 0.3,
          technicalDefectScore: 0.75,
          reason: "Repetición accidental o tartamudeo técnico propuesto para poda.",
          confidence: 0.86,
        };
      case "HESITATION":
      case "FILLER":
      case "UNCERTAINTY":
      default:
        return {
          action: "REVIEW",
          preservationScore: 0.5,
          authenticityScore: 0.5,
          technicalDefectScore: 0.5,
          reason: "Marcador ambiguo requiere revisión humana.",
          confidence: 0.65,
        };
    }
  }
}
