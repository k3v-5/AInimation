export interface FilmBorderConfig {
  compWidth: number;
  compHeight: number;
  sprocketHolesCount?: number;
  filmGaugeMm?: 16 | 35;
}

/**
 * Motor Especializado del Preset #6: High-End Agency & Luxury Monocromo (Iman Gadzhi Style).
 * Genera estética editorial monocromática de alta moda, marcos de negativo fotográfico 16/35mm y flash frames.
 */
export class AgencyLuxuryPreset {
  public static readonly PALETTE = {
    pureBlack: [0.02, 0.02, 0.02] as [number, number, number], // #050505
    pureWhite: [0.98, 0.98, 0.98] as [number, number, number], // #FAFAFA
    emeraldGreen: [0.063, 0.725, 0.506] as [number, number, number], // #10B981
    monochromeGray: [0.55, 0.55, 0.55] as [number, number, number], // #8C8C8C
  };

  /**
   * Genera el fragmento ExtendScript para un marco de negativo de película 16mm/35mm.
   */
  public static generateFilmBordersSnippet(compVar: string, config: FilmBorderConfig): string {
    const pal = this.PALETTE;
    return [
      `// === 16MM/35MM FILM NEGATIVE BORDERS ===`,
      `var borderLayer = ${compVar}.layers.addShape();`,
      `borderLayer.name = "Film_Borders_Overlay";`,
      `var bGroup = borderLayer.property("Contents").addProperty("ADBE Vector Group");`,
      `var bRect = bGroup.property("Contents").addProperty("ADBE Vector Shape - Rect");`,
      `bRect.property("Size").setValue([${config.compWidth - 80}, ${config.compHeight - 80}]);`,
      `var bStroke = bGroup.property("Contents").addProperty("ADBE Vector Graphic - Stroke");`,
      `bStroke.property("Color").setValue([${pal.pureWhite[0]}, ${pal.pureWhite[1]}, ${pal.pureWhite[2]}]);`,
      `bStroke.property("Stroke Width").setValue(8);`,
      `// Añadir grano cinematográfico`,
      `var grain = borderLayer.property("Effects").addProperty("ADBE Noise");`,
      `if (grain) { grain.property("Amount").setValue(25); }`,
    ].join("\n");
  }

  /**
   * Genera el fragmento ExtendScript para un titular de lujo editorial (Bodoni / Didot).
   */
  public static generateLuxuryHeadlineSnippet(
    compVar: string,
    titleText: string,
    position: [number, number]
  ): string {
    const pal = this.PALETTE;
    return [
      `// === HIGH-END LUXURY EDITORIAL HEADLINE ===`,
      `var txt = ${compVar}.layers.addText("${titleText}");`,
      `txt.name = "Luxury_Title";`,
      `txt.transform.position.setValue([${position[0]}, ${position[1]}]);`,
      `var tProp = txt.property("Source Text");`,
      `var tDoc = tProp.value;`,
      `tDoc.fontSize = 80;`,
      `tDoc.font = "BodoniMT-Bold";`,
      `tDoc.fillColor = [${pal.pureWhite[0]}, ${pal.pureWhite[1]}, ${pal.pureWhite[2]}];`,
      `tDoc.tracking = 20;`,
      `tProp.setValue(tDoc);`,
    ].join("\n");
  }
}
