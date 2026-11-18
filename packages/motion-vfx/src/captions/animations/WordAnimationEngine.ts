import { ColorRGBA, Time, WordAnimationConfig } from "../types/index.js";

/**
 * Motor determinista de evaluación temporal continua para animaciones por palabra (Fase 16).
 */
export class WordAnimationEngine {
  /**
   * Evalúa la escala de una palabra aplicando PopScale con overshoot amortiguado.
   */
  public static evaluatePopScale(
    t: Time,
    start: Time,
    end: Time,
    config: WordAnimationConfig = { type: "popScale" }
  ): number {
    if (t < start || t > end) {
      return 1.0;
    }

    const duration = end - start;
    if (duration <= 0) {
      return 1.0;
    }

    const intensity = config.intensity !== undefined ? Math.max(0, Math.min(1, config.intensity)) : 1.0;
    if (intensity === 0) {
      return 1.0;
    }

    const tau = Math.max(0, Math.min(1, (t - start) / duration));
    const maxAmplitude = 0.25 * intensity; // hasta 1.25x en máxima intensidad

    // Curva de overshoot analítica: sin(pi * tau) * exp(-3 * tau)
    const scale = 1.0 + maxAmplitude * Math.sin(Math.PI * tau) * Math.exp(-3 * tau) * 2.5;

    return Number(Math.max(1.0, scale).toFixed(4));
  }

  /**
   * Evalúa la intensidad y radio de resplandor para GlowPulse.
   */
  public static evaluateGlowPulse(
    t: Time,
    start: Time,
    end: Time,
    config: WordAnimationConfig = { type: "glowPulse" },
    baseGlowColor: ColorRGBA = { r: 1, g: 0.9, b: 0, a: 1 }
  ): { active: boolean; intensity: number; radius: number; color: ColorRGBA } {
    if (t < start || t > end) {
      return { active: false, intensity: 0, radius: 0, color: baseGlowColor };
    }

    const duration = end - start;
    if (duration <= 0) {
      return { active: false, intensity: 0, radius: 0, color: baseGlowColor };
    }

    const intensityFactor = config.intensity !== undefined ? Math.max(0, Math.min(1, config.intensity)) : 1.0;
    if (intensityFactor === 0) {
      return { active: false, intensity: 0, radius: 0, color: baseGlowColor };
    }

    const tau = Math.max(0, Math.min(1, (t - start) / duration));
    const pulse = Math.sin(Math.PI * tau);
    const glowIntensity = Number((pulse * intensityFactor).toFixed(4));
    const glowRadius = Number((8 + 16 * pulse * intensityFactor).toFixed(2));
    const color = config.color ?? baseGlowColor;

    return {
      active: glowIntensity > 0.01,
      intensity: glowIntensity,
      radius: glowRadius,
      color,
    };
  }

  /**
   * Evalúa la interpolación de color para ColorHighlight.
   */
  public static evaluateColorHighlight(
    t: Time,
    start: Time,
    end: Time,
    inactiveColor: ColorRGBA = { r: 0.7, g: 0.7, b: 0.7, a: 1 },
    highlightColor: ColorRGBA = { r: 1, g: 0.9, b: 0, a: 1 },
    completedColor: ColorRGBA = { r: 1, g: 1, b: 1, a: 1 }
  ): ColorRGBA {
    if (t < start) {
      return { ...inactiveColor };
    }
    if (t > end) {
      return { ...completedColor };
    }

    const duration = end - start;
    if (duration <= 0) {
      return { ...highlightColor };
    }

    const tau = Math.max(0, Math.min(1, (t - start) / duration));
    // Interpolación hacia el color destacado
    return this.lerpColor(inactiveColor, highlightColor, Math.sin((Math.PI * tau) / 2));
  }

  /**
   * Evalúa el desplazamiento cartesiano (Shake) mediante PRNG determinista LCG con semilla fija.
   */
  public static evaluateShake(
    t: Time,
    start: Time,
    end: Time,
    config: WordAnimationConfig = { type: "shake" }
  ): { x: number; y: number } {
    if (t < start || t > end) {
      return { x: 0, y: 0 };
    }

    const duration = end - start;
    if (duration <= 0) {
      return { x: 0, y: 0 };
    }

    const intensity = config.intensity !== undefined ? Math.max(0, Math.min(1, config.intensity)) : 1.0;
    if (intensity === 0) {
      return { x: 0, y: 0 };
    }

    const seed = config.seed ?? 42;
    const maxOffset = 6.0 * intensity; // hasta 6px de vibración

    // Cuantizar a intervalos de 33ms (30fps) para simulación de shake orgánico
    const frameIndex = Math.floor((t - start) * 30);
    const rndX = this.lcg(seed + frameIndex);
    const rndY = this.lcg(seed + 1000 + frameIndex);

    const x = Number(((rndX * 2 - 1) * maxOffset).toFixed(2));
    const y = Number(((rndY * 2 - 1) * maxOffset).toFixed(2));

    return { x, y };
  }

  private static lerpColor(a: ColorRGBA, b: ColorRGBA, t: number): ColorRGBA {
    const clampedT = Math.max(0, Math.min(1, t));
    return {
      r: Number((a.r + (b.r - a.r) * clampedT).toFixed(4)),
      g: Number((a.g + (b.g - a.g) * clampedT).toFixed(4)),
      b: Number((a.b + (b.b - a.b) * clampedT).toFixed(4)),
      a: Number(((a.a ?? 1) + ((b.a ?? 1) - (a.a ?? 1)) * clampedT).toFixed(4)),
    };
  }

  private static lcg(seed: number): number {
    const a = 1664525;
    const c = 1013904223;
    const m = 4294967296;
    const next = (a * (seed >>> 0) + c) % m;
    return next / m;
  }
}
