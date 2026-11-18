import { DuckingRule, SpeechRegion } from "../types/index.js";

/**
 * Motor de atenuación automática de música (*Smart Ducking*) con envolventes de ataque y decaimiento (Fase 13).
 */
export class SmartDuckingEngine {
  /**
   * Calcula el multiplicador de volumen de la música en el tiempo t ante la presencia de voz.
   */
  public static evaluateDuckingGain(
    speechRegions: SpeechRegion[],
    rule: DuckingRule,
    t: number
  ): number {
    // Si no hay voz, volumen normal
    if (speechRegions.length === 0) return rule.normalVolume;

    for (const region of speechRegions) {
      // 1. Durante la voz activa
      if (t >= region.start && t <= region.end) {
        return rule.duckedVolume;
      }

      // 2. Transición de ataque (justo antes de que empiece la voz)
      if (t >= region.start - rule.attackDuration && t < region.start) {
        const progress = (t - (region.start - rule.attackDuration)) / rule.attackDuration;
        return rule.normalVolume - (rule.normalVolume - rule.duckedVolume) * progress;
      }

      // 3. Transición de decaimiento / recuperación (justo después de que termine la voz)
      if (t > region.end && t <= region.end + rule.releaseDuration) {
        const progress = (t - region.end) / rule.releaseDuration;
        return rule.duckedVolume + (rule.normalVolume - rule.duckedVolume) * progress;
      }
    }

    return rule.normalVolume;
  }
}
