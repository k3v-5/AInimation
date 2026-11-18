import { PrismStarSpec, PrismStarSpecInput, PrismStarSpecSchema } from "./photonics-types.js";

/**
 * Motor de Filtros de Estrella / Difracción de Prisma (Cross-Screen Star Filters) (Fase 27).
 * Emula los filtros de cristal óptico con micro-red de difracción (Tiffen Star 4pt / 6pt, Hoya Cross Screen).
 */
export class PrismStarEngine {
  /**
   * Calcula los ángulos simétricos de difracción según el número de puntas (4 o 6)
   * y la rotación angular base.
   */
  public static computeDiffractionAngles(points: 4 | 6, baseRotationDegrees: number = 45): number[] {
    const angles: number[] = [];
    if (points === 4) {
      // Cruz de 2 ejes ortogonales (4 puntas)
      const ang1 = (baseRotationDegrees % 180 + 180) % 180;
      const ang2 = ((baseRotationDegrees + 90) % 180 + 180) % 180;
      angles.push(ang1, ang2);
    } else {
      // Estrella de 3 ejes (6 puntas a 60° entre sí)
      for (let i = 0; i < 3; i++) {
        const ang = ((baseRotationDegrees + i * 60) % 180 + 180) % 180;
        angles.push(ang);
      }
    }
    return angles;
  }

  /**
   * Genera código ExtendScript nativo para inyectar una capa de ajuste de difracción
   * con múltiples vectores cruzados de ADBE Directional Blur en modo aditivo.
   */
  public static exportToExtendScript(
    spec: PrismStarSpecInput,
    options?: { compVarName?: string }
  ): string[] {
    const validated = PrismStarSpecSchema.parse(spec);
    const comp = options?.compVarName ?? "comp";
    const angles = this.computeDiffractionAngles(validated.points, validated.rotationDegrees);
    const blackIn = Math.round((validated.thresholdPercent / 100) * 255);

    const lines: string[] = [
      `  // === PRISM STAR DIFFRACTION: ${validated.id} (${validated.points}-Point Star) ===`,
      "  try {",
      `    if (${comp}) {`,
      `      var starAdj = ${comp}.layers.addSolid([0, 0, 0], '[PRISM STAR ' + '${validated.points}PT] ' + '${validated.id}', ${comp}.width, ${comp}.height, 1.0);`,
      "      if (starAdj) {",
      "        starAdj.adjustmentLayer = true;",
      "        starAdj.blendingMode = BlendingMode.ADD;",
      "        starAdj.motionBlur = true;",
      "",
      "        // 1. Extracción de altas luces especulares puntuales",
      '        var levelsFx = starAdj.property("Effects").addProperty("ADBE Levels2");',
      "        if (levelsFx) {",
      `          levelsFx.property("Input Black").setValue(${blackIn});`,
      '          levelsFx.property("Input White").setValue(255);',
      "        }",
      "",
      "        // 2. Difracción multidireccional cruzada",
    ];

    angles.forEach((ang, idx) => {
      lines.push(
        `        var blurFx${idx} = starAdj.property("Effects").addProperty("ADBE Directional Blur");`,
        `        if (blurFx${idx}) {`,
        `          blurFx${idx}.property("Direction").setValue(${ang.toFixed(1)});`,
        `          blurFx${idx}.property("Blur Length").setValue(${validated.starLength.toFixed(1)});`,
        "        }"
      );
    });

    lines.push(
      "",
      "        // 3. Opacidad de difracción",
      `        var opVal = Math.min(100.0, ${validated.intensity.toFixed(2)} * 85.0);`,
      "        starAdj.property(\"Transform\").property(\"Opacity\").setValue(opVal);"
    );

    if (validated.startTimeSeconds !== undefined && validated.durationSeconds !== undefined) {
      const inT = validated.startTimeSeconds;
      const outT = validated.startTimeSeconds + validated.durationSeconds;
      lines.push(
        `        starAdj.startTime = ${inT.toFixed(4)};`,
        `        starAdj.inPoint = ${inT.toFixed(4)};`,
        `        starAdj.outPoint = ${outT.toFixed(4)};`
      );
    }

    lines.push(
      "      }",
      "    }",
      "  } catch(e) {",
      `    alert('Error in PrismStarEngine: ' + e.toString());`,
      "  }"
    );

    return lines;
  }
}
