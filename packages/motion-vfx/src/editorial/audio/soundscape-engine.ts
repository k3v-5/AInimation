import { AudioBusType, SoundscapeLayer } from "./audio-ir.types.js";

/**
 * REQ-067: Dynamic Soundscape Engine
 * Estratifica las fuentes sonoras en 3 planos perceptuales evitando la saturación de frecuencias.
 */
export class SoundscapeEngine {
  public static readonly LAYER_MAP: Record<AudioBusType, SoundscapeLayer> = {
    MASTER: "FOREGROUND",
    VOICE: "FOREGROUND",
    DIALOGUE: "FOREGROUND",
    CRITICAL_SFX: "FOREGROUND",
    SFX: "MIDGROUND",
    ARCHIVE_AUDIO: "MIDGROUND",
    MUSIC: "BACKGROUND",
    AMBIENCE: "BACKGROUND",
    ROOM_TONE: "BACKGROUND",
  };

  /**
   * Resuelve el plano perceptual para un bus o clip dado
   */
  public static getLayerForBus(busId: AudioBusType): SoundscapeLayer {
    return this.LAYER_MAP[busId] ?? "MIDGROUND";
  }

  /**
   * Valida que no exista enmascaramiento destructivo entre planos
   */
  public static checkMasking(params: {
    foregroundEnergyRms: number;
    backgroundEnergyRms: number;
  }): { isMasked: boolean; recommendedBackgroundAttenuationDb: number } {
    const diffDb = 20 * Math.log10(Math.max(1e-5, params.foregroundEnergyRms)) -
                   20 * Math.log10(Math.max(1e-5, params.backgroundEnergyRms));

    // Si el fondo está a menos de 10 dB por debajo del diálogo en el mismo intervalo, hay riesgo de enmascaramiento
    if (diffDb < 10.0) {
      return {
        isMasked: true,
        recommendedBackgroundAttenuationDb: Number((12.0 - diffDb).toFixed(1)),
      };
    }

    return {
      isMasked: false,
      recommendedBackgroundAttenuationDb: 0.0,
    };
  }
}
