import { AuteurColorGradingSpec, AuteurColorGradingSpecInput, AuteurColorGradingSpecSchema } from "./film-types.js";

/**
 * Motor de perfiles cromáticos de autor (Tyler, Kendrick, Ralphie Choo).
 */
export class AuteurColorGradingEngine {
  /**
   * Resuelve los parámetros canónicos para cada perfil de autor.
   */
  public static resolveProfileSettings(specInput: AuteurColorGradingSpecInput): {
    saturationMultiplier: number;
    contrastMultiplier: number;
    liftPedestal: number;
    shadowTint: [number, number, number];
    highlightTint: [number, number, number];
  } {
    const spec = AuteurColorGradingSpecSchema.parse(specInput);

    switch (spec.profile) {
      case "TYLER_PASTEL_70S":
        return {
          saturationMultiplier: 1.18,
          contrastMultiplier: 1.06,
          liftPedestal: 0.05, // Sombras levantadas analógicas
          shadowTint: [-5, 8, 12], // Turquesa / menta en sombras
          highlightTint: [15, 8, -10], // Ámbar cálido años 70 en altas luces
        };

      case "KENDRICK_BLEACH_BYPASS_BW":
        return {
          saturationMultiplier: 0.0, // Monocromo puro de retención de plata
          contrastMultiplier: 1.75,  // Claroscuro dramático
          liftPedestal: -0.04,       // Negros puros aplastados
          shadowTint: [0, 0, 0],
          highlightTint: [5, 5, 8],  // Tinte metálico frío sutil
        };

      case "RALPHIE_MINIDV_ACID":
        return {
          saturationMultiplier: 1.50, // Saturación ácida Y2K
          contrastMultiplier: 1.30,
          liftPedestal: 0.04,
          shadowTint: [-8, 2, 14],  // Pedestal azulado
          highlightTint: [18, 12, -6], // Altas luces saturadas
        };

      case "CUSTOM":
      default:
        return {
          saturationMultiplier: spec.saturation,
          contrastMultiplier: spec.contrast,
          liftPedestal: spec.liftPedestal,
          shadowTint: (spec.shadowTintRgb as any) ?? [0, 0, 0],
          highlightTint: (spec.highlightTintRgb as any) ?? [0, 0, 0],
        };
    }
  }

  /**
   * Genera el código ExtendScript para aplicar el color grading de autor en After Effects.
   */
  public static exportToExtendScript(
    specInput: AuteurColorGradingSpecInput,
    options: { layerVarName?: string } = {}
  ): string[] {
    const spec = AuteurColorGradingSpecSchema.parse(specInput);
    const settings = this.resolveProfileSettings(spec);
    const layerVar = options.layerVarName ?? "targetLayer";
    const lines: string[] = [];

    lines.push(`  // === AUTEUR COLOR GRADING (Profile: ${spec.profile}) ===`);
    lines.push(`  try {`);
    lines.push(`    // 1. Saturación`);
    lines.push(`    var hlsFx = ${layerVar}.property("Effects").addProperty("ADBE Color Balance (HLS)");`);
    lines.push(`    if (hlsFx) {`);
    lines.push(`      hlsFx.property("Saturation").setValue(${(settings.saturationMultiplier * 100 - 100).toFixed(1)});`);
    lines.push(`    }`);
    lines.push(`    // 2. Contraste y Brillo`);
    lines.push(`    var bcFx = ${layerVar}.property("Effects").addProperty("ADBE Brightness & Contrast 2");`);
    lines.push(`    if (bcFx) {`);
    lines.push(`      bcFx.property("Contrast").setValue(${((settings.contrastMultiplier - 1.0) * 80).toFixed(1)});`);
    lines.push(`      bcFx.property("Brightness").setValue(${(settings.liftPedestal * 100).toFixed(1)});`);
    lines.push(`    }`);
    lines.push(`    // 3. Balance de Color (Tintes en sombras y altas luces)`);
    lines.push(`    var cbFx = ${layerVar}.property("Effects").addProperty("ADBE Color Balance");`);
    lines.push(`    if (cbFx) {`);
    lines.push(`      cbFx.property("Shadow Red Balance").setValue(${settings.shadowTint[0]});`);
    lines.push(`      cbFx.property("Shadow Green Balance").setValue(${settings.shadowTint[1]});`);
    lines.push(`      cbFx.property("Shadow Blue Balance").setValue(${settings.shadowTint[2]});`);
    lines.push(`      cbFx.property("Highlight Red Balance").setValue(${settings.highlightTint[0]});`);
    lines.push(`      cbFx.property("Highlight Green Balance").setValue(${settings.highlightTint[1]});`);
    lines.push(`      cbFx.property("Highlight Blue Balance").setValue(${settings.highlightTint[2]});`);
    lines.push(`      cbFx.property("Preserve Luminosity").setValue(true);`);
    lines.push(`    }`);
    lines.push(`  } catch(e) {}`);

    return lines;
  }
}
