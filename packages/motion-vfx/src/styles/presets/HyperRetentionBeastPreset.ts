export interface BouncingArrowConfig {
  targetPoint: [number, number];
  arrowLengthPx?: number;
  bounceFrequency?: number;
  color?: [number, number, number];
}

/**
 * Motor Especializado del Preset #7: Hyper-Retention Beast (MrBeast / Ryan Trahan Style).
 * Genera títulos 3D con borde negro de 12px, flechas dinámicas de rebote sinusoidal y stickers vectoriales.
 */
export class HyperRetentionBeastPreset {
  public static readonly PALETTE = {
    beastYellow: [0.98, 0.8, 0.082] as [number, number, number], // #FACC15
    beastRed: [0.937, 0.267, 0.267] as [number, number, number], // #EF4444
    beastGreen: [0.133, 0.773, 0.369] as [number, number, number], // #22C55E
    borderBlack: [0.0, 0.0, 0.0] as [number, number, number], // #000000
    textWhite: [1.0, 1.0, 1.0] as [number, number, number], // #FFFFFF
  };

  /**
   * Evalúa la oscilación vertical de rebote sinusoidal para flechas dinámicas de atención.
   * y(t) = y0 + amplitude * sin(freq * t)
   */
  public static evaluateSinusoidalBounce(t: number, baseY: number, amplitude = 22, freq = 12): number {
    const offset = amplitude * Math.sin(freq * t);
    return Number((baseY + offset).toFixed(2));
  }

  /**
   * Genera el fragmento ExtendScript para un título 3D gigante con trazo negro y sombra dura.
   */
  public static generateBeastTitleSnippet(
    compVar: string,
    titleText: string,
    position: [number, number]
  ): string {
    const pal = this.PALETTE;
    return [
      `// === HYPER-RETENTION 3D BEAST TITLE ===`,
      `var txt = ${compVar}.layers.addText("${titleText}");`,
      `txt.name = "Beast_Title";`,
      `txt.transform.position.setValue([${position[0]}, ${position[1]}]);`,
      `var tProp = txt.property("Source Text");`,
      `var tDoc = tProp.value;`,
      `tDoc.fontSize = 96;`,
      `tDoc.font = "Impact";`,
      `tDoc.fillColor = [${pal.beastYellow[0]}, ${pal.beastYellow[1]}, ${pal.beastYellow[2]}];`,
      `tDoc.strokeColor = [0, 0, 0];`,
      `tDoc.strokeWidth = 14;`,
      `tDoc.strokeOverFill = false;`,
      `tProp.setValue(tDoc);`,
      `// Sombra dura 3D`,
      `var ds = txt.property("Effects").addProperty("ADBE Drop Shadow");`,
      `ds.property("Opacity").setValue(100);`,
      `ds.property("Distance").setValue(18);`,
      `ds.property("Softness").setValue(0);`,
      `ds.property("Direction").setValue(135);`,
    ].join("\n");
  }

  /**
   * Genera el fragmento ExtendScript para una flecha animada que rebota apuntando al sujeto.
   */
  public static generateBouncingArrowSnippet(
    compVar: string,
    config: BouncingArrowConfig,
    startTimeSec: number
  ): string {
    const pal = this.PALETTE;
    const arrowCol = config.color ?? pal.beastRed;
    const tp = config.targetPoint;

    return [
      `// === DYNAMIC BOUNCING ARROW ===`,
      `var arrow = ${compVar}.layers.addShape();`,
      `arrow.name = "Beast_Arrow_Pointer";`,
      `arrow.inPoint = ${startTimeSec};`,
      `arrow.transform.position.setValue([${tp[0]}, ${tp[1]} - 80]);`,
      `var aGroup = arrow.property("Contents").addProperty("ADBE Vector Group");`,
      `var aFill = aGroup.property("Contents").addProperty("ADBE Vector Graphic - Fill");`,
      `aFill.property("Color").setValue([${arrowCol[0]}, ${arrowCol[1]}, ${arrowCol[2]}]);`,
      `var aStroke = aGroup.property("Contents").addProperty("ADBE Vector Graphic - Stroke");`,
      `aStroke.property("Color").setValue([0, 0, 0]);`,
      `aStroke.property("Stroke Width").setValue(6);`,
      `// Expresión de rebote sinusoidal continuo`,
      `arrow.transform.position.expression = "var y = value[1] + 20 * Math.sin(time * 12); [value[0], y];";`,
    ].join("\n");
  }
}
