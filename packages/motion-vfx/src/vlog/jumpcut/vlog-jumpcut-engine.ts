import {
  JumpCutDecision,
  JumpCutPlan,
  JumpCutStatistics,
  RetainedSegment,
} from "../contracts/jump-cut.types.js";
import {
  BreathEvent,
  SilenceRegion,
  SpeechPause,
  VlogTranscript,
  VlogTranscriptWord,
} from "../contracts/speech.types.js";
import {
  EPSILON,
  JUMP_CUT_DEFAULTS,
  SYNC_TOLERANCES,
} from "../contracts/vlog.constants.js";

/** Opciones de configuración para el VlogJumpCutEngine */
export interface JumpCutEngineOptions {
  silenceThresholdSeconds?: number; // default: 0.25s
  narrativePauseMinSeconds?: number; // default: 0.80s
  microCrossfadeSeconds?: number; // default: 0.010s (10ms)
  wordBoundarySafetySeconds?: number; // default: 0.015s (15ms)
  breathAttenuationDb?: number; // default: -6.0 dB
  preserveNarrativePauses?: boolean; // default: true
}

/**
 * Motor de Detección de Silencios, Protección Fonética y Montaje por Saltos (Milestone 3).
 * Convierte el metraje hablado en una secuencia limpia y dinámica sin cortar palabras
 * y aplicando micro-crossfades deterministas para evitar transientes sonoros.
 */
export class VlogJumpCutEngine {
  /**
   * Genera el plan maestro de edición (JumpCutPlan) para una pista hablada.
   */
  public static createJumpCutPlan(
    projectId: string,
    sourceMediaId: string,
    mediaDurationSeconds: number,
    transcript?: VlogTranscript,
    rawSilences?: SilenceRegion[],
    pauses?: SpeechPause[],
    breaths?: BreathEvent[],
    options: JumpCutEngineOptions = {}
  ): JumpCutPlan {
    const silenceThreshold = options.silenceThresholdSeconds ?? JUMP_CUT_DEFAULTS.SILENCE_THRESHOLD_SECONDS;
    const narrativePauseMin = options.narrativePauseMinSeconds ?? JUMP_CUT_DEFAULTS.NARRATIVE_PAUSE_MIN_SECONDS;
    const microCrossfade = options.microCrossfadeSeconds ?? JUMP_CUT_DEFAULTS.MICRO_CROSSFADE_SECONDS;
    const safetyMargin = options.wordBoundarySafetySeconds ?? SYNC_TOLERANCES.WORD_BOUNDARY_SAFETY_SECONDS;
    const preserveNarrative = options.preserveNarrativePauses ?? true;

    // 1. Extraer y ordenar todas las palabras de la transcripción
    const allWords: VlogTranscriptWord[] = [];
    if (transcript && transcript.segments) {
      for (const seg of transcript.segments) {
        if (seg.words) {
          allWords.push(...seg.words);
        }
      }
    }
    allWords.sort((a, b) => a.startSeconds - b.startSeconds);

    // 2. Extraer o inferir regiones de silencio
    const candidateSilences = this.resolveSilenceRegions(
      mediaDurationSeconds,
      allWords,
      rawSilences
    );

    // 3. Evaluar cada silencio con protección de palabras, pausas narrativas y respiraciones
    const decisions: JumpCutDecision[] = [];
    const approvedCuts: Array<{ start: number; end: number; duration: number }> = [];

    let pausesPreservedCount = 0;
    let breathsAttenuatedCount = 0;

    for (let i = 0; i < candidateSilences.length; i++) {
      const sil = candidateSilences[i];
      let cutStart = sil.startSeconds;
      let cutEnd = sil.endSeconds;

      // Invariante de duración de silencio
      if (cutEnd <= cutStart) continue;

      const initialDuration = cutEnd - cutStart;

      // A. Regla: Silencio <= umbral (0.25s) => Mantener (KEEP)
      if (initialDuration <= silenceThreshold) {
        decisions.push({
          id: `dec_keep_${i + 1}`,
          sourceCutTimeSeconds: cutStart,
          timelineCutTimeSeconds: cutStart,
          action: "KEEP_TRANSITION",
          silenceDurationRemovedSeconds: 0,
          microCrossfadeSeconds: 0,
          reason: `Silence duration ${initialDuration.toFixed(3)}s <= threshold ${silenceThreshold}s`,
        });
        continue;
      }

      // B. Regla: Detección y protección de respiración
      const matchingBreath = (breaths ?? []).find(
        (b) => b.startSeconds >= cutStart - 0.05 && b.endSeconds <= cutEnd + 0.05
      );
      if (matchingBreath && matchingBreath.retain) {
        breathsAttenuatedCount++;
        decisions.push({
          id: `dec_breath_${i + 1}`,
          sourceCutTimeSeconds: cutStart,
          timelineCutTimeSeconds: cutStart,
          action: "ATTENUATE_BREATH",
          silenceDurationRemovedSeconds: 0,
          microCrossfadeSeconds: 0,
          reason: `Breath detected with retention, attenuated by ${options.breathAttenuationDb ?? -6.0}dB`,
        });
        continue;
      }

      // C. Regla: Protección de pausa narrativa explícita o dramática (>= 0.80s)
      const isExplicitNarrative = (pauses ?? []).some(
        (p) => p.type === "NARRATIVE" && p.startSeconds >= cutStart - 0.05 && p.endSeconds <= cutEnd + 0.05
      );
      if (preserveNarrative && (isExplicitNarrative || initialDuration >= narrativePauseMin)) {
        pausesPreservedCount++;
        decisions.push({
          id: `dec_narrative_${i + 1}`,
          sourceCutTimeSeconds: cutStart,
          timelineCutTimeSeconds: cutStart,
          action: "PRESERVE_NARRATIVE_PAUSE",
          silenceDurationRemovedSeconds: 0,
          microCrossfadeSeconds: 0,
          reason: `Narrative pause preserved (${initialDuration.toFixed(3)}s >= ${narrativePauseMin}s)`,
        });
        continue;
      }

      // D. Regla Absoluta de Oro: Protección Fonética contra cortes dentro de palabras
      // Ningún corte puede ocurrir a menos de safetyMargin (15ms) de cualquier palabra
      for (const word of allWords) {
        // Palabra antes del corte
        if (word.endSeconds > cutStart - safetyMargin && word.startSeconds < cutStart) {
          cutStart = Math.max(cutStart, word.endSeconds + safetyMargin);
        }
        // Palabra después del corte
        if (word.startSeconds < cutEnd + safetyMargin && word.endSeconds > cutEnd) {
          cutEnd = Math.min(cutEnd, word.startSeconds - safetyMargin);
        }
        // Palabra completamente dentro del silencio (corte no puede destruir la palabra)
        if (word.startSeconds >= cutStart && word.endSeconds <= cutEnd) {
          // Partir o cancelar corte si contiene una palabra fonética válida
          cutEnd = Math.min(cutEnd, word.startSeconds - safetyMargin);
        }
      }

      const finalDuration = cutEnd - cutStart;

      // Si tras la protección de bordes la duración resultante es menor al umbral, descartar el corte
      if (finalDuration < silenceThreshold) {
        decisions.push({
          id: `dec_protected_${i + 1}`,
          sourceCutTimeSeconds: sil.startSeconds,
          timelineCutTimeSeconds: sil.startSeconds,
          action: "KEEP_TRANSITION",
          silenceDurationRemovedSeconds: 0,
          microCrossfadeSeconds: 0,
          reason: `Silence shrunk below threshold after word boundary protection (${finalDuration.toFixed(3)}s)`,
        });
        continue;
      }

      // Corte aprobado para eliminación
      approvedCuts.push({
        start: cutStart,
        end: cutEnd,
        duration: finalDuration,
      });

      decisions.push({
        id: `dec_cut_${i + 1}`,
        sourceCutTimeSeconds: Number(cutStart.toFixed(4)),
        timelineCutTimeSeconds: 0, // Se calcula tras consolidar la timeline
        action: "CUT_SILENCE",
        silenceDurationRemovedSeconds: Number(finalDuration.toFixed(4)),
        microCrossfadeSeconds: microCrossfade,
        reason: `Silence removed: ${finalDuration.toFixed(3)}s with ${microCrossfade * 1000}ms micro-crossfade`,
      });
    }

    // 4. Fusionar cortes contiguos o solapados
    const mergedCuts = this.mergeOverlappingIntervals(approvedCuts);

    // 5. Construir los segmentos retenidos como complemento de los cortes sobre [0, mediaDurationSeconds]
    const retainedSegments: RetainedSegment[] = [];
    let currentSourceTime = 0.0;
    let currentTimelineTime = 0.0;
    let totalRemovedSeconds = 0.0;

    for (let i = 0; i < mergedCuts.length; i++) {
      const cut = mergedCuts[i];
      if (cut.start > currentSourceTime + EPSILON) {
        const segDuration = cut.start - currentSourceTime;
        retainedSegments.push({
          id: `seg_${retainedSegments.length + 1}`,
          sourceStartSeconds: Number(currentSourceTime.toFixed(4)),
          sourceEndSeconds: Number(cut.start.toFixed(4)),
          timelineStartSeconds: Number(currentTimelineTime.toFixed(4)),
          timelineEndSeconds: Number((currentTimelineTime + segDuration).toFixed(4)),
          durationSeconds: Number(segDuration.toFixed(4)),
          hasSpeech: this.segmentHasWords(currentSourceTime, cut.start, allWords),
        });
        currentTimelineTime += segDuration;
      }
      totalRemovedSeconds += cut.duration;
      currentSourceTime = cut.end;
    }

    // Segmento final tras el último corte
    if (currentSourceTime < mediaDurationSeconds - EPSILON) {
      const segDuration = mediaDurationSeconds - currentSourceTime;
      retainedSegments.push({
        id: `seg_${retainedSegments.length + 1}`,
        sourceStartSeconds: Number(currentSourceTime.toFixed(4)),
        sourceEndSeconds: Number(mediaDurationSeconds.toFixed(4)),
        timelineStartSeconds: Number(currentTimelineTime.toFixed(4)),
        timelineEndSeconds: Number((currentTimelineTime + segDuration).toFixed(4)),
        durationSeconds: Number(segDuration.toFixed(4)),
        hasSpeech: this.segmentHasWords(currentSourceTime, mediaDurationSeconds, allWords),
      });
      currentTimelineTime += segDuration;
    }

    // Caso especial: si ningún corte fue aprobado, retener el metraje completo
    if (retainedSegments.length === 0 && mediaDurationSeconds > 0) {
      retainedSegments.push({
        id: "seg_1",
        sourceStartSeconds: 0.0,
        sourceEndSeconds: Number(mediaDurationSeconds.toFixed(4)),
        timelineStartSeconds: 0.0,
        timelineEndSeconds: Number(mediaDurationSeconds.toFixed(4)),
        durationSeconds: Number(mediaDurationSeconds.toFixed(4)),
        hasSpeech: allWords.length > 0,
      });
      currentTimelineTime = mediaDurationSeconds;
    }

    // 6. Actualizar timestamps relativos en las decisiones de corte
    let timelineOffset = 0;
    for (const dec of decisions) {
      if (dec.action === "CUT_SILENCE") {
        dec.timelineCutTimeSeconds = Number(
          Math.max(0, dec.sourceCutTimeSeconds - timelineOffset).toFixed(4)
        );
        timelineOffset += dec.silenceDurationRemovedSeconds;
      }
    }

    // 7. Estadísticas finales
    const editedDuration = Number(currentTimelineTime.toFixed(4));
    const totalTimeSaved = Number(totalRemovedSeconds.toFixed(4));
    const percentSaved = mediaDurationSeconds > 0
      ? Number(((totalTimeSaved / mediaDurationSeconds) * 100).toFixed(2))
      : 0;

    const statistics: JumpCutStatistics = {
      originalDurationSeconds: Number(mediaDurationSeconds.toFixed(4)),
      editedDurationSeconds: editedDuration,
      totalTimeSavedSeconds: totalTimeSaved,
      percentSaved,
      cutsCount: mergedCuts.length,
      pausesPreservedCount,
      breathsAttenuatedCount,
      punchInsAppliedCount: 0,
    };

    return {
      projectId,
      sourceMediaId,
      retainedSegments,
      decisions,
      punchIns: [], // Se poblará mediante DynamicPunchIn
      statistics,
      silencesAnalyzed: candidateSilences,
    };
  }

  /**
   * Resuelve los silencios candidatos: utiliza los provistos o deduce los espacios entre palabras.
   */
  private static resolveSilenceRegions(
    mediaDurationSeconds: number,
    words: VlogTranscriptWord[],
    rawSilences?: SilenceRegion[]
  ): SilenceRegion[] {
    if (rawSilences && rawSilences.length > 0) {
      return rawSilences;
    }

    if (words.length === 0) {
      // Todo el metraje es silencio
      return [
        {
          startSeconds: 0.0,
          endSeconds: mediaDurationSeconds,
          durationSeconds: mediaDurationSeconds,
          averageEnergyRms: 0.0,
        },
      ];
    }

    const silences: SilenceRegion[] = [];

    // Silencio previo a la primera palabra
    if (words[0].startSeconds > 0.05) {
      silences.push({
        startSeconds: 0.0,
        endSeconds: words[0].startSeconds,
        durationSeconds: words[0].startSeconds,
        averageEnergyRms: 0.0,
      });
    }

    // Silencios entre palabras consecutivas
    for (let i = 0; i < words.length - 1; i++) {
      const currentEnd = words[i].endSeconds;
      const nextStart = words[i + 1].startSeconds;

      if (nextStart > currentEnd + 0.01) {
        const gap = nextStart - currentEnd;
        silences.push({
          startSeconds: currentEnd,
          endSeconds: nextStart,
          durationSeconds: gap,
          averageEnergyRms: 0.0,
        });
      }
    }

    // Silencio posterior a la última palabra
    const lastEnd = words[words.length - 1].endSeconds;
    if (lastEnd < mediaDurationSeconds - 0.05) {
      silences.push({
        startSeconds: lastEnd,
        endSeconds: mediaDurationSeconds,
        durationSeconds: mediaDurationSeconds - lastEnd,
        averageEnergyRms: 0.0,
      });
    }

    return silences;
  }

  private static mergeOverlappingIntervals(
    intervals: Array<{ start: number; end: number; duration: number }>
  ): Array<{ start: number; end: number; duration: number }> {
    if (intervals.length <= 1) return intervals;

    intervals.sort((a, b) => a.start - b.start);
    const merged: Array<{ start: number; end: number; duration: number }> = [intervals[0]];

    for (let i = 1; i < intervals.length; i++) {
      const current = intervals[i];
      const prev = merged[merged.length - 1];

      if (current.start <= prev.end + 0.01) {
        prev.end = Math.max(prev.end, current.end);
        prev.duration = prev.end - prev.start;
      } else {
        merged.push({ ...current });
      }
    }

    return merged;
  }

  private static segmentHasWords(
    start: number,
    end: number,
    words: VlogTranscriptWord[]
  ): boolean {
    return words.some((w) => w.startSeconds < end && w.endSeconds > start);
  }
}
