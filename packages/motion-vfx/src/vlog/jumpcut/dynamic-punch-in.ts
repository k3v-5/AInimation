import { PunchInDecision } from "../contracts/jump-cut.types.js";
import { EyeAnchor, FaceTrack } from "../contracts/speech.types.js";
import { PUNCH_IN_DEFAULTS } from "../contracts/vlog.constants.js";

/** Solicitud de disparo de Punch-In candidato */
export interface PunchInCandidateTrigger {
  timeSeconds: number;
  trigger: "EMPHASIS_KEYWORD" | "TOPIC_SHIFT" | "NARRATIVE_CLIMAX" | "MANUAL_OVERRIDE";
  holdDurationSeconds?: number;
  focalPointNormalized?: { x: number; y: number };
  coveredByBRoll?: boolean;
}

/** Opciones de configuración para DynamicPunchIn */
export interface DynamicPunchInOptions {
  standardScale?: number; // default: 1.15
  microScale?: number; // default: 1.12
  maxScaleCeiling?: number; // default: 1.20
  cooldownSeconds?: number; // default: 3.0s
  smoothingAlpha?: number; // default: 0.20
}

/**
 * Generador y estabilizador de Punch-In Dinámico (Milestone 3).
 * Modula el encuadre óptico $100\% \to 115\% \to 100\%$ centrado en los ojos del orador
 * con enfriamiento temporal (cooldown), interpolación suave y respeto absoluto a la precedencia del B-Roll.
 */
export class DynamicPunchIn {
  /**
   * Genera las decisiones de Punch-In deterministas para una secuencia temporal.
   */
  public static generatePunchIns(
    candidateTriggers: PunchInCandidateTrigger[],
    faceTracks?: FaceTrack[],
    options: DynamicPunchInOptions = {}
  ): PunchInDecision[] {
    if (!candidateTriggers || candidateTriggers.length === 0) {
      return [];
    }

    const standardScale = this.sanitizeScale(
      options.standardScale ?? PUNCH_IN_DEFAULTS.STANDARD_PUNCH_SCALE
    );
    const microScale = this.sanitizeScale(
      options.microScale ?? PUNCH_IN_DEFAULTS.MICRO_PUNCH_SCALE
    );
    const cooldown = options.cooldownSeconds ?? PUNCH_IN_DEFAULTS.COOLDOWN_SECONDS;
    const alpha = options.smoothingAlpha ?? PUNCH_IN_DEFAULTS.FOCAL_SMOOTHING_ALPHA;

    // 1. Ordenar disparadores cronológicamente
    const sorted = [...candidateTriggers].sort((a, b) => a.timeSeconds - b.timeSeconds);

    // 2. Filtrar por Cooldown respetando jerarquía de prioridad
    const acceptedTriggers: PunchInCandidateTrigger[] = [];

    const priorityRank: Record<PunchInCandidateTrigger["trigger"], number> = {
      MANUAL_OVERRIDE: 4,
      NARRATIVE_CLIMAX: 3,
      TOPIC_SHIFT: 2,
      EMPHASIS_KEYWORD: 1,
    };

    for (const trig of sorted) {
      if (acceptedTriggers.length === 0) {
        acceptedTriggers.push(trig);
        continue;
      }

      const lastAccepted = acceptedTriggers[acceptedTriggers.length - 1];
      const timeSinceLast = trig.timeSeconds - lastAccepted.timeSeconds;

      if (timeSinceLast >= cooldown) {
        acceptedTriggers.push(trig);
      } else {
        // Conflicto dentro del cooldown: conservar el de mayor prioridad
        const lastPriority = priorityRank[lastAccepted.trigger];
        const currentPriority = priorityRank[trig.trigger];

        if (currentPriority > lastPriority) {
          // Reemplazar el anterior por el de mayor jerarquía editorial
          acceptedTriggers[acceptedTriggers.length - 1] = trig;
        }
        // Si la prioridad actual es menor o igual, descartar el evento dentro del cooldown (determinista)
      }
    }

    // 3. Resolver anclaje focal y suavizado exponencial (Eye Tracking)
    const activeFace = faceTracks?.find((f) => f.isActiveSpeaker) ?? faceTracks?.[0];
    let smoothedFocalPoint = { x: 0.50, y: 0.50 }; // Centro de encuadre por defecto

    const decisions: PunchInDecision[] = [];

    for (let i = 0; i < acceptedTriggers.length; i++) {
      const trig = acceptedTriggers[i];

      // Determinar duración de mantenimiento
      const requestedHold = trig.holdDurationSeconds ?? 1.50;
      const holdDuration = Math.max(
        PUNCH_IN_DEFAULTS.HOLD_MIN_DURATION_SECONDS,
        Math.min(PUNCH_IN_DEFAULTS.HOLD_MAX_DURATION_SECONDS, requestedHold)
      );

      // Escala: micro-punch para eventos ultracortos (< 0.5s), standard para el resto
      const targetScale = holdDuration < 0.50 ? microScale : standardScale;

      // Calcular punto focal centrado en ojos o rostro
      let targetFocal = trig.focalPointNormalized;
      if (!targetFocal && activeFace && activeFace.samples.length > 0) {
        targetFocal = this.extractFaceFocalPoint(activeFace, trig.timeSeconds);
      }

      if (targetFocal) {
        // Suavizado exponencial EMA: smoothed = (1 - alpha) * smoothed + alpha * target
        smoothedFocalPoint = {
          x: Number(((1 - alpha) * smoothedFocalPoint.x + alpha * targetFocal.x).toFixed(4)),
          y: Number(((1 - alpha) * smoothedFocalPoint.y + alpha * targetFocal.y).toFixed(4)),
        };
      }

      // Clamping seguro a [0, 1]
      smoothedFocalPoint.x = Math.max(0.0, Math.min(1.0, smoothedFocalPoint.x));
      smoothedFocalPoint.y = Math.max(0.0, Math.min(1.0, smoothedFocalPoint.y));

      decisions.push({
        id: `punch_${i + 1}`,
        timelineStartSeconds: Number(trig.timeSeconds.toFixed(4)),
        timelineEndSeconds: Number((trig.timeSeconds + holdDuration).toFixed(4)),
        holdDurationSeconds: Number(holdDuration.toFixed(4)),
        targetScale: Number(targetScale.toFixed(3)),
        originScale: 1.00,
        focalPointNormalized: {
          x: smoothedFocalPoint.x,
          y: smoothedFocalPoint.y,
        },
        trigger: trig.trigger,
        isSuppressedByBRoll: trig.coveredByBRoll === true, // B-Roll tiene precedencia absoluta
      });
    }

    return decisions;
  }

  /**
   * Extrae el punto focal de la cara u ojos más cercano al timestamp del evento.
   */
  private static extractFaceFocalPoint(
    faceTrack: FaceTrack,
    timeSeconds: number
  ): { x: number; y: number } {
    let closestSample = faceTrack.samples[0];
    let minDelta = Math.abs(closestSample.timeSeconds - timeSeconds);

    for (let i = 1; i < faceTrack.samples.length; i++) {
      const sample = faceTrack.samples[i];
      const delta = Math.abs(sample.timeSeconds - timeSeconds);
      if (delta < minDelta) {
        minDelta = delta;
        closestSample = sample;
      }
    }

    // Prioridad 1: Centro interocular
    if (closestSample.eyes) {
      return {
        x: closestSample.eyes.normalizedX,
        y: closestSample.eyes.normalizedY,
      };
    }

    // Prioridad 2: Centro del bounding box de la cara
    const bbox = closestSample.boundingBox;
    return {
      x: bbox.x + bbox.width / 2,
      y: bbox.y + bbox.height / 2,
    };
  }

  private static sanitizeScale(scale: number): number {
    if (isNaN(scale) || !isFinite(scale) || scale < 1.0) {
      return PUNCH_IN_DEFAULTS.STANDARD_PUNCH_SCALE;
    }
    return Math.min(scale, PUNCH_IN_DEFAULTS.MAX_SCALE_CEILING);
  }
}
