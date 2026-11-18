import {
  PerformanceSegment,
  TakeCandidate,
  TrimProposal,
  PerformanceReviewItem,
  TrimmingMetrics,
  IntelligentTrimReport,
  BestTakeSelection,
  RedundancyCandidate,
  PreservationDecision,
  IntelligentTrimStatus,
} from "./performance-types.js";
import { PerformanceScoring } from "./performance-scoring.js";
import { SemanticRedundancyEngine } from "./semantic-redundancy-engine.js";
import { BestTakeSelector } from "./best-take-selector.js";
import { NaturalPerformancePreservation } from "./natural-performance-preservation.js";

export interface IntelligentTrimProcessInput {
  segments: PerformanceSegment[];
  takeGroups?: Record<string, TakeCandidate[]>;
  sourceDurationSeconds?: number;
  profile?: string;
  narrativeDependencies?: Record<string, string[]>;
}

/**
 * RF-056: IntelligentTrimmingEngine
 * Orquestador puro determinista para la poda semántica y preservación de performance.
 */
export class IntelligentTrimmingEngine {
  public static readonly VERSION = "4.0.0";
  public static readonly MAX_AUTOMATIC_REDUCTION_RATIO = 0.3;
  public static readonly PRE_ROLL_SECONDS = 0.08;
  public static readonly POST_ROLL_SECONDS = 0.12;
  public static readonly MICRO_CROSSFADE_DURATION = 0.025;

  public static process(input: IntelligentTrimProcessInput): IntelligentTrimReport {
    const segments = [...input.segments].sort((a, b) => a.startSeconds - b.startSeconds || a.id.localeCompare(b.id));

    // Validar límites físicos de segmentos
    for (const seg of segments) {
      if (seg.startSeconds < 0 || seg.endSeconds <= seg.startSeconds) {
        throw new Error(
          `IntelligentTrimmingEngine: Segment '${seg.id}' has invalid bounds [${seg.startSeconds}, ${seg.endSeconds}]`
        );
      }
      if (input.sourceDurationSeconds !== undefined && seg.endSeconds > input.sourceDurationSeconds + 1e-4) {
        throw new Error(
          `IntelligentTrimmingEngine: Segment '${seg.id}' end (${seg.endSeconds}) exceeds source duration (${input.sourceDurationSeconds})`
        );
      }
    }

    // 1. Análisis de Redundancia Semántica
    const redundancy = SemanticRedundancyEngine.analyze(segments);

    // 2. Selección de Mejores Tomas
    const takeSelections: BestTakeSelection[] = [];
    if (input.takeGroups) {
      const groupKeys = Object.keys(input.takeGroups).sort();
      for (const grpId of groupKeys) {
        const takes = input.takeGroups[grpId];
        if (takes.length > 0) {
          takeSelections.push(BestTakeSelector.select(grpId, takes));
        }
      }
    }

    // 3. Evaluación de Preservación de Performance Humana
    const preservationDecisions: PreservationDecision[] = [];
    for (const seg of segments) {
      const decs = NaturalPerformancePreservation.evaluate(seg);
      preservationDecisions.push(...decs);
    }

    // 4. Generación de Propuestas de Poda (Proposal-First)
    const proposals: TrimProposal[] = [];
    const reviewQueue: PerformanceReviewItem[] = [];

    // Calcular duración original total
    let originalDuration = 0;
    for (const seg of segments) {
      originalDuration += seg.endSeconds - seg.startSeconds;
    }
    if (input.sourceDurationSeconds !== undefined && input.sourceDurationSeconds > originalDuration) {
      originalDuration = input.sourceDurationSeconds;
    }

    let removedDuration = 0;
    let trimsAccepted = 0;
    let trimsRejected = 0;

    for (const seg of segments) {
      const segDuration = seg.endSeconds - seg.startSeconds;
      const isEvidenceProtected = seg.evidenceProtection === true;
      const hasProtectedMarkers = NaturalPerformancePreservation.hasProtectedHumanMarkers(seg);
      const isOnlyTechnical = NaturalPerformancePreservation.hasOnlyTechnicalErrors(seg);

      // Comprobar si existe dependencia narrativa hacia este segmento
      const hasNarrativeDep =
        input.narrativeDependencies &&
        Object.values(input.narrativeDependencies).some((deps) => deps.includes(seg.id));

      // Comprobar beats narrativos protegidos
      const protectedBeats = new Set(["HOOK", "QUESTION", "EVIDENCE", "CONFLICT", "ESCALATION", "REVELATION", "RESOLUTION"]);
      const isProtectedBeat = seg.beatId !== undefined && protectedBeats.has(seg.beatId);

      // Comprobar recomendación de redundancia que afecte a este segmento
      const redundancyA = redundancy.find((r) => r.segmentAId === seg.id && r.recommendation === "KEEP_B");
      const redundancyB = redundancy.find((r) => r.segmentBId === seg.id && r.recommendation === "KEEP_A");
      const isMarkedRedundant = Boolean(redundancyA || redundancyB);

      if (isOnlyTechnical && !isEvidenceProtected && !hasNarrativeDep && !isProtectedBeat) {
        // Poda automática justificada por error técnico sin dependencias
        const trimStart = Math.max(0, seg.startSeconds - this.PRE_ROLL_SECONDS);
        const trimEnd = seg.endSeconds + this.POST_ROLL_SECONDS;

        proposals.push({
          id: `trim_${seg.id}`,
          sourceClipId: seg.sourceClipId,
          startSeconds: Number(trimStart.toFixed(4)),
          endSeconds: Number(trimEnd.toFixed(4)),
          action: "TRIM",
          reason: "Error técnico/falso inicio detectado sin dependencias narrativas ni probatorias.",
          confidence: 0.92,
          audioTransition: {
            startSeconds: Number(trimStart.toFixed(4)),
            durationSeconds: this.MICRO_CROSSFADE_DURATION,
            type: "MICRO_CROSSFADE",
          },
        });
        removedDuration += segDuration;
        trimsAccepted++;
      } else if (isMarkedRedundant && !isEvidenceProtected && !hasProtectedMarkers && !hasNarrativeDep && !isProtectedBeat) {
        // Poda propuesta por redundancia sin violaciones
        proposals.push({
          id: `trim_${seg.id}`,
          sourceClipId: seg.sourceClipId,
          startSeconds: seg.startSeconds,
          endSeconds: seg.endSeconds,
          action: "TRIM",
          reason: "Segmento redundante sustituido por variante con mayor valor probatorio.",
          confidence: 0.85,
        });
        removedDuration += segDuration;
        trimsAccepted++;
      } else if (hasProtectedMarkers || isEvidenceProtected || hasNarrativeDep || isProtectedBeat) {
        // Protección absoluta
        proposals.push({
          id: `keep_${seg.id}`,
          sourceClipId: seg.sourceClipId,
          startSeconds: seg.startSeconds,
          endSeconds: seg.endSeconds,
          action: "KEEP",
          reason: isEvidenceProtected
            ? "Preservado por protección de evidencia factual obligatoria."
            : hasProtectedMarkers
            ? "Preservado por marcador expresivo humano."
            : "Preservado por rol estructural en el arco narrativo.",
          confidence: 0.95,
        });
      } else if (seg.confidence < 0.7) {
        // Caso ambiguo -> Human Review Queue
        proposals.push({
          id: `review_${seg.id}`,
          sourceClipId: seg.sourceClipId,
          startSeconds: seg.startSeconds,
          endSeconds: seg.endSeconds,
          action: "REVIEW",
          reason: "Confianza insuficiente (< 0.70) para decisión automática.",
          confidence: seg.confidence,
        });
        reviewQueue.push({
          id: `rev_${seg.id}`,
          priority: "HIGH",
          reason: "Segmento ambiguo con baja confianza requiere decisión humana.",
          candidateIds: [seg.id],
          confidence: seg.confidence,
          affectedRange: {
            startSeconds: seg.startSeconds,
            endSeconds: seg.endSeconds,
          },
        });
        trimsRejected++;
      } else {
        proposals.push({
          id: `keep_${seg.id}`,
          sourceClipId: seg.sourceClipId,
          startSeconds: seg.startSeconds,
          endSeconds: seg.endSeconds,
          action: "KEEP",
          reason: "Contenido editorial estándar preservado por omisión de razones de poda.",
          confidence: 0.9,
        });
      }
    }

    // Agregar items de revisión por tomas no resueltas
    for (const ts of takeSelections) {
      if (!ts.isAutoSelected) {
        reviewQueue.push({
          id: `rev_take_${ts.takeGroupId}`,
          priority: "MEDIUM",
          reason: `Selección de toma en grupo '${ts.takeGroupId}' requiere revisión (diferencia de score insuficiente).`,
          candidateIds: [ts.selectedTakeId],
          confidence: ts.winnerScore,
          affectedRange: {
            startSeconds: 0,
            endSeconds: 5.0,
          },
        });
      }
    }

    // Cálculo de Métricas Finales
    const finalDuration = Math.max(0, originalDuration - removedDuration);
    const reductionRatio = originalDuration > 0 ? removedDuration / originalDuration : 0;

    const metrics: TrimmingMetrics = {
      originalDurationSeconds: Number(originalDuration.toFixed(4)),
      finalDurationSeconds: Number(finalDuration.toFixed(4)),
      removedDurationSeconds: Number(removedDuration.toFixed(4)),
      reductionRatio: Number(reductionRatio.toFixed(4)),
      preservedSemanticCoverage: Number(
        (segments.length > 0 ? (segments.length - trimsAccepted) / segments.length : 1.0).toFixed(4)
      ),
      preservedPerformanceCoverage: Number(
        (preservationDecisions.filter((d) => d.action === "PRESERVE").length /
          Math.max(1, preservationDecisions.length)).toFixed(4)
      ),
    };

    // Restricción de sobrepoda (REQ-056.026)
    let status: IntelligentTrimStatus = "PROPOSALS_READY";
    if (reductionRatio > this.MAX_AUTOMATIC_REDUCTION_RATIO) {
      status = "REVIEW_REQUIRED";
    } else if (reviewQueue.length === 0 && trimsAccepted === 0) {
      status = "WITHIN_SAFE_BOUNDS";
    }

    const preliminaryReport: Omit<IntelligentTrimReport, "checksumSha256"> = {
      engineVersion: this.VERSION,
      processedSegments: segments.length,
      redundancyCandidates: redundancy.length,
      trimsProposed: proposals.length,
      trimsAccepted,
      trimsRejected,
      takesEvaluated: takeSelections.length,
      automaticTakeSelections: takeSelections.filter((t) => t.isAutoSelected).length,
      reviewItems: reviewQueue.length,
      metrics,
      proposals,
      takeSelections,
      redundancy,
      preservation: preservationDecisions,
      reviewQueue,
      status,
    };

    const checksumSha256 = PerformanceScoring.computeCanonicalSha256(preliminaryReport);

    return {
      ...preliminaryReport,
      checksumSha256,
    };
  }
}
