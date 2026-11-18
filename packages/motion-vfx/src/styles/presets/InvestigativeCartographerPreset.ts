import { Composition } from "../../core/composition.js";

export interface MapCoordinates {
  latitude: number;
  longitude: number;
  label: string;
}

export interface DocumentCutoutConfig {
  id: string;
  headline: string;
  sourceDate: string;
  rotationDegrees?: number;
  pinLocation?: [number, number];
}

export interface RouteWaypoint {
  x: number;
  y: number;
  timeSec: number;
}

export interface CartographerSnippetResult {
  mapCameraSnippet: string;
  highlighterSnippet: string;
  routeTraceSnippet: string;
  documentCutoutSnippet: string;
}

/**
 * Motor Especializado del Preset #1: The Investigative Cartographer (Johnny Harris / Vox Style).
 * Genera composiciones 2.5D de mapas topográficos, recortes de documentos históricos,
 * resaltadores analógicos y trazado de rutas vectoriales animadas.
 */
export class InvestigativeCartographerPreset {
  public static readonly PALETTE = {
    paperKraft: [0.953, 0.922, 0.867] as [number, number, number], // #F3EBDD
    documentInk: [0.102, 0.102, 0.102] as [number, number, number], // #1A1A1A
    highlighterYellow: [1.0, 0.898, 0.0] as [number, number, number], // #FFE500
    conflictRed: [0.902, 0.224, 0.275] as [number, number, number], // #E63946
    oceanBlue: [0.165, 0.294, 0.486] as [number, number, number], // #2A4B7C
  };

  /**
   * Calcula la rotación pseudoaleatoria determinista para un documento según su ID/semilla.
   */
  public static calculateDeterministicRotation(seedStr: string): number {
    let hash = 0;
    for (let i = 0; i < seedStr.length; i++) {
      hash = (hash << 5) - hash + seedStr.charCodeAt(i);
      hash |= 0;
    }
    const normalized = (Math.abs(hash) % 1000) / 1000; // [0, 1]
    return Number((normalized * 6.0 - 3.0).toFixed(2)); // [-3.0°, +3.0°]
  }

  /**
   * Calcula la curva de escala con rebote inercial (Overshoot) para el impacto de una chincheta/pin.
   */
  public static calculatePinOvershootScale(t: number): number {
    if (t < 0) return 0;
    // S(t) = 100 + 45 * exp(-6t) * cos(18t)
    const scale = 100 + 45 * Math.exp(-6 * t) * Math.cos(18 * t);
    return Number(scale.toFixed(2));
  }

  /**
   * Genera el script ExtendScript para configurar la cámara 2.5D y el vuelo cartográfico.
   */
  public static generateMapCameraSnippet(
    compVar: string,
    targetPosition: [number, number] = [960, 540],
    zoomDurationSec = 4.0
  ): string {
    return [
      `// === 2.5D CARTOGRAPHIC CAMERA RIG ===`,
      `var cam = ${compVar}.layers.addCamera("Carto_Camera", [${targetPosition[0]}, ${targetPosition[1]}]);`,
      `cam.property("Position").setValue([${targetPosition[0]}, ${targetPosition[1]}, -1450]);`,
      `cam.property("Point of Interest").setValue([${targetPosition[0]}, ${targetPosition[1]}, 0]);`,
      `cam.property("X Rotation").setValue(32);`,
      `cam.property("Z Rotation").setValue(-12);`,
      `// Vuelo y Zoom In cinematográfico`,
      `var posProp = cam.property("Position");`,
      `posProp.setValueAtTime(0.0, [${targetPosition[0]}, ${targetPosition[1]} - 120, -1450]);`,
      `posProp.setValueAtTime(${zoomDurationSec}, [${targetPosition[0]}, ${targetPosition[1]}, -950]);`,
      `posProp.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER);`,
      `posProp.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER);`,
    ].join("\n");
  }

  /**
   * Genera el fragmento ExtendScript para un texto con resaltador analógico animado (Trim Paths detrás del texto).
   */
  public static generateHighlighterSnippet(
    compVar: string,
    layerName: string,
    text: string,
    position: [number, number],
    startTimeSec: number,
    durationSec = 1.2
  ): string {
    const pal = this.PALETTE;
    return [
      `// === ANALOG HIGHLIGHTER STROKE (${layerName}) ===`,
      `var textLayer = ${compVar}.layers.addText("${text}");`,
      `textLayer.name = "${layerName}_Text";`,
      `textLayer.transform.position.setValue([${position[0]}, ${position[1]}]);`,
      `var tProp = textLayer.property("Source Text");`,
      `var tDoc = tProp.value;`,
      `tDoc.fontSize = 58;`,
      `tDoc.font = "PlayfairDisplay-Bold";`,
      `tDoc.fillColor = [${pal.documentInk[0]}, ${pal.documentInk[1]}, ${pal.documentInk[2]}];`,
      `tDoc.tracking = -5;`,
      `tProp.setValue(tDoc);`,
      ``,
      `// Capa de Forma del Resaltador (Detrás del texto, modo Multiply)`,
      `var highlight = ${compVar}.layers.addShape();`,
      `highlight.name = "${layerName}_Highlight";`,
      `highlight.moveAfter(textLayer);`,
      `highlight.blendingMode = BlendingMode.MULTIPLY;`,
      `var shapeGroup = highlight.property("Contents").addProperty("ADBE Vector Group");`,
      `var stroke = shapeGroup.property("Contents").addProperty("ADBE Vector Graphic - Stroke");`,
      `stroke.property("Color").setValue([${pal.highlighterYellow[0]}, ${pal.highlighterYellow[1]}, ${pal.highlighterYellow[2]}, 0.75]);`,
      `stroke.property("Stroke Width").setValue(54);`,
      `var trim = shapeGroup.property("Contents").addProperty("ADBE Vector Filter - Trim");`,
      `trim.property("End").setValueAtTime(${startTimeSec}, 0);`,
      `trim.property("End").setValueAtTime(${startTimeSec + durationSec}, 100);`,
    ].join("\n");
  }

  /**
   * Genera el fragmento ExtendScript para trazar una ruta vectorial discontinua con avance progresivo.
   */
  public static generateRouteTraceSnippet(
    compVar: string,
    routeName: string,
    points: Array<[number, number]>,
    startTimeSec: number,
    durationSec = 2.5
  ): string {
    const pal = this.PALETTE;
    return [
      `// === ANIMATED ROUTE TRIM PATHS (${routeName}) ===`,
      `var routeLayer = ${compVar}.layers.addShape();`,
      `routeLayer.name = "${routeName}";`,
      `var rGroup = routeLayer.property("Contents").addProperty("ADBE Vector Group");`,
      `var rStroke = rGroup.property("Contents").addProperty("ADBE Vector Graphic - Stroke");`,
      `rStroke.property("Color").setValue([${pal.conflictRed[0]}, ${pal.conflictRed[1]}, ${pal.conflictRed[2]}]);`,
      `rStroke.property("Stroke Width").setValue(6);`,
      `rStroke.property("Line Cap").setValue(2); // Round Cap`,
      `var rDashes = rStroke.property("Dashes");`,
      `if (rDashes && rDashes.canAddProperty("ADBE Vector Dash - 1")) {`,
      `  rDashes.addProperty("ADBE Vector Dash - 1").setValue(14);`,
      `  rDashes.addProperty("ADBE Vector Dash - 2").setValue(8);`,
      `}`,
      `var rTrim = rGroup.property("Contents").addProperty("ADBE Vector Filter - Trim");`,
      `rTrim.property("End").setValueAtTime(${startTimeSec}, 0);`,
      `rTrim.property("End").setValueAtTime(${startTimeSec + durationSec}, 100);`,
    ].join("\n");
  }

  /**
   * Genera el fragmento ExtendScript para un recorte de periódico / documento histórico con chincheta.
   */
  public static generateDocumentCutoutSnippet(
    compVar: string,
    doc: DocumentCutoutConfig,
    position: [number, number],
    appearTimeSec: number
  ): string {
    const rot = doc.rotationDegrees ?? this.calculateDeterministicRotation(doc.id);
    const pal = this.PALETTE;
    return [
      `// === HISTORICAL DOCUMENT CUTOUT (${doc.id}) ===`,
      `var docLayer = ${compVar}.layers.addSolid([${pal.paperKraft[0]}, ${pal.paperKraft[1]}, ${pal.paperKraft[2]}], "${doc.id}", 640, 420, 1.0);`,
      `docLayer.transform.position.setValue([${position[0]}, ${position[1]}]);`,
      `docLayer.transform.rotation.setValue(${rot});`,
      `docLayer.inPoint = ${appearTimeSec};`,
      `// Drop Shadow`,
      `var ds = docLayer.property("Effects").addProperty("ADBE Drop Shadow");`,
      `ds.property("Opacity").setValue(35);`,
      `ds.property("Distance").setValue(12);`,
      `ds.property("Softness").setValue(25);`,
      `// Chincheta / Pin de fijación`,
      `var pinLayer = ${compVar}.layers.addShape();`,
      `pinLayer.name = "${doc.id}_Pin";`,
      `pinLayer.transform.position.setValue([${position[0]}, ${position[1]} - 190]);`,
      `pinLayer.transform.scale.setValueAtTime(${appearTimeSec}, [0, 0]);`,
      `pinLayer.transform.scale.setValueAtTime(${appearTimeSec + 0.12}, [145, 145]);`,
      `pinLayer.transform.scale.setValueAtTime(${appearTimeSec + 0.28}, [92, 92]);`,
      `pinLayer.transform.scale.setValueAtTime(${appearTimeSec + 0.40}, [100, 100]);`,
    ].join("\n");
  }
}
