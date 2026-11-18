import crypto from "crypto";
import { AudioTransition } from "./audio-ir.types.js";

/**
 * REQ-020: Master J-Cut & L-Cut Engine
 * Transiciones de audio/video desfasadas guiadas por narrativa y límites matemáticos seguros.
 */
export class JLCutEngine {
  public static readonly MAX_SPLIT_SECONDS = 2.0;
  public static readonly DEFAULT_SPLIT_SECONDS = 0.5;

  /**
   * Genera un ID determinista para la transición de audio
   */
  public static generateTransitionId(fromClipId: string, toClipId: string, visualCutTime: number): string {
    const raw = `${fromClipId}_${toClipId}_${visualCutTime.toFixed(4)}`;
    return `jl_${crypto.createHash("sha256").update(raw, "utf8").digest("hex").slice(0, 12)}`;
  }

  /**
   * Planifica y valida matemáticamente un J-Cut o L-Cut entre dos clips contiguos
   */
  public static planSplitCut(params: {
    fromClip: { id: string; durationSeconds: number; isDialogue: boolean; hasAudioHandleTail?: number };
    toClip: { id: string; durationSeconds: number; isDialogue: boolean; hasAudioHandleHead?: number };
    visualCutTimestampSeconds: number;
    preferSplitCuts?: boolean;
    emotionalContinuityRequired?: boolean;
  }): AudioTransition {
    const { fromClip, toClip, visualCutTimestampSeconds, preferSplitCuts = true, emotionalContinuityRequired = false } = params;

    const id = this.generateTransitionId(fromClip.id, toClip.id, visualCutTimestampSeconds);

    if (!preferSplitCuts) {
      return {
        id,
        type: "HARD_CUT",
        visualCutTimestampSeconds,
        audioLeadSeconds: 0,
        audioTailSeconds: 0,
        fromClipId: fromClip.id,
        toClipId: toClip.id,
        reason: "Hard cut asignado por configuración o política editorial.",
      };
    }

    // 1. L-Cut: El diálogo del sujeto continúa sobre el inicio del siguiente plano (ej. B-Roll o plano reacción)
    if (fromClip.isDialogue && !toClip.isDialogue) {
      const maxAllowedTail = Math.min(
        this.MAX_SPLIT_SECONDS,
        toClip.durationSeconds * 0.5,
        fromClip.hasAudioHandleTail ?? this.MAX_SPLIT_SECONDS
      );
      const audioTailSeconds = Math.max(0.2, Math.min(maxAllowedTail, this.DEFAULT_SPLIT_SECONDS));

      return {
        id,
        type: "L_CUT",
        visualCutTimestampSeconds,
        audioLeadSeconds: 0,
        audioTailSeconds: Number(audioTailSeconds.toFixed(3)),
        fromClipId: fromClip.id,
        toClipId: toClip.id,
        reason: "L-Cut: Diálogo continuo sobreimpreso al corte visual para suavizar el ritmo.",
      };
    }

    // 2. J-Cut: La voz o sonido del siguiente plano entra antes de la imagen (anticipación narrativa)
    if (!fromClip.isDialogue && toClip.isDialogue) {
      const maxAllowedLead = Math.min(
        this.MAX_SPLIT_SECONDS,
        fromClip.durationSeconds * 0.5,
        toClip.hasAudioHandleHead ?? this.MAX_SPLIT_SECONDS
      );
      const audioLeadSeconds = Math.max(0.2, Math.min(maxAllowedLead, this.DEFAULT_SPLIT_SECONDS));

      return {
        id,
        type: "J_CUT",
        visualCutTimestampSeconds,
        audioLeadSeconds: Number(audioLeadSeconds.toFixed(3)),
        audioTailSeconds: 0,
        fromClipId: fromClip.id,
        toClipId: toClip.id,
        reason: "J-Cut: Anticipación acústica del orador antes del corte de vídeo.",
      };
    }

    // 3. Diálogo a Diálogo con requerimiento de continuidad emocional
    if (fromClip.isDialogue && toClip.isDialogue && emotionalContinuityRequired) {
      const audioLeadSeconds = Math.min(0.3, fromClip.durationSeconds * 0.25);
      return {
        id,
        type: "J_CUT",
        visualCutTimestampSeconds,
        audioLeadSeconds: Number(audioLeadSeconds.toFixed(3)),
        audioTailSeconds: 0,
        fromClipId: fromClip.id,
        toClipId: toClip.id,
        reason: "J-Cut sutil: Solapamiento breve entre interlocutores para fluidez emocional.",
      };
    }

    return {
      id,
      type: "HARD_CUT",
      visualCutTimestampSeconds,
      audioLeadSeconds: 0,
      audioTailSeconds: 0,
      fromClipId: fromClip.id,
      toClipId: toClip.id,
      reason: "Hard cut asignado por coincidencia de tipos de plano estándar.",
    };
  }
}
