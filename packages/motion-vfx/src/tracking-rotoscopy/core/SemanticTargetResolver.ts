import { SemanticTargetQuery, Track } from "../types/index.js";

/**
 * Resolvedor semántico de objetivos de tracking para la IA (Fase 12).
 */
export class SemanticTargetResolver {
  /**
   * Resuelve la mejor pista de tracking correspondiente a una consulta semántica.
   */
  public static resolveTarget(
    tracks: Track[],
    query: SemanticTargetQuery
  ): Track | undefined {
    const candidates = tracks.filter((t) => {
      const classMatch =
        !query.semanticClass ||
        (t.semanticClass && t.semanticClass.toLowerCase() === query.semanticClass.toLowerCase());
      const roleMatch = !query.role || t.role === query.role;
      return classMatch && roleMatch;
    });

    if (candidates.length === 0) return undefined;

    // Ordenar por prioridad: main_subject > mayor confianza
    candidates.sort((a, b) => {
      if (a.role === "main_subject" && b.role !== "main_subject") return -1;
      if (b.role === "main_subject" && a.role !== "main_subject") return 1;
      return b.confidence - a.confidence;
    });

    return candidates[0];
  }
}
