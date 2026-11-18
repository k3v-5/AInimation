import crypto from "node:crypto";
import { SoundBankManager } from "../../audio-design/SoundBankManager.js";
import {
  PolaroidFreezeFrame,
  PolaroidFreezeFrameSchema,
} from "../contracts/travel-overlays.types.js";

export interface PolaroidCreationParams {
  id: string;
  freezeTimestampSeconds: number;
  holdDurationSeconds?: number; // default 2.0s
  captionText?: string;
  handwrittenFont?: string;
  pinTackColor?: string;
  fps?: number; // default 30
}

/**
 * Generador Determinista de Congelamiento Polaroid (Milestone 6-C).
 * Deriva inclinaciones [-15°, 15°] usando hashing SHA-256 (sin aleatoriedad),
 * sincroniza el SFX del obturador con precisión de 1 frame y reutiliza SoundBankManager.
 */
export class PolaroidGenerator {
  /**
   * Genera una definición completa y determinista de PolaroidFreezeFrame.
   */
  public static createPolaroid(params: PolaroidCreationParams): {
    polaroid: PolaroidFreezeFrame;
    shutterAudioBuffer: Buffer;
  } {
    const fps = params.fps ?? 30;
    const frameDuration = 1 / fps; // 0.0333s para 30fps

    // 1. Inclinación determinista basada en hash de ID y timestamp
    const seed = `${params.id}_${params.freezeTimestampSeconds.toFixed(3)}`;
    const hash = crypto.createHash("sha256").update(seed).digest();
    const rawVal = hash.readUInt16BE(0); // [0, 65535]
    // Mapear a rango [-15.0, 15.0] grados
    const rotationDegrees = Number((-15.0 + (rawVal / 65535) * 30.0).toFixed(2));

    // 2. Sincronización exacta del SFX de obturador (±1 frame del freeze timestamp)
    const shutterSfxSyncSeconds = Number(params.freezeTimestampSeconds.toFixed(4));

    const polaroid: PolaroidFreezeFrame = {
      id: params.id,
      freezeTimestampSeconds: params.freezeTimestampSeconds,
      holdDurationSeconds: params.holdDurationSeconds ?? 2.0,
      rotationDegrees,
      captionText: params.captionText,
      handwrittenFont: params.handwrittenFont ?? "Caveat",
      pinTackColor: params.pinTackColor ?? "#FF1424", // Rojo carmesí TIME
      dropShadow: {
        opacity: 0.45,
        distancePx: 16,
        softnessPx: 24,
      },
      shutterSfxSyncSeconds,
    };

    // Validar esquema Zod
    PolaroidFreezeFrameSchema.parse(polaroid);

    // 3. Reutilizar SoundBankManager existente para sintetizar el shutter
    const shutterAudioBuffer = SoundBankManager.synthesizeCameraShutter(0.18);

    return {
      polaroid,
      shutterAudioBuffer,
    };
  }
}
