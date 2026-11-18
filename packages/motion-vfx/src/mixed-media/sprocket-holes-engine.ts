import { SprocketHolesSpec, SprocketHolesSpecInput, SprocketHolesSpecSchema } from "./mixed-media-types.js";

/**
 * Motor de 35mm / 16mm Sprocket Holes y Gate Weave Jitter (Fase 28).
 * Simula las perforaciones mecánicas de celuloide en los márgenes de la película,
 * texto KeyKode de laboratorio y temblor orgánico de ventanilla de arrastre.
 */
export class SprocketHolesEngine {
  /**
   * Calcula las posiciones Y normalizadas de las perforaciones según el calibre de película.
   * 35mm tiene 4 perforaciones por fotograma estándar; 16mm tiene 1 por fotograma.
   */
  public static computePerforationPositions(compHeight: number, gauge: "35MM" | "16MM"): number[] {
    const h = compHeight > 0 ? compHeight : 1080;
    const count = gauge === "35MM" ? 4 : 1;
    const positions: number[] = [];
    const step = h / count;
    for (let i = 0; i < count; i++) {
      positions.push(Math.round((i + 0.5) * step));
    }
    return positions;
  }

  /**
   * Genera código ExtendScript nativo para inyectar la capa de celuloide con perforaciones y jitter.
   */
  public static exportToExtendScript(
    spec: SprocketHolesSpecInput,
    options?: { compVarName?: string }
  ): string[] {
    const validated = SprocketHolesSpecSchema.parse(spec);
    const comp = options?.compVarName ?? "comp";
    const marginW = validated.gauge === "35MM" ? 90 : 60;
    const holeW = validated.gauge === "35MM" ? 48 : 32;
    const holeH = validated.gauge === "35MM" ? 64 : 44;

    const lines: string[] = [
      `  // === 35MM SPROCKET HOLES & GATE WEAVE: ${validated.id} (${validated.gauge}) ===`,
      "  try {",
      `    if (${comp}) {`,
      `      var sprockSolid = ${comp}.layers.addSolid([0.02, 0.02, 0.02], '[SPROCKET FILM BORDER] ' + '${validated.id}', ${comp}.width, ${comp}.height, 1.0);`,
      "      if (sprockSolid) {",
      "        sprockSolid.motionBlur = true;",
      `        sprockSolid.property("Transform").property("Opacity").setValue(${validated.opacity.toFixed(1)});`,
      "",
      "        // 1. Inestabilidad mecánica de ventanilla de proyección (Gate Weave Jitter)",
      '        var posProp = sprockSolid.property("Transform").property("Position");',
      `        posProp.expression = "wiggle(12, ${validated.gateWeaveJitterPx.toFixed(1)});";`,
      "",
      "        // 2. Máscara de recorte de celuloide marginal",
      '        var borderMask = sprockSolid.property("Masks").addProperty("ADBE Mask Atom");',
      "        if (borderMask) {",
      "          borderMask.maskMode = MaskMode.SUBTRACT;",
      "          var bShape = borderMask.property(\"Mask Path\").value;",
      `          var lW = ${validated.side === "RIGHT" ? 0 : marginW};`,
      `          var rW = ${validated.side === "LEFT" ? 0 : marginW};`,
      `          bShape.vertices = [[lW, 0], [${comp}.width - rW, 0], [${comp}.width - rW, ${comp}.height], [lW, ${comp}.height]];`,
      "          bShape.closed = true;",
      '          borderMask.property("Mask Path").setValue(bShape);',
      "        }",
    ];

    if (validated.keyKodeText) {
      lines.push(
        "",
        "        // 3. Estampado KeyKode de celuloide marginal (Kodak / Fujifilm edge text)",
        `        var keyKodeLyr = ${comp}.layers.addText('${validated.keyKodeText}');`,
        "        if (keyKodeLyr) {",
        "          keyKodeLyr.name = '[KEYKODE TEXT] ' + '" + validated.id + "';",
        "          var textProp = keyKodeLyr.property(\"Source Text\");",
        "          var textDoc = textProp.value;",
        "          textDoc.fontSize = 18;",
        "          textDoc.fillColor = [0.95, 0.82, 0.45]; // Amarillo dorado Kodak",
        "          textDoc.font = 'CourierNewPSMT';",
        "          textProp.setValue(textDoc);",
        `          keyKodeLyr.property("Transform").property("Rotation").setValue(90.0);`,
        `          keyKodeLyr.property("Transform").property("Position").setValue([${marginW / 2}, ${comp}.height * 0.5]);`,
        "          keyKodeLyr.parent = sprockSolid; // Vinculado al jitter mecánico",
        "        }"
      );
    }

    lines.push(
      "      }",
      "    }",
      "  } catch(e) {",
      `    alert('Error in SprocketHolesEngine: ' + e.toString());`,
      "  }"
    );

    return lines;
  }
}
