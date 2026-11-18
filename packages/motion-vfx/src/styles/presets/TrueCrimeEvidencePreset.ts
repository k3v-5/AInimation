export interface RedYarnConfig {
  id: string;
  pinA: [number, number];
  pinB: [number, number];
  sagPx?: number; // default: 16px de caída gravitatoria en el centro
}

export interface PolaroidCardConfig {
  id: string;
  imageLayerName: string;
  captionText: string;
  rotationDegrees?: number;
}

/**
 * Motor Especializado del Preset #9: True Crime & Cold Case Evidence Room.
 * Genera pizarras de investigación policial, fotos Polaroid con etiquetas mecanografiadas,
 * hilos rojos elásticos y sellos 'CLASSIFIED'.
 */
export class TrueCrimeEvidencePreset {
  public static readonly PALETTE = {
    corkboardBrown: [0.36, 0.25, 0.18] as [number, number, number], // #5C402E
    evidenceRed: [0.85, 0.12, 0.12] as [number, number, number], // #D91E1E
    polaroidWhite: [0.94, 0.93, 0.9] as [number, number, number], // #F0EDE6
    censoredBlack: [0.05, 0.05, 0.05] as [number, number, number], // #0D0D0D
    folderManila: [0.88, 0.78, 0.6] as [number, number, number], // #E0C799
  };

  /**
   * Genera el fragmento ExtendScript para un hilo rojo conectado entre dos chinchetas de evidencia.
   */
  public static generateRedYarnSnippet(
    compVar: string,
    config: RedYarnConfig,
    startTimeSec: number
  ): string {
    const pal = this.PALETTE;
    const midX = (config.pinA[0] + config.pinB[0]) / 2;
    const midY = (config.pinA[1] + config.pinB[1]) / 2 + (config.sagPx ?? 16);

    return [
      `// === TRUE CRIME RED YARN STRING (${config.id}) ===`,
      `var yarn = ${compVar}.layers.addShape();`,
      `yarn.name = "Yarn_${config.id}";`,
      `yarn.inPoint = ${startTimeSec};`,
      `var yGroup = yarn.property("Contents").addProperty("ADBE Vector Group");`,
      `var yStroke = yGroup.property("Contents").addProperty("ADBE Vector Graphic - Stroke");`,
      `yStroke.property("Color").setValue([${pal.evidenceRed[0]}, ${pal.evidenceRed[1]}, ${pal.evidenceRed[2]}]);`,
      `yStroke.property("Stroke Width").setValue(4);`,
      `yStroke.property("Line Cap").setValue(2);`,
      `// Drop Shadow sobre el corcho`,
      `var ds = yarn.property("Effects").addProperty("ADBE Drop Shadow");`,
      `ds.property("Opacity").setValue(40);`,
      `ds.property("Distance").setValue(8);`,
      `ds.property("Softness").setValue(12);`,
    ].join("\n");
  }

  /**
   * Genera el fragmento ExtendScript para un sello rojo de 'CLASSIFIED' estampado sobre documentos.
   */
  public static generateClassifiedStampSnippet(
    compVar: string,
    position: [number, number],
    stampTimeSec: number
  ): string {
    const pal = this.PALETTE;
    return [
      `// === CLASSIFIED EVIDENCE STAMP ===`,
      `var stamp = ${compVar}.layers.addText("TOP SECRET // CLASSIFIED");`,
      `stamp.name = "Classified_Stamp";`,
      `stamp.transform.position.setValue([${position[0]}, ${position[1]}]);`,
      `stamp.transform.rotation.setValue(-12);`,
      `stamp.inPoint = ${stampTimeSec};`,
      `var tProp = stamp.property("Source Text");`,
      `var tDoc = tProp.value;`,
      `tDoc.fontSize = 68;`,
      `tDoc.font = "Impact";`,
      `tDoc.fillColor = [${pal.evidenceRed[0]}, ${pal.evidenceRed[1]}, ${pal.evidenceRed[2]}];`,
      `tDoc.tracking = 15;`,
      `tProp.setValue(tDoc);`,
      `// Impacto de estampado con escala`,
      `stamp.transform.scale.setValueAtTime(${stampTimeSec}, [180, 180]);`,
      `stamp.transform.scale.setValueAtTime(${stampTimeSec + 0.08}, [100, 100]);`,
    ].join("\n");
  }
}
