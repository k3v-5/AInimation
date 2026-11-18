import { SpeedLinesSpec, SpeedLinesSpecInput, SpeedLinesSpecSchema } from "./mixed-media-types.js";

/**
 * Motor de Speed Lines Radiales Procedurales (Anime Kinetics) (Fase 28).
 * Emula los haces cinéticos de velocidad de manga/anime convergentes hacia el sujeto
 * con zona de exclusión central y parpadeo posterizado a 12 fps.
 */
export class SpeedLinesEngine {
  /**
   * Determina geométricamente si un punto (x, y) cae dentro de la zona de exclusión central del sujeto.
   */
  public static isInsideExclusionZone(
    x: number,
    y: number,
    center: [number, number],
    innerRadius: number
  ): boolean {
    const dx = x - center[0];
    const dy = y - center[1];
    return Math.sqrt(dx * dx + dy * dy) < innerRadius;
  }

  /**
   * Genera código ExtendScript nativo para inyectar una capa de líneas de velocidad radiales
   * con máscara de exclusión de rostro y expresión de parpadeo posterizado.
   */
  public static exportToExtendScript(
    spec: SpeedLinesSpecInput,
    options?: { compVarName?: string }
  ): string[] {
    const validated = SpeedLinesSpecSchema.parse(spec);
    const comp = options?.compVarName ?? "comp";
    const [cx, cy] = validated.centerPoint;
    const r = validated.innerRadiusPx;
    const [cr, cg, cb] = validated.color;

    const startT = validated.startTimeSeconds;
    const endT = validated.startTimeSeconds + validated.durationSeconds;

    const lines: string[] = [
      `  // === PROCEDURAL SPEED LINES: ${validated.id} ===`,
      "  try {",
      `    if (${comp}) {`,
      `      var speedSolid = ${comp}.layers.addSolid([${cr.toFixed(3)}, ${cg.toFixed(3)}, ${cb.toFixed(3)}], '[SPEED LINES] ' + '${validated.id}', ${comp}.width, ${comp}.height, 1.0);`,
      "      if (speedSolid) {",
      `        speedSolid.startTime = ${startT.toFixed(4)};`,
      `        speedSolid.inPoint = ${startT.toFixed(4)};`,
      `        speedSolid.outPoint = ${endT.toFixed(4)};`,
      "        speedSolid.motionBlur = true;",
      "        speedSolid.blendingMode = BlendingMode.SCREEN;",
      "",
      "        // 1. Máscara elíptica invertida para excluir el rostro del sujeto",
      '        var mask = speedSolid.property("Masks").addProperty("ADBE Mask Atom");',
      "        if (mask) {",
      "          mask.maskMode = MaskMode.SUBTRACT;",
      '          mask.property("Mask Feather").setValue([30.0, 30.0]);',
      "          var maskShape = mask.property(\"Mask Path\").value;",
      `          maskShape.vertices = [[${(cx - r).toFixed(1)}, ${cy.toFixed(1)}], [${cx.toFixed(1)}, ${(cy - r).toFixed(1)}], [${(cx + r).toFixed(1)}, ${cy.toFixed(1)}], [${cx.toFixed(1)}, ${(cy + r).toFixed(1)}]];`,
      `          maskShape.inTangents = [[0, ${(-r * 0.55).toFixed(1)}], [${(-r * 0.55).toFixed(1)}, 0], [0, ${(r * 0.55).toFixed(1)}], [${(r * 0.55).toFixed(1)}, 0]];`,
      `          maskShape.outTangents = [[0, ${(r * 0.55).toFixed(1)}], [${(r * 0.55).toFixed(1)}, 0], [0, ${(-r * 0.55).toFixed(1)}], [${(-r * 0.55).toFixed(1)}, 0]];`,
      "          maskShape.closed = true;",
      '          mask.property("Mask Path").setValue(maskShape);',
      "        }",
      "",
      "        // 2. Ruido fractal radial o Radial Blur en modo Zoom",
      '        var radBlurFx = speedSolid.property("Effects").addProperty("ADBE Radial Blur");',
      "        if (radBlurFx) {",
      "          radBlurFx.property(1).setValue(2); // Zoom mode",
      `          radBlurFx.property(2).setValue(${cx.toFixed(1)}, ${cy.toFixed(1)}); // Center`,
      `          radBlurFx.property(3).setValue(${Math.min(100.0, validated.density * 85.0).toFixed(1)}); // Amount`,
      "        }",
      "",
      "        // 3. Modulación de parpadeo posterizado (Anime Boil)",
      '        var opProp = speedSolid.property("Transform").property("Opacity");',
      `        opProp.expression = "posterizeTime(${validated.boilFps}); 65 + random(-30, 30);";`,
      "      }",
      "    }",
      "  } catch(e) {",
      `    alert('Error in SpeedLinesEngine: ' + e.toString());`,
      "  }",
    ];

    return lines;
  }
}
