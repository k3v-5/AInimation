import { AudioTrackType } from "../types/index.js";

/**
 * Mezclador de buses de audio multicanal con limitador de picos y prevención de saturación (*clipping*) (Fase 13).
 */
export class AudioMixBus {
  private busGains = new Map<AudioTrackType, number>([
    ["voice", 1.0],
    ["music", 0.7],
    ["sfx", 0.8],
    ["ambience", 0.3],
  ]);

  public setBusGain(bus: AudioTrackType, gain: number): void {
    this.busGains.set(bus, Math.max(0, gain));
  }

  public getBusGain(bus: AudioTrackType): number {
    return this.busGains.get(bus) ?? 1.0;
  }

  /**
   * Suma de niveles de buses aplicando limitador de picos (*Peak Limiter*).
   */
  public mixAndLimit(
    levels: { bus: AudioTrackType; rawLevel: number }[],
    masterGain = 1.0,
    peakCeiling = 1.0
  ): { masterLevel: number; hasClipped: boolean } {
    let sum = 0;
    for (const item of levels) {
      const busGain = this.getBusGain(item.bus);
      sum += item.rawLevel * busGain;
    }

    const rawMaster = sum * masterGain;
    const hasClipped = rawMaster > peakCeiling;
    const masterLevel = Math.min(peakCeiling, Math.max(0, rawMaster));

    return { masterLevel, hasClipped };
  }
}
