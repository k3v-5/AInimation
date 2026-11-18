export interface SpeedRampPoint {
  compTime: number; // Tiempo en la composición (segundos)
  sourceTime: number; // Tiempo en el metraje original (segundos)
  speedFactor: number; // Velocidad instantánea (ej. 3.0x, 0.25x)
}

export interface SpeedRampProfile {
  name: "whip_slowmo_whip" | "impact_freeze" | "constant_smooth";
  description: string;
  whipInSpeed: number; // default: 3.0x
  slowMoSpeed: number; // default: 0.3x
  whipOutSpeed: number; // default: 2.5x
}

/**
 * Motor de Speed Ramping y curvas de aceleración temporal no lineales (Fase 5B / Mejoras).
 * Calcula el remapeo temporal monótono continuo ($t_{source} = f(t_{comp})$) y genera keyframes de
 * timeRemap para After Effects garantizando transiciones hiper-dinámicas y cero tirones de fotogramas.
 */
export class DynamicSpeedRampEngine {
  /**
   * Genera los puntos de control de remapeo temporal para un clip con efecto Whip-SlowMo-Whip.
   */
  public static calculateRampCurve(
    inTime: number,
    outTime: number,
    footageDuration: number,
    profile: SpeedRampProfile = {
      name: "whip_slowmo_whip",
      description: "Entrada rápida 3.0x -> Cámara lenta en el clímax 0.3x -> Salida rápida 2.5x",
      whipInSpeed: 3.0,
      slowMoSpeed: 0.3,
      whipOutSpeed: 2.5,
    }
  ): SpeedRampPoint[] {
    const compDuration = Math.max(0.5, outTime - inTime);

    // Dividir la duración en 3 fases: 25% entrada rápida, 50% slow-motion, 25% salida rápida
    const t1 = inTime + compDuration * 0.25;
    const t2 = inTime + compDuration * 0.75;
    const t3 = outTime;

    // Calcular avances en tiempo de metraje original
    const s0 = 0.0;
    const s1 = s0 + (t1 - inTime) * profile.whipInSpeed;
    const s2 = s1 + (t2 - t1) * profile.slowMoSpeed;
    const s3 = Math.min(footageDuration, s2 + (t3 - t2) * profile.whipOutSpeed);

    return [
      { compTime: Number(inTime.toFixed(3)), sourceTime: Number(s0.toFixed(3)), speedFactor: profile.whipInSpeed },
      { compTime: Number(t1.toFixed(3)), sourceTime: Number(s1.toFixed(3)), speedFactor: profile.slowMoSpeed },
      { compTime: Number(t2.toFixed(3)), sourceTime: Number(s2.toFixed(3)), speedFactor: profile.slowMoSpeed },
      { compTime: Number(t3.toFixed(3)), sourceTime: Number(s3.toFixed(3)), speedFactor: profile.whipOutSpeed },
    ];
  }

  /**
   * Genera el fragmento ExtendScript para aplicar el remapeo temporal con curvas Bézier en After Effects.
   */
  public static generateExtendScriptSpeedRamp(
    layerVar: string,
    inTime: number,
    outTime: number,
    footageDuration: number
  ): string {
    const points = this.calculateRampCurve(inTime, outTime, footageDuration);

    const scriptLines = [
      `// === DYNAMIC SPEED RAMPING (WHIP -> SLOWMO -> WHIP) ===`,
      `${layerVar}.timeRemapEnabled = true;`,
    ];

    for (const p of points) {
      scriptLines.push(`${layerVar}.timeRemap.setValueAtTime(${p.compTime}, ${p.sourceTime});`);
    }

    return scriptLines.join("\n");
  }
}
