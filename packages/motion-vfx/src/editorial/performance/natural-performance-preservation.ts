import { PerformanceMarker, PerformanceSegment, PreservationDecision } from "./performance-types.js";
import { PerformanceScoring } from "./performance-scoring.js";

/**
 * RF-056: NaturalPerformancePreservation
 * Clasifica imperfecciones en técnicas vs humanas y protege la organicidad interpretativa.
 */
export class NaturalPerformancePreservation {
  public static evaluate(segment: PerformanceSegment): PreservationDecision[] {
    const decisions: PreservationDecision[] = [];

    for (const marker of segment.markers) {
      const evalResult = PerformanceScoring.evaluateMarkerPreservation(marker);
      decisions.push({
        marker,
        action: evalResult.action,
        preservationScore: evalResult.preservationScore,
        authenticityScore: evalResult.authenticityScore,
        technicalDefectScore: evalResult.technicalDefectScore,
        reason: evalResult.reason,
        confidence: evalResult.confidence,
      });
    }

    return decisions;
  }

  /**
   * Determina si un segmento contiene marcadores humanos protegidos que impiden su poda automática.
   */
  public static hasProtectedHumanMarkers(segment: PerformanceSegment): boolean {
    const protectedSet = new Set<PerformanceMarker>([
      "BREATH",
      "LAUGH",
      "REFLECTIVE_PAUSE",
      "EMPHATIC_PAUSE",
      "EMOTIONAL_REACTION",
    ]);

    return segment.markers.some((m) => protectedSet.has(m));
  }

  /**
   * Determina si un segmento contiene únicamente errores técnicos que justifican su propuesta de eliminación.
   */
  public static hasOnlyTechnicalErrors(segment: PerformanceSegment): boolean {
    if (segment.markers.length === 0) return false;
    const technicalSet = new Set<PerformanceMarker>([
      "FALSE_START",
      "TECHNICAL_ERROR",
      "STUTTER",
      "WORD_REPETITION",
    ]);

    return segment.markers.every((m) => technicalSet.has(m));
  }
}
