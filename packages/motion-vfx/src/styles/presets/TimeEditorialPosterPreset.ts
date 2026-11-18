export interface EditorialDialConfig {
  center: [number, number];
  radiusPx?: number;
  ticksCount?: number;
}

/**
 * Motor Especializado del Preset #15: The TIME Editorial News Poster (Estilo Insignia Maestro).
 * Cumple rigurosamente la guía maestra de diseño del usuario:
 * - Tipografía Impact/Arial Black ultra-condensada estirada verticalmente al 130%-150%
 * - Paleta rojo carmesí #FF1424 + blanco puro #FFFFFF sobre negro absoluto
 * - Interletraje negativo (-5) y justificación ParagraphJustification.CENTER_JUSTIFY
 * - Diales/ticks vectoriales de acompañamiento y Motion Blur absoluto.
 */
export class TimeEditorialPosterPreset {
  public static readonly PALETTE = {
    crimsonRed: [1.0, 0.078, 0.141] as [number, number, number], // #FF1424
    pureWhite: [1.0, 1.0, 1.0] as [number, number, number], // #FFFFFF
    carbonBlack: [0.04, 0.04, 0.04] as [number, number, number], // #0A0A0A
    borderRed: [0.9, 0.05, 0.1] as [number, number, number],
  };

  /**
   * Genera el fragmento ExtendScript para el gran titular central estilo TIME Editorial Poster.
   */
  public static generateTIMEHeadlineSnippet(
    compVar: string,
    headlineText: string,
    position: [number, number],
    verticalStretchPct = 140
  ): string {
    const pal = this.PALETTE;
    return [
      `// === TIME EDITORIAL POSTER HEADLINE ===`,
      `var txt = ${compVar}.layers.addText("${headlineText}");`,
      `txt.name = "TIME_Headline";`,
      `txt.transform.position.setValue([${position[0]}, ${position[1]}]);`,
      `var tProp = txt.property("ADBE Text Properties") ? txt.property("ADBE Text Properties").property("ADBE Text Document") : (txt.property("Source Text") || txt.property("Texto de origen"));`,
      `if (!tProp) { tProp = txt.text.sourceText; }`,
      `var tDoc = tProp.value;`,
      `tDoc.fontSize = 110;`,
      `try { tDoc.font = "Impact"; } catch(e) {}`,
      `tDoc.fillColor = [${pal.pureWhite[0]}, ${pal.pureWhite[1]}, ${pal.pureWhite[2]}];`,
      `tDoc.tracking = -5;`,
      `tDoc.justification = ParagraphJustification.CENTER_JUSTIFY;`,
      `tProp.setValue(tDoc);`,
      `// Estiramiento vertical característico (130% - 150%)`,
      `txt.transform.scale.setValue([100, ${verticalStretchPct}]);`,
      `// Motion Blur en la composición`,
      `${compVar}.motionBlur = true;`,
    ].join("\n");
  }

  /**
   * Genera el fragmento ExtendScript para un marco perimetral rojo carmesí estilo TIME Magazine.
   */
  public static generateTIMEFrameSnippet(
    compVar: string,
    compWidth: number,
    compHeight: number
  ): string {
    const pal = this.PALETTE;
    return [
      `// === TIME MAGAZINE CRIMSON RED BORDER ===`,
      `var frame = ${compVar}.layers.addShape();`,
      `frame.name = "TIME_Crimson_Border";`,
      `var fContents = frame.property("ADBE Root Vectors Group") || frame.property("Contents") || frame.property("Contenido");`,
      `var fGroup = fContents.addProperty("ADBE Vector Group");`,
      `var fGroupContents = fGroup.property("ADBE Vectors Group") || fGroup.property("Contents") || fGroup.property("Contenido");`,
      `var fRect = fGroupContents.addProperty("ADBE Vector Shape - Rect");`,
      `fRect.property("Size").setValue([${compWidth - 40}, ${compHeight - 40}]);`,
      `var fStroke = fGroupContents.addProperty("ADBE Vector Graphic - Stroke");`,
      `fStroke.property("Color").setValue([${pal.crimsonRed[0]}, ${pal.crimsonRed[1]}, ${pal.crimsonRed[2]}]);`,
      `fStroke.property("Stroke Width").setValue(16);`,
    ].join("\n");
  }

  /**
   * Genera el fragmento ExtendScript para diales y ticks vectoriales de precisión militar/editorial.
   */
  public static generateEditorialDialSnippet(
    compVar: string,
    config: EditorialDialConfig,
    startTimeSec: number
  ): string {
    const pal = this.PALETTE;
    const r = config.radiusPx ?? 120;
    return [
      `// === VECTORIAL EDITORIAL DIAL ===`,
      `var dial = ${compVar}.layers.addShape();`,
      `dial.name = "Editorial_Dial";`,
      `dial.inPoint = ${startTimeSec};`,
      `dial.transform.position.setValue([${config.center[0]}, ${config.center[1]}]);`,
      `var dContents = dial.property("ADBE Root Vectors Group") || dial.property("Contents") || dial.property("Contenido");`,
      `var dGroup = dContents.addProperty("ADBE Vector Group");`,
      `var dGroupContents = dGroup.property("ADBE Vectors Group") || dGroup.property("Contents") || dGroup.property("Contenido");`,
      `var dCircle = dGroupContents.addProperty("ADBE Vector Shape - Ellipse");`,
      `dCircle.property("Size").setValue([${r * 2}, ${r * 2}]);`,
      `var dStroke = dGroupContents.addProperty("ADBE Vector Graphic - Stroke");`,
      `dStroke.property("Color").setValue([${pal.crimsonRed[0]}, ${pal.crimsonRed[1]}, ${pal.crimsonRed[2]}]);`,
      `dStroke.property("Stroke Width").setValue(2);`,
      `// Rotación continua del dial`,
      `dial.transform.rotation.expression = "time * 45;";`,
    ].join("\n");
  }
}
