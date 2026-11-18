export type ColorGradePresetName =
  | "teal_orange"
  | "kodak_35mm"
  | "cyberpunk_crimson"
  | "golden_hour"
  | "clean_commercial";

export interface ColorGradeProfile {
  name: ColorGradePresetName;
  description: string;
  shadows: [number, number, number]; // [r, g, b] offset / tint en sombras
  midtones: [number, number, number]; // [r, g, b] balance en medios tonos
  highlights: [number, number, number]; // [r, g, b] tinte en altas luces
  saturation: number; // Porcentaje de saturación (ej. 95)
  contrast: number; // Contraste [-100, 100]
  vignetteAmount: number; // Cantidad de viñeta [0, 100]
  liftPedestal: number; // Levantamiento de negros para look de película (ej. 0.04)
}

/**
 * Motor de gradación de color cinemática y LUTs procedurales (Fase 4C / Mejoras).
 * Aplica perfiles de color de nivel de producción cinematográfica (Hollywood Teal & Orange, Kodak 35mm, Cyberpunk)
 * en capas individuales o capas de ajuste globales de After Effects.
 */
export class CinematicColorGradingEngine {
  private static readonly PRESETS: Record<ColorGradePresetName, ColorGradeProfile> = {
    teal_orange: {
      name: "teal_orange",
      description: "Hollywood Teal & Orange: Sombras cian frías con tonos de piel cálidos y ámbar",
      shadows: [0.0, 0.55, 0.65],
      midtones: [1.0, 0.85, 0.70],
      highlights: [1.0, 0.75, 0.45],
      saturation: 110,
      contrast: 18,
      vignetteAmount: 35,
      liftPedestal: 0.02,
    },
    kodak_35mm: {
      name: "kodak_35mm",
      description: "Kodak 35mm Film: Negros levantados orgánicos, grano analógico y compresión de altas luces",
      shadows: [0.15, 0.12, 0.10],
      midtones: [1.0, 0.98, 0.92],
      highlights: [0.98, 0.95, 0.90],
      saturation: 92,
      contrast: 10,
      vignetteAmount: 25,
      liftPedestal: 0.05,
    },
    cyberpunk_crimson: {
      name: "cyberpunk_crimson",
      description: "Cyberpunk Crimson: Rojos carmesí profundos, sombras violetas y contraste agresivo",
      shadows: [0.25, 0.05, 0.35],
      midtones: [0.95, 0.15, 0.25],
      highlights: [1.0, 0.85, 0.20],
      saturation: 125,
      contrast: 28,
      vignetteAmount: 45,
      liftPedestal: 0.01,
    },
    golden_hour: {
      name: "golden_hour",
      description: "Golden Hour: Resplandor dorado de atardecer con balance cálido y sombras suaves",
      shadows: [0.18, 0.12, 0.05],
      midtones: [1.0, 0.82, 0.40],
      highlights: [1.0, 0.90, 0.60],
      saturation: 105,
      contrast: 14,
      vignetteAmount: 30,
      liftPedestal: 0.03,
    },
    clean_commercial: {
      name: "clean_commercial",
      description: "Clean Commercial: Blanco puro, colores vibrantes y contraste cristalino estilo Apple",
      shadows: [0.0, 0.0, 0.0],
      midtones: [1.0, 1.0, 1.0],
      highlights: [1.0, 1.0, 1.0],
      saturation: 102,
      contrast: 8,
      vignetteAmount: 10,
      liftPedestal: 0.0,
    },
  };

  /**
   * Obtiene el perfil de color correspondiente a un preset.
   */
  public static getProfile(presetName: ColorGradePresetName): ColorGradeProfile {
    return this.PRESETS[presetName] ?? this.PRESETS.teal_orange;
  }

  /**
   * Genera el fragmento ExtendScript para aplicar el perfil de gradación de color a una capa de ajuste o clip.
   */
  public static generateExtendScriptGrade(
    compVar: string,
    layerName: string,
    presetName: ColorGradePresetName,
    inTime = 0.0,
    outTime = 220.0
  ): string {
    const p = this.getProfile(presetName);

    return [
      `// === CINEMATIC COLOR GRADE: ${p.name.toUpperCase()} ===`,
      `var adjLayer = ${compVar}.layers.addSolid([0.5, 0.5, 0.5], "${layerName}_Grade_${p.name}", ${compVar}.width, ${compVar}.height, 1.0, ${outTime - inTime});`,
      `adjLayer.adjustmentLayer = true;`,
      `adjLayer.startTime = ${inTime};`,
      `adjLayer.inPoint = ${inTime};`,
      `adjLayer.outPoint = ${outTime};`,
      `try {`,
      `  var colBal = adjLayer.property("Effects").addProperty("ADBE Color Balance (HLS)");`,
      `  if (colBal) {`,
      `    colBal.property("Saturation").setValue(${p.saturation - 100});`,
      `    colBal.property("Lightness").setValue(${p.contrast / 4});`,
      `  }`,
      `} catch(e1) {}`,
      `try {`,
      `  var tint = adjLayer.property("Effects").addProperty("ADBE Tint");`,
      `  if (tint) {`,
      `    tint.property("Map Black To").setValue([${p.shadows[0]}, ${p.shadows[1]}, ${p.shadows[2]}]);`,
      `    tint.property("Map White To").setValue([${p.highlights[0]}, ${p.highlights[1]}, ${p.highlights[2]}]);`,
      `    tint.property("Amount to Tint").setValue(35);`,
      `  }`,
      `} catch(e2) {}`,
    ].join("\n");
  }
}
