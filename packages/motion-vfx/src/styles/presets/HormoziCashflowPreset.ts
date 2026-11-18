export interface HormoziWordHighlight {
  word: string;
  isKeyWord: boolean;
  colorType?: "yellow" | "green" | "red" | "white";
}

/**
 * Motor Especializado del Preset #8: Cashflow Direct-to-Camera (Alex Hormozi Style).
 * Genera subtítulos reactivos de alta retención, resaltado palabra por palabra en amarillo/verde y punch zooms.
 */
export class HormoziCashflowPreset {
  public static readonly PALETTE = {
    neonYellow: [0.918, 0.702, 0.031] as [number, number, number], // #EAB308
    dollarGreen: [0.133, 0.773, 0.369] as [number, number, number], // #22C55E
    alertRed: [0.937, 0.267, 0.267] as [number, number, number], // #EF4444
    pureWhite: [1.0, 1.0, 1.0] as [number, number, number], // #FFFFFF
  };

  /**
   * Resuelve el color exacto para una palabra clave en el estilo Hormozi.
   */
  public static resolveWordColor(type?: "yellow" | "green" | "red" | "white"): [number, number, number] {
    const pal = this.PALETTE;
    switch (type) {
      case "green":
        return pal.dollarGreen;
      case "red":
        return pal.alertRed;
      case "white":
        return pal.pureWhite;
      case "yellow":
      default:
        return pal.neonYellow;
    }
  }

  /**
   * Genera el fragmento ExtendScript para un segmento de subtítulo con caja de fondo adaptativa (Split-Box Pill).
   */
  public static generateHormoziCaptionSnippet(
    compVar: string,
    words: HormoziWordHighlight[],
    position: [number, number],
    startTimeSec: number,
    durationSec = 1.8
  ): string {
    const pal = this.PALETTE;
    const fullText = words.map((w) => w.word.toUpperCase()).join(" ");

    return [
      `// === HORMOZI CASHFLOW RECEPTIVE CAPTION ===`,
      `var txt = ${compVar}.layers.addText("${fullText}");`,
      `txt.name = "Hormozi_Caption_${startTimeSec}";`,
      `txt.transform.position.setValue([${position[0]}, ${position[1]}]);`,
      `txt.inPoint = ${startTimeSec};`,
      `txt.outPoint = ${startTimeSec + durationSec};`,
      `var tProp = txt.property("Source Text");`,
      `var tDoc = tProp.value;`,
      `tDoc.fontSize = 84;`,
      `tDoc.font = "TheBoldFont";`,
      `tDoc.fillColor = [${pal.pureWhite[0]}, ${pal.pureWhite[1]}, ${pal.pureWhite[2]}];`,
      `tDoc.strokeColor = [0, 0, 0];`,
      `tDoc.strokeWidth = 10;`,
      `tDoc.justification = ParagraphJustification.CENTER_JUSTIFY;`,
      `tProp.setValue(tDoc);`,
      `// Animación Pop-in inercial en escala`,
      `txt.transform.scale.setValueAtTime(${startTimeSec}, [130, 150]);`,
      `txt.transform.scale.setValueAtTime(${startTimeSec + 0.12}, [95, 110]);`,
      `txt.transform.scale.setValueAtTime(${startTimeSec + 0.22}, [100, 115]);`,
    ].join("\n");
  }

  /**
   * Genera el fragmento ExtendScript para un Punch Zoom súbito en la capa de video.
   */
  public static generatePunchZoomSnippet(
    compVar: string,
    layerName: string,
    punchTimeSec: number,
    targetScalePct = 120
  ): string {
    return [
      `// === PUNCH ZOOM SÚBITO ===`,
      `var vLayer = ${compVar}.layer("${layerName}");`,
      `if (vLayer) {`,
      `  vLayer.transform.scale.setValueAtTime(${punchTimeSec - 0.04}, [100, 100]);`,
      `  vLayer.transform.scale.setValueAtTime(${punchTimeSec}, [${targetScalePct}, ${targetScalePct}]);`,
      `}`,
    ].join("\n");
  }
}
