import { TrimPaths } from "../types/index.js";

/**
 * Motor de movimiento procedural determinista para gráficos 2D (Fase 5J).
 */
export class ProceduralMotion {
  /**
   * Evalúa el recorte paramétrico de curvas (Trim Paths).
   * Devuelve el rango normalizado visible [visibleStart, visibleEnd] dentro de [0, 1].
   */
  public static evaluateTrimPaths(
    progress: number,
    trim: TrimPaths
  ): { visibleStart: number; visibleEnd: number } {
    const s = Math.max(0, Math.min(1, trim.start));
    const e = Math.max(0, Math.min(1, trim.end));
    const off = trim.offset % 1.0;

    const currentSpan = (e - s) * Math.max(0, Math.min(1, progress));
    const startPos = (s + off) % 1.0;
    const endPos = (startPos + currentSpan) % 1.0;

    return {
      visibleStart: startPos,
      visibleEnd: endPos,
    };
  }

  /**
   * Generador determinista armónico de ruido procedural basado en tiempo y semilla.
   */
  public static evaluateNoise(
    time: number,
    seed = 42,
    frequency = 2.0,
    amplitude = 1.0
  ): number {
    const n1 = Math.sin(time * frequency * 2 * Math.PI + seed);
    const n2 = Math.sin(time * frequency * 1.618 * Math.PI + seed * 2);
    const n3 = Math.cos(time * frequency * 0.707 * Math.PI + seed * 3);

    return (n1 * 0.5 + n2 * 0.3 + n3 * 0.2) * amplitude;
  }

  /**
   * Resorte amortiguado para efectos de rebote (Bounce-in / Pop).
   */
  public static evaluateSpringBounce(
    progress: number,
    damping = 0.7,
    frequency = 4.0
  ): number {
    const t = Math.max(0, Math.min(1, progress));
    if (t >= 1.0) return 1.0;

    // Fórmula clásica de resorte subamortiguado: 1 - e^(-d*t) * cos(w*t)
    const decay = Math.exp(-damping * 6.0 * t);
    const oscillation = Math.cos(frequency * 2.0 * Math.PI * t);

    return 1.0 - decay * oscillation;
  }
}
