import crypto from "crypto";
import {
  CameraAngleDefinition,
  CameraAngleDefinitionSchema,
  MultiCamSwitchDecision,
  MultiCamSwitchDecisionSchema,
  EmotionalProtectionState,
} from "./multicam.types.js";

export interface SpeechTurn {
  speakerId: string;
  startSeconds: number;
  endSeconds: number;
  isEmotionalPeak?: boolean;
  emotionalState?: EmotionalProtectionState;
  energyLevel?: number;
}

/**
 * REQ-011 & REQ-012: Master Multi-Camera Director Engine.
 * Conmutación determinista de ángulos basada en tracking de hablante,
 * respeto estricto a la Ley del Eje de 180° y regla inviolable de Protección Emocional.
 */
export class MultiCameraDirector {
  private static generateDeterministicId(prefix: string, timestamp: number, angleId: string): string {
    const raw = `${prefix}_${timestamp.toFixed(4)}_${angleId}`;
    return `${prefix}_${crypto.createHash("sha256").update(raw, "utf8").digest("hex").slice(0, 10)}`;
  }

  /**
   * REQ-011 §6.4: Valida si una transición entre dos cámaras respeta la Ley del Eje de 180°
   */
  public static validate180Axis(
    fromAngle: CameraAngleDefinition,
    toAngle: CameraAngleDefinition
  ): { isValid: boolean; reason?: string } {
    if (fromAngle.angleId === toAngle.angleId) {
      return { isValid: true };
    }

    // El plano general o neutro siempre es una transición segura para re-orientar el eje
    if (fromAngle.spatialSide === "NEUTRAL_CENTER" || toAngle.spatialSide === "NEUTRAL_CENTER") {
      return { isValid: true };
    }

    // Cruzar de izquierda a derecha directamente rompe el eje de 180°
    if (
      (fromAngle.spatialSide === "LEFT_OF_AXIS" && toAngle.spatialSide === "RIGHT_OF_AXIS") ||
      (fromAngle.spatialSide === "RIGHT_OF_AXIS" && toAngle.spatialSide === "LEFT_OF_AXIS")
    ) {
      return {
        isValid: false,
        reason: `Violación del eje de 180°: cambio directo de '${fromAngle.name}' (${fromAngle.spatialSide}) a '${toAngle.name}' (${toAngle.spatialSide}) sin plano neutro intermedio.`,
      };
    }

    return { isValid: true };
  }

  /**
   * Planifica la conmutación de cámaras para una secuencia de entrevista
   */
  public static planSwitching(params: {
    angles: CameraAngleDefinition[];
    speechTurns: SpeechTurn[];
    options?: {
      minShotDurationSeconds?: number;
      wideResetIntervalSeconds?: number;
    };
  }): MultiCamSwitchDecision[] {
    const minShotDuration = params.options?.minShotDurationSeconds ?? 2.5;
    const wideResetInterval = params.options?.wideResetIntervalSeconds ?? 45.0;

    const validatedAngles = params.angles.map((a) => CameraAngleDefinitionSchema.parse(a));
    const wideAngle = validatedAngles.find((a) => a.role === "WIDE") ?? validatedAngles[0];

    if (!wideAngle || params.speechTurns.length === 0) {
      return [];
    }

    const decisions: MultiCamSwitchDecision[] = [];
    let currentAngle = wideAngle;
    let lastCutTimestamp = 0;
    let lastWideTimestamp = 0;

    // Plano de establecimiento inicial determinista
    decisions.push(
      MultiCamSwitchDecisionSchema.parse({
        id: this.generateDeterministicId("mc_init", 0, wideAngle.angleId),
        timestampSeconds: 0,
        activeAngleId: wideAngle.angleId,
        reason: "Initial spatial establishing shot.",
        isEmotionalProtection: false,
        emotionalState: "NONE",
        confidence: 1.0,
        axisValidated: true,
      })
    );

    for (let i = 0; i < params.speechTurns.length; i++) {
      const turn = params.speechTurns[i];
      const emoState = turn.emotionalState || (turn.isEmotionalPeak ? "CONFESSION" : "NONE");
      const isProtected = emoState !== "NONE";

      // 1. REGLA INVIOLABLE DE PROTECCIÓN EMOCIONAL (REQ-011 §6.3):
      // Durante confesión, llanto, quiebre o alta vulnerabilidad, la cámara NO PUEDE ser retirada del orador.
      if (isProtected) {
        const speakerCam = validatedAngles.find((a) => a.assignedSpeakerId === turn.speakerId) ?? currentAngle;

        if (speakerCam.angleId !== currentAngle.angleId) {
          // Si no estábamos en la cámara del orador, cortamos a él inmediatamente para proteger el momento
          decisions.push(
            MultiCamSwitchDecisionSchema.parse({
              id: this.generateDeterministicId("mc_emo", turn.startSeconds, speakerCam.angleId),
              timestampSeconds: turn.startSeconds,
              activeAngleId: speakerCam.angleId,
              previousAngleId: currentAngle.angleId,
              reason: `Cut to speaker for emotional testimony peak (${emoState}).`,
              isEmotionalProtection: true,
              emotionalState: emoState,
              confidence: 0.99,
              axisValidated: true,
            })
          );
          currentAngle = speakerCam;
          lastCutTimestamp = turn.startSeconds;
        } else {
          // Si ya estamos en la cámara del orador, MANTENEMOS la toma fija
          decisions.push(
            MultiCamSwitchDecisionSchema.parse({
              id: this.generateDeterministicId("mc_hold", turn.startSeconds, currentAngle.angleId),
              timestampSeconds: turn.startSeconds,
              activeAngleId: currentAngle.angleId,
              previousAngleId: currentAngle.angleId,
              reason: `Holding camera on speaker to protect emotional testimony peak (${emoState}).`,
              isEmotionalProtection: true,
              emotionalState: emoState,
              confidence: 1.0,
              axisValidated: true,
            })
          );
        }
        continue;
      }

      // 2. Spatial Wide Reset periódico
      if (
        turn.startSeconds - lastWideTimestamp >= wideResetInterval &&
        turn.startSeconds - lastCutTimestamp >= minShotDuration
      ) {
        if (currentAngle.angleId !== wideAngle.angleId) {
          decisions.push(
            MultiCamSwitchDecisionSchema.parse({
              id: this.generateDeterministicId("mc_wide", turn.startSeconds, wideAngle.angleId),
              timestampSeconds: turn.startSeconds,
              activeAngleId: wideAngle.angleId,
              previousAngleId: currentAngle.angleId,
              reason: `Periodic spatial reset after ${(turn.startSeconds - lastWideTimestamp).toFixed(0)}s.`,
              isEmotionalProtection: false,
              emotionalState: "NONE",
              confidence: 0.92,
              axisValidated: true,
            })
          );
          currentAngle = wideAngle;
          lastCutTimestamp = turn.startSeconds;
          lastWideTimestamp = turn.startSeconds;
          continue;
        }
      }

      // 3. Speaker Tracking Cut con validación de eje de 180°
      const matchingAngle =
        validatedAngles.find((a) => a.assignedSpeakerId === turn.speakerId) ??
        validatedAngles.find((a) => a.role === "SPEAKER_PRIMARY") ??
        wideAngle;

      if (matchingAngle.angleId !== currentAngle.angleId) {
        if (turn.startSeconds - lastCutTimestamp >= minShotDuration) {
          // Validar eje de 180°
          const axisCheck = this.validate180Axis(currentAngle, matchingAngle);
          let targetAngle = matchingAngle;
          let reason = `Speaker tracking switch to angle ${matchingAngle.name}.`;

          if (!axisCheck.isValid) {
            // Eje violado: se fuerza paso por plano general neutro para restablecer el eje
            targetAngle = wideAngle;
            reason = `180° axis violation prevented. Bridging through wide angle before cutting to ${matchingAngle.name}.`;
          }

          decisions.push(
            MultiCamSwitchDecisionSchema.parse({
              id: this.generateDeterministicId("mc_spk", turn.startSeconds, targetAngle.angleId),
              timestampSeconds: turn.startSeconds,
              activeAngleId: targetAngle.angleId,
              previousAngleId: currentAngle.angleId,
              reason,
              isEmotionalProtection: false,
              emotionalState: "NONE",
              confidence: 0.95,
              axisValidated: true,
            })
          );
          currentAngle = targetAngle;
          lastCutTimestamp = turn.startSeconds;
        }
      }
    }

    return decisions;
  }
}
