import {
  LiquidChromeSpec,
  LiquidChromeSpecInput,
  LiquidChromeSpecSchema,
} from "./kinetic-typography-types.js";

/**
 * Motor de shader procedural de Cromo Líquido reflectante (Liquid Chrome).
 */
export class LiquidChromeEngine {
  /**
   * Genera el stack de efectos ExtendScript para aplicar el look metálico viscoso a una capa.
   */
  public static exportToExtendScript(
    specInput: LiquidChromeSpecInput,
    options: { layerVarName?: string } = {}
  ): string[] {
    const spec = LiquidChromeSpecSchema.parse(specInput);
    const layerVar = options.layerVarName ?? "textLyr";
    const lines: string[] = [];

    // Resolver tinte de paleta cromática
    let mapWhiteTo = "[0.95, 0.95, 0.98]"; // PLATINUM por defecto
    if (spec.chromePalette === "ACID_EMERALD") {
      mapWhiteTo = "[0.45, 1.00, 0.55]"; // Cromo verdoso ácido
    } else if (spec.chromePalette === "MOLTEN_GOLD") {
      mapWhiteTo = "[1.00, 0.85, 0.35]"; // Oro líquido
    } else if (spec.tintRgb) {
      mapWhiteTo = `[${spec.tintRgb[0]}, ${spec.tintRgb[1]}, ${spec.tintRgb[2]}]`;
    }

    lines.push(`  // === LIQUID CHROME SHADER: ${spec.id} (${spec.chromePalette}) ===`);
    lines.push(`  try {`);
    lines.push(`    // 1. Bisel Alfa Metálico`);
    lines.push(`    var bevelFx = ${layerVar}.property("Effects").addProperty("ADBE Bevel Alpha");`);
    lines.push(`    if (bevelFx) {`);
    lines.push(`      bevelFx.property("Edge Thickness").setValue(${spec.bevelDepthPx.toFixed(1)});`);
    lines.push(`      bevelFx.property("Light Angle").setValue(45.0);`);
    lines.push(`      bevelFx.property("Light Intensity").setValue(0.65);`);
    lines.push(`    }`);
    lines.push(``);
    lines.push(`    // 2. Deformación Ondulatoria Turbulenta Líquida`);
    lines.push(`    var turbFx = ${layerVar}.property("Effects").addProperty("ADBE Turbulent Displace");`);
    lines.push(`    if (turbFx) {`);
    lines.push(`      turbFx.property("Amount").setValue(${spec.turbulentAmount.toFixed(1)});`);
    lines.push(`      turbFx.property("Size").setValue(${spec.turbulentSize.toFixed(1)});`);
    lines.push(`      turbFx.property("Evolution").expression = "time * ${(spec.evolutionSpeed * 120.0).toFixed(1)};";`);
    lines.push(`    }`);
    lines.push(``);
    lines.push(`    // 3. Contraste y Reflexión Metálica`);
    lines.push(`    var bcFx = ${layerVar}.property("Effects").addProperty("ADBE Brightness & Contrast 2");`);
    lines.push(`    if (bcFx) {`);
    lines.push(`      bcFx.property("Contrast").setValue(45.0);`);
    lines.push(`      bcFx.property("Brightness").setValue(10.0);`);
    lines.push(`    }`);
    lines.push(``);
    lines.push(`    // 4. Mapeo de Tinte Cromático`);
    lines.push(`    var tintFx = ${layerVar}.property("Effects").addProperty("ADBE Tint");`);
    lines.push(`    if (tintFx) {`);
    lines.push(`      tintFx.property("Map Black To").setValue([0.05, 0.05, 0.08]);`);
    lines.push(`      tintFx.property("Map White To").setValue(${mapWhiteTo});`);
    lines.push(`      tintFx.property("Amount to Tint").setValue(85.0);`);
    lines.push(`    }`);
    lines.push(`  } catch(e) {`);
    lines.push(`    alert('Error in LiquidChromeEngine: ' + e.toString());`);
    lines.push(`  }`);

    return lines;
  }
}
