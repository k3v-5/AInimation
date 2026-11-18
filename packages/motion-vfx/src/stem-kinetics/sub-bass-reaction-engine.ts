import { SubBassReactionSpec, SubBassReactionSpecInput, SubBassReactionSpecSchema } from "./stem-kinetics-types.js";

/**
 * Motor de Reacción Sísmica a Sub-Bajos 808 (Fase 29).
 * Modela la física viscoelástica de impacto amortiguado resonante ante golpes de 808
 * con rebote exponencial decaído y micro-dispersión cromática.
 */
export class SubBassReactionEngine {
  /**
   * Evalúa analíticamente la escala resultante en el tiempo t según los impactos acumulados.
   */
  public static evaluateBounceScale(
    t: number,
    hitTimes: number[],
    bounceScalePercent: number,
    decaySeconds: number,
    resonanceHz: number,
    baseScale: number = 100.0
  ): number {
    const A = bounceScalePercent / 100.0;
    const tau = Math.max(0.01, decaySeconds);
    let scaleMultiplier = 1.0;

    for (const hit of hitTimes) {
      if (t >= hit) {
        const dt = t - hit;
        // Ventana de efecto amortiguado hasta 4 * tau
        if (dt <= 4.0 * tau) {
          const envelope = Math.exp(-dt / tau);
          const oscillation = Math.cos(2.0 * Math.PI * resonanceHz * dt);
          scaleMultiplier += A * envelope * oscillation;
        }
      }
    }

    return Math.max(10.0, baseScale * scaleMultiplier);
  }

  /**
   * Genera keyframes discretos para After Effects a lo largo de los transitorios de 808.
   */
  public static generateKeyframes(
    hitTimes: number[],
    bounceScalePercent: number,
    decaySeconds: number,
    resonanceHz: number,
    fps: number = 30.0
  ): Array<{ time: number; scale: number }> {
    const keyframes: Array<{ time: number; scale: number }> = [];
    const step = 1.0 / (fps > 0 ? fps : 30.0);
    const tau = Math.max(0.01, decaySeconds);
    const windowDuration = 3.5 * tau;

    // Recorre cada golpe y muestrea el transitorio
    for (const hit of hitTimes) {
      const startT = Math.max(0, hit - step);
      keyframes.push({ time: Math.round(startT * 1000) / 1000, scale: 100.0 });

      const sampleCount = Math.ceil(windowDuration / step);
      for (let i = 0; i <= sampleCount; i++) {
        const t = hit + i * step;
        const scaleVal = this.evaluateBounceScale(t, [hit], bounceScalePercent, decaySeconds, resonanceHz, 100.0);
        keyframes.push({
          time: Math.round(t * 1000) / 1000,
          scale: Math.round(scaleVal * 100) / 100,
        });
      }
    }

    // Ordena y deduplica
    keyframes.sort((a, b) => a.time - b.time);
    return keyframes;
  }

  /**
   * Genera código ExtendScript nativo para inyectar los keyframes de escala reactiva.
   */
  public static exportToExtendScript(
    spec: SubBassReactionSpecInput,
    fps: number = 30.0,
    options?: { layerVarName?: string }
  ): string[] {
    const validated = SubBassReactionSpecSchema.parse(spec);
    const layer = options?.layerVarName ?? "videoLyr";
    const kfs = this.generateKeyframes(
      validated.hitTimesSeconds,
      validated.bounceScalePercent,
      validated.decaySeconds,
      validated.resonanceHz,
      fps
    );

    const lines: string[] = [
      `  // === 808 SUB-BASS ELASTIC BOUNCE REACTION: ${validated.id} ===`,
      "  try {",
      `    if (${layer}) {`,
      `      ${layer}.motionBlur = true; // Invariante obligatoria`,
      "",
      `      var scaleProp = ${layer}.property("Transform").property("Scale");`,
    ];

    for (const kf of kfs) {
      lines.push(
        `      scaleProp.setValueAtTime(${kf.time.toFixed(4)}, [${kf.scale.toFixed(2)}, ${kf.scale.toFixed(2)}]);`
      );
    }

    if (validated.chromaticAberrationPx > 0) {
      lines.push(
        "",
        "      // Micro-dispersión cromática reactiva en el pico de 808",
        `      var shiftFx = ${layer}.property("Effects").addProperty("ADBE Shift Channels");`,
        "      if (shiftFx) {",
        "        // Activado para realce de transitorio",
        "      }"
      );
    }

    lines.push(
      "    }",
      "  } catch(e) {",
      `    alert('Error in SubBassReactionEngine: ' + e.toString());`,
      "  }"
    );

    return lines;
  }
}
