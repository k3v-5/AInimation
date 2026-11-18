import { PerformanceSegment, RedundancyCandidate } from "./performance-types.js";
import { PerformanceScoring } from "./performance-scoring.js";

/**
 * RF-056: SemanticRedundancyEngine
 * Detecta redundancia semántica entre narrador, entrevistados y tomas sin destruir evidencia factual.
 */
export class SemanticRedundancyEngine {
  public static analyze(segments: PerformanceSegment[]): RedundancyCandidate[] {
    const candidates: RedundancyCandidate[] = [];

    for (let i = 0; i < segments.length; i++) {
      for (let j = i + 1; j < segments.length; j++) {
        const segA = segments[i];
        const segB = segments[j];

        const similarity = PerformanceScoring.calculateSemanticSimilarity(segA.transcript, segB.transcript);
        const overlap = PerformanceScoring.calculateInformationOverlap(segA.transcript, segB.transcript);
        const temporalDist = Math.abs(segB.startSeconds - segA.endSeconds);

        // If similarity is negligible, skip
        if (similarity < 0.15 && overlap < 0.2) continue;

        const redundancyScore = PerformanceScoring.calculateRedundancyScore({
          semanticSimilarity: similarity,
          informationOverlap: overlap,
          temporalDistanceSeconds: temporalDist,
          narrativeRoleA: segA.narrativeRole,
          narrativeRoleB: segB.narrativeRole,
        });

        // REQ-056.020: Verificación de Evidencia e Información Nueva
        const bHasNewInfo = PerformanceScoring.hasNewInformationalValue(segA.transcript, segB.transcript);
        const aHasNewInfo = PerformanceScoring.hasNewInformationalValue(segB.transcript, segA.transcript);
        const aProtected = segA.evidenceProtection === true;
        const bProtected = segB.evidenceProtection === true;

        let recommendation: "KEEP_BOTH" | "KEEP_A" | "KEEP_B" | "REVIEW";
        let reason = "";
        let confidence = Math.max(0.0, Math.min(1.0, (segA.confidence + segB.confidence) / 2.0));

        if (aProtected && bProtected) {
          recommendation = "KEEP_BOTH";
          reason = "Ambos segmentos contienen evidencia factual protegida obligatoria.";
        } else if (bHasNewInfo && !aHasNewInfo) {
          recommendation = "KEEP_B";
          reason = "El segmento B aporta datos fácticos, fuentes o cifras no presentes en A.";
        } else if (aHasNewInfo && !bHasNewInfo) {
          recommendation = "KEEP_A";
          reason = "El segmento A aporta mayor precisión factual que B.";
        } else if (redundancyScore >= 0.75) {
          // Alta redundancia
          if (bProtected) {
            recommendation = "KEEP_B";
            reason = "Redundancia alta; se preserva B por protección de evidencia.";
          } else if (aProtected) {
            recommendation = "KEEP_A";
            reason = "Redundancia alta; se preserva A por protección de evidencia.";
          } else {
            recommendation = "REVIEW";
            reason = "Redundancia semántica elevada sin evidencia concluyente de sustitución automática.";
          }
        } else if (redundancyScore < 0.4) {
          recommendation = "KEEP_BOTH";
          reason = "Similitud superficial o complementaria; no existe redundancia perjudicial.";
        } else {
          recommendation = "REVIEW";
          reason = "Similitud moderada requiere juicio editorial.";
        }

        candidates.push({
          id: `red_${segA.id}_${segB.id}`,
          segmentAId: segA.id,
          segmentBId: segB.id,
          semanticSimilarity: similarity,
          informationOverlap: overlap,
          temporalDistanceSeconds: Number(temporalDist.toFixed(4)),
          narrativeRoleA: segA.narrativeRole,
          narrativeRoleB: segB.narrativeRole,
          redundancyScore,
          recommendation,
          reason,
          confidence: Number(confidence.toFixed(4)),
        });
      }
    }

    // Ordenamiento determinista
    return candidates.sort((a, b) => b.redundancyScore - a.redundancyScore || a.id.localeCompare(b.id));
  }
}
