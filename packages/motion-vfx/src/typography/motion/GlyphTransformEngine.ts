import { GlyphPosition, GlyphTransform, StaggerMode } from "../types/index.js";

/**
 * Motor de animación y transformación cinética independiente por glifo (Fase 5F).
 */
export class GlyphTransformEngine {
  /**
   * Generador determinista de números pseudo-aleatorios con semilla (Linear Congruential Generator).
   */
  private static lcgRandom(seed: number): () => number {
    let state = seed % 2147483647;
    if (state <= 0) state += 2147483646;
    return () => {
      state = (state * 16807) % 2147483647;
      return (state - 1) / 2147483646;
    };
  }

  /**
   * Calcula todos los retardos de stagger en O(N) para un conjunto de glifos.
   */
  public static calculateStaggerDelays(
    total: number,
    mode: StaggerMode = "forward",
    stepSec = 0.05,
    seed = 42
  ): number[] {
    if (total <= 0) return [];
    if (total === 1) return [0];

    const delays = new Array<number>(total);

    switch (mode) {
      case "forward":
        for (let i = 0; i < total; i++) delays[i] = i * stepSec;
        break;
      case "reverse":
        for (let i = 0; i < total; i++) delays[i] = (total - 1 - i) * stepSec;
        break;
      case "center": {
        const center = (total - 1) / 2;
        for (let i = 0; i < total; i++) delays[i] = Math.abs(i - center) * stepSec;
        break;
      }
      case "random": {
        const rng = this.lcgRandom(seed);
        const order = Array.from({ length: total }, (_, i) => i);
        // Fisher-Yates shuffle determinista en O(N)
        for (let i = total - 1; i > 0; i--) {
          const j = Math.floor(rng() * (i + 1));
          const tmp = order[i];
          order[i] = order[j];
          order[j] = tmp;
        }
        for (let rank = 0; rank < total; rank++) {
          delays[order[rank]] = rank * stepSec;
        }
        break;
      }
    }

    return delays;
  }

  /**
   * Calcula el retardo de stagger para un único glifo.
   */
  public static calculateStaggerDelay(
    index: number,
    total: number,
    mode: StaggerMode = "forward",
    stepSec = 0.05,
    seed = 42
  ): number {
    const delays = this.calculateStaggerDelays(total, mode, stepSec, seed);
    return delays[index] ?? 0;
  }

  /**
   * Genera el mapa de transformaciones espaciales para cada glifo en un instante de tiempo en O(N).
   */
  public static evaluateGlyphMotion(
    glyphs: GlyphPosition[],
    localTime: number,
    animationDuration = 0.4,
    mode: StaggerMode = "forward",
    stepSec = 0.05,
    seed = 42
  ): GlyphTransform[] {
    const total = glyphs.length;
    const delays = this.calculateStaggerDelays(total, mode, stepSec, seed);
    const transforms: GlyphTransform[] = new Array(total);

    for (let i = 0; i < total; i++) {
      const delay = delays[i];
      const glyphTime = localTime - delay;

      let progress = 0;
      if (glyphTime > 0) {
        progress = Math.min(1.0, glyphTime / animationDuration);
      }

      // Animación cinética por defecto: scale 0 -> 1 y sube 20px
      const scaleVal = progress;
      const offsetY = (1 - progress) * 20;

      transforms[i] = {
        position: { x: 0, y: offsetY },
        scale: { x: scaleVal, y: scaleVal },
        rotation: (1 - progress) * -15, // Ligero giro de entrada
        opacity: progress,
      };
    }

    return transforms;
  }
}
