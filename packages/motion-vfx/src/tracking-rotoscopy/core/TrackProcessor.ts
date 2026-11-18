import { Vector2 } from "../../core/types.js";
import { Track, TrackSample } from "../types/index.js";

/**
 * Procesador y evaluador de trayectorias de seguimiento con interpolación y suavizado (Fase 12).
 */
export class TrackProcessor {
  /**
   * Evalúa la posición de una pista de tracking en un tiempo t determinista.
   */
  public static evaluatePosition(track: Track, t: number): Vector2 | undefined {
    if (track.samples.length === 0) return undefined;
    if (track.samples.length === 1) return track.samples[0].position;

    // Encontrar muestras adyacentes
    let prev = track.samples[0];
    let next = track.samples[track.samples.length - 1];

    if (t <= prev.time) return prev.position;
    if (t >= next.time) return next.position;

    for (let i = 0; i < track.samples.length - 1; i++) {
      if (t >= track.samples[i].time && t <= track.samples[i + 1].time) {
        prev = track.samples[i];
        next = track.samples[i + 1];
        break;
      }
    }

    if (!prev.position || !next.position) return prev.position ?? next.position;

    const span = next.time - prev.time;
    const progress = span > 0 ? (t - prev.time) / span : 0;

    return {
      x: prev.position.x + (next.position.x - prev.position.x) * progress,
      y: prev.position.y + (next.position.y - prev.position.y) * progress,
    };
  }

  /**
   * Aplica un filtro de suavizado adaptativo sobre las muestras para reducir temblores (*jitter*).
   */
  public static smoothSamples(samples: TrackSample[], alpha = 0.5): TrackSample[] {
    if (samples.length <= 1) return samples;

    const smoothed: TrackSample[] = [samples[0]];

    for (let i = 1; i < samples.length; i++) {
      const curr = samples[i];
      const prevSmoothed = smoothed[i - 1];

      let newPos: Vector2 | undefined = curr.position;
      if (curr.position && prevSmoothed.position) {
        newPos = {
          x: alpha * curr.position.x + (1 - alpha) * prevSmoothed.position.x,
          y: alpha * curr.position.y + (1 - alpha) * prevSmoothed.position.y,
        };
      }

      smoothed.push({
        ...curr,
        position: newPos,
      });
    }

    return smoothed;
  }
}
