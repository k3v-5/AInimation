import { Time } from "../../core/types.js";
import { MediaShot, ShotAnalysis } from "../types/index.js";

/**
 * Segmentador de tomas visuales (Shots) y extractor de keyframes canónicos (Fase 6).
 */
export class ShotDetector {
  /**
   * Genera los 5 timestamps de keyframes canónicos (0%, 25%, 50%, 75%, 100%) para una toma.
   */
  public static calculateKeyframes(start: Time, end: Time): Time[] {
    const duration = end - start;
    if (duration <= 0) return [start];

    return [
      start,
      start + duration * 0.25,
      start + duration * 0.5,
      start + duration * 0.75,
      end,
    ];
  }

  /**
   * Segmenta una duración de video en base a puntos de corte detectados.
   */
  public static createShotsFromCuts(
    assetId: string,
    cutPoints: Time[],
    totalDuration: Time,
    analysisList?: ShotAnalysis[]
  ): MediaShot[] {
    const sortedCuts = Array.from(new Set([0.0, ...cutPoints, totalDuration])).sort(
      (a, b) => a - b
    );

    const shots: MediaShot[] = [];

    for (let i = 0; i < sortedCuts.length - 1; i++) {
      const start = sortedCuts[i];
      const end = sortedCuts[i + 1];

      if (end - start > 0.05) {
        // Ignorar segmentos menores a 50ms
        shots.push({
          id: `${assetId}_shot_${i}`,
          start,
          end,
          keyframes: this.calculateKeyframes(start, end),
          analysis: analysisList?.[i],
        });
      }
    }

    return shots;
  }
}
