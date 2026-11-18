import { Vector2 } from "../../core/types.js";
import { CameraDynamicsConfig } from "../types/index.js";

/**
 * Motor de dinámicas de cámara 2D y sacudida orgánica determinista con semilla (Fase 11).
 */
export class CameraDynamicsEngine {
  /**
   * Generador determinista de números pseudoaleatorios (PRNG) basado en LCG con semilla.
   */
  public static seededRandom(seed: number, index: number): number {
    const x = Math.sin(seed * 997 + index * 1013) * 10000;
    return x - Math.floor(x);
  }

  /**
   * Evalúa la transformación de cámara en un tiempo t.
   */
  public static evaluateCamera(
    config: CameraDynamicsConfig,
    t: number
  ): { position: Vector2; scale: number; rotation: number } {
    const normalizedTime = Math.max(0, Math.min(1.0, config.duration > 0 ? t / config.duration : 0));
    const seed = config.seed ?? 42;

    switch (config.mode) {
      case "snapZoom": {
        // Zoom rápido al principio con caída amortiguada
        const bounce = Math.sin(normalizedTime * Math.PI * 2) * Math.exp(-normalizedTime * 4);
        const scale = 1.0 + 0.15 * config.intensity * (1 + bounce);
        return { position: { x: 0, y: 0 }, scale, rotation: 0 };
      }
      case "subtlePush": {
        // Empuje suave progresivo
        const scale = 1.0 + 0.08 * config.intensity * normalizedTime;
        return { position: { x: 0, y: 0 }, scale, rotation: 0 };
      }
      case "dramaticPush": {
        // Zoom rápido hacia adentro
        const scale = 1.0 + 0.25 * config.intensity * Math.pow(normalizedTime, 2);
        return { position: { x: 0, y: 0 }, scale, rotation: 0 };
      }
      case "shake": {
        // Sacudida con PRNG determinista
        const frameIdx = Math.floor(t * 30);
        const randX = this.seededRandom(seed, frameIdx) * 2 - 1;
        const randY = this.seededRandom(seed + 1, frameIdx) * 2 - 1;
        const randRot = (this.seededRandom(seed + 2, frameIdx) * 2 - 1) * 0.5;

        const maxOffset = 15 * config.intensity;
        return {
          position: { x: randX * maxOffset, y: randY * maxOffset },
          scale: 1.05, // Ligero overscale para evitar bordes negros
          rotation: randRot * config.intensity,
        };
      }
      case "static":
      default:
        return { position: { x: 0, y: 0 }, scale: 1.0, rotation: 0 };
    }
  }
}
