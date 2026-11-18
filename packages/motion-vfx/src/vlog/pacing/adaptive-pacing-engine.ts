import { SupportedLocale } from "../contracts/language.types.js";
import {
  PacingAdjustment,
  PacingConflict,
  PacingRequest,
  PacingResult,
  PacingResultSchema,
  SegmentAlignment,
} from "../contracts/pacing.types.js";
import { VoiceoverTrack } from "../contracts/voiceover.types.js";
import {
  EPSILON,
  PACING_DEFAULTS,
  SYNC_TOLERANCES,
} from "../contracts/vlog.constants.js";
import { AnchorResolver, NarrativeAnchor } from "./anchor-resolver.js";
import { BRollPacingAssignment, BRollPacingResolver } from "./broll-pacing-resolver.js";
import { PacingConflictResolver } from "./pacing-conflict-resolver.js";
import { TimeMapper } from "./time-mapper.js";
import { VisualRetimingResolver } from "./visual-retiming-resolver.js";
import { VoiceStretchResolver } from "./voice-stretch-resolver.js";

/** Opciones de configuración avanzadas para el motor de pacing */
export interface AdaptivePacingOptions {
  allowManualOverride?: boolean;
  maxHoldDurationSeconds?: number;
  maxSpeedFactor?: number;
  minSpeedFactor?: number;
}

/**
 * Motor de Ritmo Adaptativo y Sincronización Temporal Multilingüe (Milestone 5).
 * Adapta el timeline visual a la duración real de cada locución por idioma de forma
 * puramente declarativa, determinista y matemáticamente acotada.
 */
export class VlogAdaptivePacingEngine {
  /**
   * Planifica la adaptación temporal de un timeline a una pista de locución por idioma.
   */
  public static plan(
    request: PacingRequest,
    voiceoverTrack?: VoiceoverTrack,
    anchors: NarrativeAnchor[] = [],
    brollAssignments: BRollPacingAssignment[] = [],
    options: AdaptivePacingOptions = {}
  ): PacingResult & { timeMapper: TimeMapper } {
    const locale = request.locale;
    const sourceDuration = request.sourceTimelineDurationSeconds;
    const voiceDuration = request.voiceDurationSeconds;
    const allowOverride = options.allowManualOverride ?? false;

    const adjustments: PacingAdjustment[] = [];
    const alignments: SegmentAlignment[] = [];
    const conflicts: PacingConflict[] = [];

    const timeMapper = new TimeMapper();

    // 1. Evaluación global de elasticidad vocal
    const stretchDecision = VoiceStretchResolver.evaluateStretch(
      voiceDuration,
      sourceDuration,
      allowOverride,
      request.allowStretchRange
    );

    let voiceStretchFactor = 1.0;
    let adaptedDuration = sourceDuration;

    // 2. Si la pista de voz contiene segmentos individuales, procesar segmento por segmento
    if (voiceoverTrack && voiceoverTrack.segments.length > 0) {
      let currentDerivedTimeline = 0.0;

      for (let i = 0; i < voiceoverTrack.segments.length; i++) {
        const seg = voiceoverTrack.segments[i];
        const segTargetDuration = seg.durationSeconds;

        // Estimar duración fuente proporcional o usar segmentStart/End si existen
        const segSourceDuration = (seg.endSeconds - seg.startSeconds) > 0
          ? seg.endSeconds - seg.startSeconds
          : segTargetDuration;

        const segDelta = segTargetDuration - segSourceDuration;

        // A. Verificar B-Roll asociado
        const broll = brollAssignments.find((b) => b.mediaId === seg.narrativeSegmentId);
        if (broll) {
          const brollRes = BRollPacingResolver.retimeBRoll(broll, segTargetDuration);
          adjustments.push({
            segmentId: seg.narrativeSegmentId,
            strategy: brollRes.strategyApplied === "TRIMMED" ? "BROLL_TRIMMED" : "BROLL_EXTENDED",
            appliedRatio: Number((segTargetDuration / segSourceDuration).toFixed(3)),
            deltaSeconds: Number(segDelta.toFixed(4)),
            rationale: `B-Roll retimed via ${brollRes.strategyApplied} to match voice segment (${segTargetDuration.toFixed(2)}s)`,
          });
        }

        // B. Retiming visual declarativo
        const retiming = VisualRetimingResolver.resolve(
          seg.narrativeSegmentId,
          segSourceDuration,
          segTargetDuration,
          segSourceDuration * 1.5,
          { maxHoldDurationSeconds: options.maxHoldDurationSeconds ?? 2.0 }
        );

        if (!retiming.isPossible) {
          conflicts.push(
            PacingConflictResolver.createConflict({
              segmentId: seg.narrativeSegmentId,
              locale,
              conflictType: "NO_VALID_SOLUTION",
              severity: "BLOCKING",
              unresolvedDeltaSeconds: segDelta,
              requiredVoiceStretch: Number((segTargetDuration / segSourceDuration).toFixed(3)),
              measuredValue: segTargetDuration,
              allowedValue: segSourceDuration,
              suggestedAction: "EXTEND_BROLL_FURTHER",
              description: retiming.reason,
            })
          );
        }

        // C. Mapeo temporal del segmento
        timeMapper.addInterval({
          sourceStart: seg.startSeconds,
          sourceEnd: seg.endSeconds,
          derivedStart: currentDerivedTimeline,
          derivedEnd: currentDerivedTimeline + segTargetDuration,
          strategy: segDelta > 0 ? "STRETCH" : (segDelta < 0 ? "TRIM" : "KEEP"),
          scaleFactor: Number((segTargetDuration / segSourceDuration).toFixed(4)),
        });

        // D. Alineación y deriva
        const drift = Number((currentDerivedTimeline - seg.startSeconds).toFixed(4));
        const withinTolerance = Math.abs(drift) <= SYNC_TOLERANCES.SUBTITLE_WORD_DRIFT_SECONDS; // 40ms

        alignments.push({
          narrativeSegmentId: seg.narrativeSegmentId,
          voiceStartSeconds: seg.startSeconds,
          voiceEndSeconds: seg.endSeconds,
          visualStartSeconds: currentDerivedTimeline,
          visualEndSeconds: currentDerivedTimeline + segTargetDuration,
          driftSeconds: drift,
          isWithinDriftTolerance: withinTolerance,
        });

        currentDerivedTimeline += segTargetDuration;
      }

      adaptedDuration = Number(currentDerivedTimeline.toFixed(4));
    } else {
      // Caso de adaptación global (sin segmentos detallados)
      if (stretchDecision.applied) {
        voiceStretchFactor = stretchDecision.ratio;
        adaptedDuration = Number((sourceDuration * voiceStretchFactor).toFixed(4));

        adjustments.push({
          segmentId: "global_timeline",
          strategy: "VOICE_MICRO_STRETCH",
          appliedRatio: voiceStretchFactor,
          deltaSeconds: Number((adaptedDuration - sourceDuration).toFixed(4)),
          rationale: stretchDecision.reason,
        });

        timeMapper.addInterval({
          sourceStart: 0,
          sourceEnd: sourceDuration,
          derivedStart: 0,
          derivedEnd: adaptedDuration,
          strategy: voiceStretchFactor !== 1.0 ? "STRETCH" : "KEEP",
          scaleFactor: voiceStretchFactor,
        });
      } else {
        // Conflicto de stretch
        conflicts.push(
          PacingConflictResolver.createConflict({
            segmentId: "global_timeline",
            locale,
            conflictType: "STRETCH_LIMIT_EXCEEDED",
            severity: "BLOCKING",
            unresolvedDeltaSeconds: voiceDuration - sourceDuration,
            requiredVoiceStretch: stretchDecision.ratio,
            measuredValue: stretchDecision.ratio,
            allowedValue: PACING_DEFAULTS.AUTOMATIC_STRETCH_MAX,
            suggestedAction: "MANUAL_SCRIPT_EDIT",
            description: stretchDecision.reason,
          })
        );
      }
    }

    // 3. Resolución y verificación de anclas narrativas
    for (const anchor of anchors) {
      const derivedAnchorTime = timeMapper.mapSourceToDerived(anchor.sourceTimeSeconds);
      const anchorRes = AnchorResolver.evaluateAnchor(anchor, derivedAnchorTime);

      if (!anchorRes.isCompliant) {
        conflicts.push(
          PacingConflictResolver.createConflict({
            segmentId: `anchor_${anchor.id}`,
            locale,
            conflictType: "ANCHOR_DRIFT",
            severity: anchorRes.status === "FATAL" || anchor.locked ? "BLOCKING" : "WARNING",
            unresolvedDeltaSeconds: anchorRes.driftSeconds,
            requiredVoiceStretch: 1.0,
            measuredValue: anchorRes.driftSeconds,
            allowedValue: anchor.toleranceSeconds ?? 0.040,
            suggestedAction: "ADD_PAUSE",
            description: anchorRes.message,
          })
        );
      }
    }

    const deltaFromSource = Number((adaptedDuration - sourceDuration).toFixed(4));
    const hasBlockingConflict = conflicts.some((c) => c.severity === "BLOCKING");

    const result: PacingResult = {
      locale,
      adaptedDurationSeconds: Math.max(0.1, adaptedDuration),
      deltaFromSourceSeconds: deltaFromSource,
      adjustments,
      alignments,
      conflicts,
      voiceStretchFactor: Number(voiceStretchFactor.toFixed(3)),
      success: !hasBlockingConflict,
    };

    // Validar esquema formal Zod
    PacingResultSchema.parse(result);

    return {
      ...result,
      timeMapper,
    };
  }
}
