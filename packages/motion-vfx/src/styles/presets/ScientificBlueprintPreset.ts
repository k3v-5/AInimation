export interface DimensionCalloutConfig {
  id: string;
  startPoint: [number, number];
  endPoint: [number, number];
  label: string;
}

export interface IsometricNode {
  x: number;
  y: number;
  label: string;
  connectionsTo?: number[]; // Índices a los que se conecta
}

/**
 * Motor Especializado del Preset #3: Scientific Blueprint & 3D Isometric (Veritasium / Kurzgesagt Style).
 * Genera cuadrículas isométricas milimétricas, cotas de medición vectorial, nodos conectados y resplandor científico.
 */
export class ScientificBlueprintPreset {
  public static readonly PALETTE = {
    blueprintNavy: [0.059, 0.09, 0.165] as [number, number, number], // #0F172A
    cyanNeon: [0.024, 0.714, 0.831] as [number, number, number], // #06B6D4
    gridBlue: [0.118, 0.176, 0.298] as [number, number, number], // #1E2D4C
    pureWhite: [1.0, 1.0, 1.0] as [number, number, number], // #FFFFFF
    laserOrange: [0.976, 0.451, 0.086] as [number, number, number], // #F97316
  };

  /**
   * Calcula la distancia euclidiana y ángulo entre dos puntos en el lienzo.
   */
  public static calculateDistanceAndAngle(
    p1: [number, number],
    p2: [number, number]
  ): { distance: number; angleDegrees: number; midpoint: [number, number] } {
    const dx = p2[0] - p1[0];
    const dy = p2[1] - p1[1];
    const distance = Number(Math.sqrt(dx * dx + dy * dy).toFixed(2));
    const angleDegrees = Number(((Math.atan2(dy, dx) * 180) / Math.PI).toFixed(2));
    const midpoint: [number, number] = [
      Number(((p1[0] + p2[0]) / 2).toFixed(1)),
      Number(((p1[1] + p2[1]) / 2).toFixed(1)),
    ];
    return { distance, angleDegrees, midpoint };
  }

  /**
   * Genera el fragmento ExtendScript para la cuadrícula milimétrica de fondo (Grid Blueprint).
   */
  public static generateBlueprintGridSnippet(compVar: string): string {
    const pal = this.PALETTE;
    return [
      `// === SCIENTIFIC BLUEPRINT BACKGROUND GRID ===`,
      `var bgSolid = ${compVar}.layers.addSolid([${pal.blueprintNavy[0]}, ${pal.blueprintNavy[1]}, ${pal.blueprintNavy[2]}], "Blueprint_Background", 1920, 1080, 1.0);`,
      `var gridEffect = bgSolid.property("Effects").addProperty("ADBE Grid");`,
      `if (gridEffect) {`,
      `  gridEffect.property("Size From").setValue(2); // Width Slider`,
      `  gridEffect.property("Width").setValue(60);`,
      `  gridEffect.property("Border").setValue(1.5);`,
      `  gridEffect.property("Color").setValue([${pal.gridBlue[0]}, ${pal.gridBlue[1]}, ${pal.gridBlue[2]}]);`,
      `  gridEffect.property("Opacity").setValue(0.4);`,
      `}`,
    ].join("\n");
  }

  /**
   * Genera el fragmento ExtendScript para una cota de medición vectorial animada con texto dinámico.
   */
  public static generateDimensionCalloutSnippet(
    compVar: string,
    config: DimensionCalloutConfig,
    startTimeSec: number,
    durationSec = 1.5
  ): string {
    const pal = this.PALETTE;
    const geom = this.calculateDistanceAndAngle(config.startPoint, config.endPoint);

    return [
      `// === DIMENSION CALLOUT (${config.id}) ===`,
      `var lineLayer = ${compVar}.layers.addShape();`,
      `lineLayer.name = "${config.id}_Ruler";`,
      `lineLayer.inPoint = ${startTimeSec};`,
      `var lGroup = lineLayer.property("Contents").addProperty("ADBE Vector Group");`,
      `var lStroke = lGroup.property("Contents").addProperty("ADBE Vector Graphic - Stroke");`,
      `lStroke.property("Color").setValue([${pal.cyanNeon[0]}, ${pal.cyanNeon[1]}, ${pal.cyanNeon[2]}]);`,
      `lStroke.property("Stroke Width").setValue(3);`,
      `var lTrim = lGroup.property("Contents").addProperty("ADBE Vector Filter - Trim");`,
      `lTrim.property("End").setValueAtTime(${startTimeSec}, 0);`,
      `lTrim.property("End").setValueAtTime(${startTimeSec + durationSec}, 100);`,
      `// Etiqueta de Texto con Distancia`,
      `var txt = ${compVar}.layers.addText("${config.label}");`,
      `txt.name = "${config.id}_Label";`,
      `txt.transform.position.setValue([${geom.midpoint[0]}, ${geom.midpoint[1]} - 25]);`,
      `txt.inPoint = ${startTimeSec + durationSec * 0.5};`,
      `var tProp = txt.property("Source Text");`,
      `var tDoc = tProp.value;`,
      `tDoc.fontSize = 28;`,
      `tDoc.font = "Inter-Bold";`,
      `tDoc.fillColor = [${pal.pureWhite[0]}, ${pal.pureWhite[1]}, ${pal.pureWhite[2]}];`,
      `tProp.setValue(tDoc);`,
    ].join("\n");
  }
}
