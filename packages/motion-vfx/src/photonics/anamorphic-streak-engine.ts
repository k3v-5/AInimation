import {
  AnamorphicStreakSpec,
  AnamorphicStreakSpecInput,
  AnamorphicStreakSpecSchema,
} from "./photonics-types.js";

/**
 * Motor de Destellos Anamórficos Horizontales (Anamorphic Streak Flares) (Fase 27).
 * Emula la aberración anamórfica de lentes cilíndricas (Lomo, Panavision, Cooke Anamorphic)
 * aislando altas luces y dispersándolas en un haz horizontal cian o dorado.
 */
export class AnamorphicStreakEngine {
  /**
   * Calcula la luminancia perceptual Rec. 601 / Rec. 709 para un color RGB normalizado [0, 1].
   */
  public static computePerceptualLuminance(r: number, g: number, b: number): number {
    const cr = Math.max(0, Math.min(1, r));
    const cg = Math.max(0, Math.min(1, g));
    const cb = Math.max(0, Math.min(1, b));
    return 0.299 * cr + 0.587 * cg + 0.114 * cb;
  }

  /**
   * Determina si un valor RGB supera el umbral de altas luces especulares.
   */
  public static isHighlight(r: number, g: number, b: number, thresholdPercent: number): boolean {
    const lum = this.computePerceptualLuminance(r, g, b);
    const thresholdNorm = Math.max(0, Math.min(1, thresholdPercent / 100));
    return lum >= thresholdNorm;
  }

  /**
   * Genera código ExtendScript nativo para inyectar una capa de ajuste anamórfica
   * con extracción de altas luces, ADBE Directional Blur a 90° y ADBE Tint cromático.
   */
  public static exportToExtendScript(
    spec: AnamorphicStreakSpecInput,
    options?: { compVarName?: string; layerVarName?: string }
  ): string[] {
    const validated = AnamorphicStreakSpecSchema.parse(spec);
    const comp = options?.compVarName ?? "comp";
    const layer = options?.layerVarName ?? "videoLyr";
    const [tintR, tintG, tintB] = validated.tintColor;

    const blackIn = Math.round((validated.thresholdPercent / 100) * 255);

    const lines: string[] = [
      `  // === ANAMORPHIC STREAK FLARE: ${validated.id} ===`,
      "  try {",
      `    if (${comp}) {`,
      `      var streakAdj = ${comp}.layers.addSolid([0, 0, 0], '[ANAMORPHIC STREAK] ' + '${validated.id}', ${comp}.width, ${comp}.height, 1.0);`,
      "      if (streakAdj) {",
      "        streakAdj.adjustmentLayer = true;",
      "        streakAdj.blendingMode = BlendingMode.ADD;",
      "        streakAdj.motionBlur = true;",
      "",
      "        // 1. Extracción de altas luces especulares mediante Niveles",
      '        var levelsFx = streakAdj.property("Effects").addProperty("ADBE Levels2");',
      "        if (levelsFx) {",
      `          levelsFx.property("Input Black").setValue(${blackIn});`,
      '          levelsFx.property("Input White").setValue(255);',
      "        }",
      "",
      "        // 2. Dispersión horizontal cilíndrica anamórfica (ADBE Directional Blur a 90°)",
      '        var dirBlurFx = streakAdj.property("Effects").addProperty("ADBE Directional Blur");',
      "        if (dirBlurFx) {",
      `          dirBlurFx.property("Direction").setValue(${validated.directionDegrees.toFixed(1)});`,
      `          dirBlurFx.property("Blur Length").setValue(${validated.streakLength.toFixed(1)});`,
      "        }",
      "",
      "        // 3. Tinte cromático anamórfico",
      '        var tintFx = streakAdj.property("Effects").addProperty("ADBE Tint");',
      "        if (tintFx) {",
      "          tintFx.property(\"Map Black To\").setValue([0.0, 0.0, 0.0]);",
      `          tintFx.property("Map White To").setValue([${tintR.toFixed(3)}, ${tintG.toFixed(3)}, ${tintB.toFixed(3)}]);`,
      "          tintFx.property(\"Amount to Tint\").setValue(100.0);",
      "        }",
      "",
      "        // 4. Intensidad / Opacidad global de la capa de ajuste",
      `        var opVal = Math.min(100.0, ${validated.intensity.toFixed(2)} * 100.0);`,
      "        streakAdj.property(\"Transform\").property(\"Opacity\").setValue(opVal);",
    ];

    if (validated.startTimeSeconds !== undefined && validated.durationSeconds !== undefined) {
      const inT = validated.startTimeSeconds;
      const outT = validated.startTimeSeconds + validated.durationSeconds;
      lines.push(
        `        streakAdj.startTime = ${inT.toFixed(4)};`,
        `        streakAdj.inPoint = ${inT.toFixed(4)};`,
        `        streakAdj.outPoint = ${outT.toFixed(4)};`
      );
    }

    lines.push(
      "      }",
      "    }",
      "  } catch(e) {",
      `    alert('Error in AnamorphicStreakEngine: ' + e.toString());`,
      "  }"
    );

    return lines;
  }
}
