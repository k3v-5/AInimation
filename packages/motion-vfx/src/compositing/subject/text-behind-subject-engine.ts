import crypto from "crypto";
import {
  SubjectCompositingPlan,
  SubjectCompositingPlanSchema,
  TextBehindSubjectConfig,
  TextBehindSubjectConfigSchema,
} from "./detection-types.js";
import { ObjectDetectionEngine } from "./object-detection-engine.js";

/**
 * Motor de composición de texto y gráficos detrás de personas (Depth Layering Sandwich).
 */
export class TextBehindSubjectEngine {
  /**
   * Compila un plan de composición para insertar texto detrás del sujeto.
   */
  public static compile(configInput: TextBehindSubjectConfig): SubjectCompositingPlan {
    const config = TextBehindSubjectConfigSchema.parse(configInput);

    // Detección del sujeto (o generación procedural si no se proporcionó)
    const subject =
      config.detectedSubject ??
      ObjectDetectionEngine.createProceduralPersonDetection({
        frameIndex: 0,
        timestampSeconds: config.inTimeSeconds,
        compWidth: 1920,
        compHeight: 1080,
        zone: "CENTER",
      });

    const extendScriptLines = this.generateExtendScript(config, subject);

    const hashContent = JSON.stringify({
      type: "TEXT_BEHIND_SUBJECT",
      sourceAssetPath: config.sourceAssetPath,
      text: config.text,
      typography: config.typography,
      featherPx: config.featherPx,
      blurPx: config.backgroundBlurPx,
      duration: config.outTimeSeconds - config.inTimeSeconds,
    });
    const checksumSha256 = crypto.createHash("sha256").update(hashContent).digest("hex");

    return SubjectCompositingPlanSchema.parse({
      id: `plan_text_behind_${config.id}`,
      type: "TEXT_BEHIND_SUBJECT",
      totalDurationSeconds: config.outTimeSeconds - config.inTimeSeconds,
      layersCount: 3, // [Fondo, Texto, Sujeto Cutout]
      extendScriptLines,
      checksumSha256,
    });
  }

  /**
   * Genera el código ExtendScript nativo para After Effects que arma el Depth Sandwich.
   */
  public static generateExtendScript(
    config: TextBehindSubjectConfig,
    subject: any
  ): string[] {
    const assetPathNorm = config.sourceAssetPath.replace(/\\/g, "/");
    const dur = (config.outTimeSeconds - config.inTimeSeconds).toFixed(3);
    const inT = config.inTimeSeconds.toFixed(3);
    const outT = config.outTimeSeconds.toFixed(3);

    // Extraer vértices del contorno o bounding box para la máscara Bezier
    let verticesStr = "[]";
    if (subject.contourPoints && subject.contourPoints.length >= 3) {
      verticesStr = JSON.stringify(subject.contourPoints.map((p: any) => [Math.round(p.x), Math.round(p.y)]));
    } else {
      const b = subject.boundingBox;
      verticesStr = JSON.stringify([
        [Math.round(b.x), Math.round(b.y)],
        [Math.round(b.x + b.width), Math.round(b.y)],
        [Math.round(b.x + b.width), Math.round(b.y + b.height)],
        [Math.round(b.x), Math.round(b.y + b.height)],
      ]);
    }

    const lines: string[] = [
      "// ============================================================================",
      "//  DEPTH LAYER SANDWICH: TEXT BEHIND SUBJECT (TIME EDITORIAL STYLE)",
      `//  Subject Track: ${subject.trackId} | Confidence: ${subject.confidence}`,
      "// ============================================================================",
      "",
      `app.beginUndoGroup('Build Text Behind Subject: ${config.id}');`,
      "try {",
      "  var project = app.project || app.newProject();",
      `  var footageFile = new File('${assetPathNorm}');`,
      "  if (!footageFile.exists) footageFile = new File(footageBase + '/' + '" + assetPathNorm.split("/").pop() + "');",
      "  var importedFootage = null;",
      "  if (footageFile.exists) {",
      "    importedFootage = project.importFile(new ImportOptions(footageFile));",
      "  }",
      "",
      `  var compW = 1080; var compH = 1920;`,
      `  var mainComp = project.items.addComp('Text Behind Subject - ${config.id}', compW, compH, 1.0, ${dur}, 30.0);`,
      "  mainComp.bgColor = [0.03, 0.03, 0.04];",
      "  mainComp.motionBlur = true; // Invariante obligatoria",
      "",
      "  // 1. CAPA INFERIOR: FONDO COMPLETO (Background)",
      "  var bgLayer = null;",
      "  if (importedFootage) {",
      "    bgLayer = mainComp.layers.add(importedFootage);",
      "    bgLayer.name = '[BG] Background Video';",
      `    bgLayer.startTime = ${inT}; bgLayer.inPoint = ${inT}; bgLayer.outPoint = ${outT};`,
      "    bgLayer.motionBlur = true;",
      "    bgLayer.property('Transform').property('Position').setValue([compW / 2, compH / 2]);",
      "    var bgScale = Math.max((compW / importedFootage.width), (compH / importedFootage.height)) * 100.0;",
      "    bgLayer.property('Transform').property('Scale').setValue([bgScale, bgScale]);",
    ];

    if (config.backgroundBlurPx > 0) {
      lines.push("    // Desenfoque de profundidad sutil (Depth bokeh)");
      lines.push("    var blurFx = bgLayer.property('Effects').addProperty('ADBE Fast Blur');");
      lines.push(`    blurFx.property('Blurriness').setValue(${config.backgroundBlurPx});`);
      lines.push("    blurFx.property('Repeat Edge Pixels').setValue(true);");
    }

    lines.push(
      "  }",
      "",
      "  // 2. CAPA INTERMEDIA: TEXTO EDITORIAL TIME STYLE",
      `  var textLayer = mainComp.layers.addText('${config.text.replace(/'/g, "\\'")}');`,
      "  textLayer.name = '[TEXT] Behind Subject';",
      `  textLayer.startTime = ${inT}; textLayer.inPoint = ${inT}; textLayer.outPoint = ${outT};`,
      "  textLayer.motionBlur = true;",
      `  textLayer.property('Transform').property('Position').setValue([${config.position.x}, ${config.position.y}]);`,
      "  var textDoc = textLayer.property('Source Text').value;",
      `  textDoc.fontSize = ${config.typography.fontSize};`,
      "  textDoc.fillColor = [1.0, 0.08, 0.14]; // Crimson #FF1424",
      "  textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;",
      "  textLayer.property('Source Text').setValue(textDoc);",
      `  // Estiramiento vertical TIME (130%)`,
      `  textLayer.property('Transform').property('Scale').setValue([100.0, ${config.typography.verticalStretchPercent}.0]);`,
      "",
      "  // 3. CAPA SUPERIOR: SUJETO EN PRIMER PLANO (Foreground Cutout con Máscara Bezier)",
      "  var fgLayer = null;",
      "  if (importedFootage) {",
      "    fgLayer = mainComp.layers.add(importedFootage);",
      "    fgLayer.name = '[FG CUTOUT] Foreground Subject';",
      `    fgLayer.startTime = ${inT}; fgLayer.inPoint = ${inT}; fgLayer.outPoint = ${outT};`,
      "    fgLayer.audioEnabled = false; // Evitar doblar audio",
      "    fgLayer.motionBlur = true;",
      "    fgLayer.property('Transform').property('Position').setValue([compW / 2, compH / 2]);",
      "    var fgScale = Math.max((compW / importedFootage.width), (compH / importedFootage.height)) * 100.0;",
      "    fgLayer.property('Transform').property('Scale').setValue([fgScale, fgScale]);",
      "",
      "    // Aplicar Máscara Bezier para recortar al sujeto",
      "    var mask = fgLayer.property('Masks').addProperty('Mask');",
      "    mask.maskMode = MaskMode.ROTO_BEZIER || MaskMode.ADD;",
      "    var shape = mask.property('maskShape').value;",
      `    shape.vertices = ${verticesStr};`,
      "    shape.closed = true;",
      "    mask.property('maskShape').setValue(shape);",
      `    mask.property('maskFeather').setValue([${config.featherPx}, ${config.featherPx}]);`,
      "  }",
      "",
      "  app.endUndoGroup();",
      "  alert('¡Composición Text Behind Subject generada con éxito!');",
      "} catch(e) {",
      "  app.endUndoGroup();",
      "  alert('Error al generar Text Behind Subject: ' + e.toString());",
      "}"
    );

    return lines;
  }
}
