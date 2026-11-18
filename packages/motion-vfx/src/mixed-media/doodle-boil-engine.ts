import { DoodleBoilSpec, DoodleBoilSpecInput, DoodleBoilSpecSchema } from "./mixed-media-types.js";

/**
 * Motor de Stop-Motion Doodle Boil (Fase 28).
 * Simula trazos y garabatos animados a mano con ebullición (*boiling*) a 8 o 12 fps
 * característicos de la animación indie y secuencias de técnica mixta.
 */
export class DoodleBoilEngine {
  /**
   * Calcula el intervalo temporal por fotograma de ebullición.
   */
  public static calculateFrameStep(boilFps: 8 | 12): number {
    return 1.0 / boilFps;
  }

  /**
   * Genera código ExtendScript nativo para aplicar ebullición de trazo (Turbulent Displace / Roughen Edges).
   */
  public static exportToExtendScript(
    spec: DoodleBoilSpecInput,
    options?: { layerVarName?: string }
  ): string[] {
    const validated = DoodleBoilSpecSchema.parse(spec);
    const layer = options?.layerVarName ?? "videoLyr";
    const [sr, sg, sb] = validated.strokeColor;

    const lines: string[] = [
      `  // === STOP-MOTION DOODLE BOIL: ${validated.id} (${validated.boilFps} FPS) ===`,
      "  try {",
      `    if (${layer}) {`,
      `      ${layer}.motionBlur = true; // Invariante obligatoria`,
      "",
      "      // 1. Desplazamiento turbulento posterizado a baja tasa de cuadros",
      `      var turbFx = ${layer}.property("Effects").addProperty("ADBE Turbulent Displace");`,
      "      if (turbFx) {",
      `        turbFx.property("Amount").setValue(${validated.jitterAmplitudePx.toFixed(1)} * 6.0);`,
      `        turbFx.property("Size").setValue(15.0);`,
      '        var evoProp = turbFx.property("Evolution");',
      `        evoProp.expression = "posterizeTime(${validated.boilFps}); Math.floor(time * ${validated.boilFps}) * 75;";`,
      "      }",
      "",
      "      // 2. Bordes rugosos estilo papel/tinta",
      `      var roughFx = ${layer}.property("Effects").addProperty("ADBE Roughen Edges");`,
      "      if (roughFx) {",
      `        roughFx.property("Border").setValue(${validated.strokeWidthPx.toFixed(1)} * 2.0);`,
      "        roughFx.property(\"Edge Sharpness\").setValue(4.0);",
      '        var roughEvo = roughFx.property("Evolution");',
      `        roughEvo.expression = "posterizeTime(${validated.boilFps}); Math.floor(time * ${validated.boilFps}) * 90;";`,
      "      }",
      "    }",
      "  } catch(e) {",
      `    alert('Error in DoodleBoilEngine: ' + e.toString());`,
      "  }",
    ];

    return lines;
  }
}
