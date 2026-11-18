export interface HighlighterConfig {
  width: number;
  height: number;
  color?: [number, number, number]; // [r, g, b] normalizado [0, 1] (default: amarillo neón [1.0, 0.9, 0.2])
  opacity?: number; // default: 85
  roundness?: number; // default: 12
  angleDeg?: number; // default: -2.0 (ligera inclinación natural de marcador)
}

export interface TapeStickerConfig {
  width?: number; // default: 140
  height?: number; // default: 45
  color?: [number, number, number]; // default: blanco translúcido [0.95, 0.95, 0.90]
  opacity?: number; // default: 75
  rotationDeg?: number; // default: 8.0
}

export interface CamcorderHUDConfig {
  title?: string;
  showThirdsGrid?: boolean;
  showBattery?: boolean;
  showRecBlink?: boolean;
  color?: [number, number, number];
}

/**
 * Librería de elementos gráficos y overlays estéticos virales estilo TikTok / Reels (Fase 5J / Mejoras).
 * Genera código ExtendScript y definiciones vectoriales para resaltadores animados, stickers de cinta,
 * visores retro de cámara y rasgados de papel.
 */
export class AestheticElementsLibrary {
  /**
   * Genera el código ExtendScript para un subrayado de marcador resaltador animado (Animated Highlighter).
   */
  public static generateHighlighterSnippet(
    compVar: string,
    layerName: string,
    position: [number, number],
    inTime: number,
    duration = 0.35,
    config: HighlighterConfig = { width: 320, height: 48 }
  ): string {
    const col = config.color ?? [1.0, 0.88, 0.15]; // Amarillo flúor
    const op = config.opacity ?? 80;
    const w = config.width;
    const h = config.height;
    const r = config.roundness ?? 10;
    const rot = config.angleDeg ?? -2.0;

    return [
      `// === ANIMATED HIGHLIGHTER MARKER (${layerName}) ===`,
      `var hl = ${compVar}.layers.addShape();`,
      `hl.name = "${layerName}";`,
      `hl.startTime = ${inTime};`,
      `hl.inPoint = ${inTime};`,
      `hl.outPoint = ${inTime + duration + 5.0};`,
      `hl.motionBlur = true;`,
      `var hlContents = hl.property("Contents");`,
      `var hlGroup = hlContents.addProperty("ADBE Vector Group");`,
      `var hlShape = hlGroup.property("Contents").addProperty("ADBE Vector Shape - Rect");`,
      `hlShape.property("Size").setValue([${w}, ${h}]);`,
      `hlShape.property("Roundness").setValue(${r});`,
      `var hlFill = hlGroup.property("Contents").addProperty("ADBE Vector Graphic - Fill");`,
      `hlFill.property("Color").setValue([${col[0]}, ${col[1]}, ${col[2]}]);`,
      `hl.transform.position.setValue([${position[0]}, ${position[1]}]);`,
      `hl.transform.rotation.setValue(${rot});`,
      `hl.transform.opacity.setValue(${op});`,
      `hl.blendingMode = BlendingMode.MULTIPLY;`,
      `hl.transform.scale.setValueAtTime(${inTime}, [0, 100]);`,
      `hl.transform.scale.setValueAtTime(${inTime + duration}, [100, 100]);`,
    ].join("\n");
  }

  /**
   * Genera el código ExtendScript para un sticker de cinta adhesiva (Tape Sticker Overlay).
   */
  public static generateTapeStickerSnippet(
    compVar: string,
    layerName: string,
    position: [number, number],
    inTime: number,
    outTime: number,
    config: TapeStickerConfig = {}
  ): string {
    const w = config.width ?? 150;
    const h = config.height ?? 42;
    const col = config.color ?? [0.96, 0.95, 0.90];
    const op = config.opacity ?? 70;
    const rot = config.rotationDeg ?? 6.5;

    return [
      `// === TAPE STICKER OVERLAY (${layerName}) ===`,
      `var tape = ${compVar}.layers.addShape();`,
      `tape.name = "${layerName}";`,
      `tape.startTime = ${inTime};`,
      `tape.inPoint = ${inTime};`,
      `tape.outPoint = ${outTime};`,
      `var tapeContents = tape.property("Contents");`,
      `var tapeGroup = tapeContents.addProperty("ADBE Vector Group");`,
      `var tapeRect = tapeGroup.property("Contents").addProperty("ADBE Vector Shape - Rect");`,
      `tapeRect.property("Size").setValue([${w}, ${h}]);`,
      `tapeRect.property("Roundness").setValue(4);`,
      `var tapeFill = tapeGroup.property("Contents").addProperty("ADBE Vector Graphic - Fill");`,
      `tapeFill.property("Color").setValue([${col[0]}, ${col[1]}, ${col[2]}]);`,
      `tape.transform.position.setValue([${position[0]}, ${position[1]}]);`,
      `tape.transform.rotation.setValue(${rot});`,
      `tape.transform.opacity.setValue(${op});`,
    ].join("\n");
  }

  /**
   * Genera el código ExtendScript para un HUD retro de cámara con visor (Camcorder Viewfinder).
   */
  public static generateCamcorderHUDSnippet(
    compVar: string,
    compWidth: number,
    compHeight: number,
    inTime: number,
    outTime: number,
    config: CamcorderHUDConfig = {}
  ): string {
    const title = config.title ?? "LIVE // 4K 60FPS";
    const col = config.color ?? [0.92, 0.95, 1.0];

    return [
      `// === CAMCORDER RETRO VIEWFINDER HUD ===`,
      `// 1. Indicador REC parpadeante`,
      `var recText = ${compVar}.layers.addText("● REC");`,
      `recText.name = "HUD_REC_Indicator";`,
      `recText.startTime = ${inTime};`,
      `recText.inPoint = ${inTime};`,
      `recText.outPoint = ${outTime};`,
      `var recDoc = recText.property("Source Text").value;`,
      `recDoc.fontSize = 26;`,
      `recDoc.fillColor = [1.0, 0.1, 0.15];`,
      `recText.property("Source Text").setValue(recDoc);`,
      `recText.transform.position.setValue([120, 160]);`,
      `recText.transform.opacity.expression = "Math.floor(time * 2) % 2 === 0 ? 100 : 0;";`,
      `// 2. Metadata y Timecode`,
      `var metaText = ${compVar}.layers.addText("${title}");`,
      `metaText.name = "HUD_Meta_Header";`,
      `metaText.startTime = ${inTime};`,
      `metaText.inPoint = ${inTime};`,
      `metaText.outPoint = ${outTime};`,
      `var metaDoc = metaText.property("Source Text").value;`,
      `metaDoc.fontSize = 20;`,
      `metaDoc.fillColor = [${col[0]}, ${col[1]}, ${col[2]}];`,
      `metaDoc.tracking = 20;`,
      `metaText.property("Source Text").setValue(metaDoc);`,
      `metaText.transform.position.setValue([${compWidth - 280}, 160]);`,
    ].join("\n");
  }
}
