import {
  BrutalistTypeSpec,
  BrutalistTypeSpecInput,
  BrutalistTypeSpecSchema,
} from "./kinetic-typography-types.js";

/**
 * Motor de tipografía brutalista editorial de impacto masivo (TIME / Tyler Style).
 */
export class BrutalistTypeEngine {
  /**
   * Convierte un código hexadecimal (#RRGGBB) a una tupla normalizada [r, g, b] en [0, 1].
   */
  public static hexToRgbTuple(hex: string): [number, number, number] {
    const cleanHex = hex.replace("#", "");
    if (cleanHex.length !== 6) return [1.0, 0.078, 0.141]; // Default #FF1424
    const r = parseInt(cleanHex.substring(0, 2), 16) / 255.0;
    const g = parseInt(cleanHex.substring(2, 4), 16) / 255.0;
    const b = parseInt(cleanHex.substring(4, 6), 16) / 255.0;
    return [
      Number(r.toFixed(4)),
      Number(g.toFixed(4)),
      Number(b.toFixed(4)),
    ];
  }

  /**
   * Genera las sentencias ExtendScript para crear y maquetar la capa de texto brutalista.
   */
  public static exportToExtendScript(
    specInput: BrutalistTypeSpecInput,
    options: { compVarName?: string; layerVarName?: string } = {}
  ): string[] {
    const spec = BrutalistTypeSpecSchema.parse(specInput);
    const compVar = options.compVarName ?? "comp";
    const layerVar = options.layerVarName ?? "textLyr";
    const lines: string[] = [];

    const displayText = spec.allCaps ? spec.text.toUpperCase() : spec.text;
    const rgb = this.hexToRgbTuple(spec.colorHex);
    const escapedText = displayText.replace(/'/g, "\\'");

    lines.push(`  // === BRUTALIST KINETIC TYPOGRAPHY: ${spec.id} ===`);
    lines.push(`  try {`);
    lines.push(`    var ${layerVar} = ${compVar}.layers.addText('${escapedText}');`);
    lines.push(`    ${layerVar}.name = '[BRUTALIST TYPE] ${escapedText.substring(0, 20)}';`);
    lines.push(`    ${layerVar}.motionBlur = true; // Invariante obligatoria`);
    lines.push(`    var textProp = ${layerVar}.property("Source Text");`);
    lines.push(`    var textDoc = textProp.value;`);
    lines.push(`    textDoc.font = '${spec.fontFamily}';`);
    lines.push(`    textDoc.fontSize = ${spec.fontSizePx};`);
    lines.push(`    textDoc.tracking = ${spec.tracking};`);
    lines.push(`    textDoc.fillColor = [${rgb[0]}, ${rgb[1]}, ${rgb[2]}];`);
    lines.push(`    textDoc.applyFill = true;`);
    lines.push(`    textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;`);
    lines.push(`    textProp.setValue(textDoc);`);
    lines.push(``);
    lines.push(`    // Recalcular punto de anclaje geométrico centrado`);
    lines.push(`    var b = ${layerVar}.sourceRectAtTime(0, false);`);
    lines.push(`    ${layerVar}.property("Transform").property("Anchor Point").setValue([b.left + b.width / 2, b.top + b.height / 2]);`);
    lines.push(`    ${layerVar}.property("Transform").property("Position").setValue([${compVar}.width / 2, ${compVar}.height / 2]);`);
    lines.push(``);
    lines.push(`    // Deformación vertical anamórfica (Anamorphic Vertical Stretch)`);
    lines.push(`    ${layerVar}.property("Transform").property("Scale").setValue([100.0, ${spec.verticalStretchPercent.toFixed(1)}]);`);
    lines.push(`  } catch(e) {`);
    lines.push(`    alert('Error in BrutalistTypeEngine: ' + e.toString());`);
    lines.push(`  }`);

    return lines;
  }
}
