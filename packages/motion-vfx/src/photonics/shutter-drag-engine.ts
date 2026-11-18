import { ShutterDragSpec, ShutterDragSpecInput, ShutterDragSpecSchema } from "./photonics-types.js";

/**
 * Motor de Shutter Drag y Kinetic Ghosting (Fase 27).
 * Emula obturación lenta a 360° o tiempos de exposición largos en After Effects
 * mediante el efecto nativo ADBE Echo con decaimiento exponencial estricto.
 */
export class ShutterDragEngine {
  /**
   * Mapea el operador semántico al índice numérico de After Effects (1-indexed).
   * 1 = Add, 2 = Screen, 5 = Composite in Back, 8 = Maximum
   */
  public static mapOperatorToIndex(op: "MAXIMUM" | "ADD" | "SCREEN" | "COMPOSITE_IN_BACK"): number {
    switch (op) {
      case "ADD":
        return 1;
      case "SCREEN":
        return 2;
      case "COMPOSITE_IN_BACK":
        return 5;
      case "MAXIMUM":
      default:
        return 8;
    }
  }

  /**
   * Calcula las amplitudes teóricas de cada eco temporal según la fórmula:
   * A_k = decay^k para k in [0, N-1]
   */
  public static calculateEchoAmplitudes(count: number, decay: number): number[] {
    if (count <= 0) return [];
    const clampedDecay = Math.max(0.01, Math.min(1.0, decay));
    const amplitudes: number[] = [];
    for (let k = 0; k < count; k++) {
      amplitudes.push(Math.pow(clampedDecay, k));
    }
    return amplitudes;
  }

  /**
   * Genera código ExtendScript nativo para inyectar el efecto ADBE Echo con keyframes temporales.
   */
  public static exportToExtendScript(
    spec: ShutterDragSpecInput,
    options?: { layerVarName?: string }
  ): string[] {
    const validated = ShutterDragSpecSchema.parse(spec);
    const layer = options?.layerVarName ?? "videoLyr";
    const opIndex = this.mapOperatorToIndex(validated.blendOperator);

    const startT = validated.startTimeSeconds;
    const endT = validated.startTimeSeconds + validated.durationSeconds;
    const rampTime = Math.min(0.15, validated.durationSeconds * 0.2);

    const lines: string[] = [
      `  // === SHUTTER DRAG ECHO TRAILS: ${validated.id} ===`,
      "  try {",
      `    if (${layer}) {`,
      `      ${layer}.motionBlur = true; // Invariante obligatoria`,
      "",
      `      var echoFx = ${layer}.property("Effects").addProperty("ADBE Echo");`,
      "      if (echoFx) {",
      `        echoFx.property("Echo Time (seconds)").setValue(${validated.echoTimeStepSeconds.toFixed(4)});`,
      `        echoFx.property("Decay").setValue(${validated.decay.toFixed(3)});`,
      `        echoFx.property("Starting Intensity").setValue(1.0);`,
      `        echoFx.property("Echo Operator").setValue(${opIndex});`,
      "",
      "        // Keyframing de número de ecos para activación suave",
      `        var numEchoesProp = echoFx.property("Number of Echoes");`,
      `        numEchoesProp.setValueAtTime(${(startT).toFixed(4)}, 0);`,
      `        numEchoesProp.setValueAtTime(${(startT + rampTime).toFixed(4)}, ${validated.echoCount});`,
      `        numEchoesProp.setValueAtTime(${(endT - rampTime).toFixed(4)}, ${validated.echoCount});`,
      `        numEchoesProp.setValueAtTime(${(endT).toFixed(4)}, 0);`,
      "      }",
    ];

    if (validated.chromaticDispersion) {
      lines.push(
        "      // Dispersión cromática para destellos fantasma (Canal Rojo vs Azul)",
        `      var shiftFx = ${layer}.property("Effects").addProperty("ADBE Shift Channels");`,
        "      if (shiftFx) {",
        "        // Mantiene canales vivos para acentuar dispersión de estelas",
        "      }"
      );
    }

    lines.push(
      "    }",
      "  } catch(e) {",
      `    alert('Error in ShutterDragEngine: ' + e.toString());`,
      "  }"
    );

    return lines;
  }
}
