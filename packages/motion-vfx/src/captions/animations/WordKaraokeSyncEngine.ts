import { RecognizedWord } from "../intelligence/SpeechRecognitionEngine.js";

export interface KaraokeStyleConfig {
  activeColor?: [number, number, number]; // default: amarillo dorado [1.0, 0.78, 0.10]
  inactiveColor?: [number, number, number]; // default: blanco [0.95, 0.95, 0.95]
  emphasisColor?: [number, number, number]; // default: rojo carmesí [1.0, 0.08, 0.14]
  fontSize?: number; // default: 110
  fontFamily?: string; // default: "Impact"
  activeScale?: number; // default: 125
}

/**
 * Motor de subtítulos dinámicos y animación palabra por palabra estilo TikTok / Reels Karaoke (Fase 5E / Mejoras).
 * Genera código ExtendScript y expresiones de sincronización temporal para resaltar palabras al ritmo de la voz.
 */
export class WordKaraokeSyncEngine {
  /**
   * Genera el fragmento ExtendScript para animar un grupo de palabras con efecto karaoke y pop-in inercial.
   */
  public static generateKaraokeSegmentSnippet(
    compVar: string,
    layerBaseName: string,
    words: RecognizedWord[],
    position: [number, number],
    config: KaraokeStyleConfig = {}
  ): string {
    if (words.length === 0) return "";

    const activeCol = config.activeColor ?? [1.0, 0.78, 0.10];
    const inactiveCol = config.inactiveColor ?? [0.95, 0.95, 0.95];
    const emphCol = config.emphasisColor ?? [1.0, 0.08, 0.14];
    const fontSize = config.fontSize ?? 110;
    const font = config.fontFamily ?? "Impact";

    const segStart = words[0].start;
    const segEnd = words[words.length - 1].end;
    const fullText = words.map((w) => w.word).join(" ");

    const snippetLines = [
      `// === VIRAL WORD KARAOKE SEGMENT (${layerBaseName}) ===`,
      `var txtLayer = ${compVar}.layers.addText("${fullText}");`,
      `txtLayer.name = "${layerBaseName}";`,
      `txtLayer.motionBlur = true;`,
      `txtLayer.startTime = ${segStart};`,
      `txtLayer.inPoint = ${segStart};`,
      `txtLayer.outPoint = ${segEnd + 0.15};`,
      `var tProp = txtLayer.property("Source Text");`,
      `var tDoc = tProp.value;`,
      `tDoc.fontSize = ${fontSize};`,
      `tDoc.fillColor = [${inactiveCol[0]}, ${inactiveCol[1]}, ${inactiveCol[2]}];`,
      `tDoc.justification = ParagraphJustification.CENTER_JUSTIFY;`,
      `tDoc.tracking = -10;`,
      `try { tDoc.font = "${font}"; } catch(fe) {}`,
      `tProp.setValue(tDoc);`,
      `txtLayer.transform.position.setValue([${position[0]}, ${position[1]}]);`,
    ];

    // Animación de escala Pop-In al inicio del segmento
    snippetLines.push(
      `txtLayer.transform.scale.setValueAtTime(${segStart}, [140, 160]);`,
      `txtLayer.transform.scale.setValueAtTime(${segStart + 0.18}, [100, 100]);`,
      `txtLayer.transform.scale.expression = "var n = 0; if (numKeys > 0) { n = nearestKey(time).index; if (key(n).time > time) n--; } if (n === 0) value; else { var t = time - key(n).time; var amp = 0.03; var freq = 8; var decay = 4.5; var v = velocityAtTime(key(n).time - thisComp.frameDuration/10); value + v * amp * Math.sin(freq * t * 2 * Math.PI) / Math.exp(decay * t); }";`
    );

    // Animador de color por rango de caracteres (Character Range Selector)
    snippetLines.push(
      `try {`,
      `  var animators = txtLayer.property("Text").property("Animators");`,
      `  var colAnim = animators.addProperty("ADBE Text Animator");`,
      `  colAnim.name = "Karaoke_Highlight";`,
      `  var fillProp = colAnim.property("ADBE Text Animator Properties").addProperty("ADBE Text Fill Color");`,
      `  fillProp.setValue([${activeCol[0]}, ${activeCol[1]}, ${activeCol[2]}]);`,
      `  var selector = colAnim.property("ADBE Text Selectors").addProperty("ADBE Text Selector");`,
      `  selector.property("Start").setValue(0);`,
      `  selector.property("End").setValue(100);`,
      `  selector.property("Offset").setValueAtTime(${segStart}, -100);`,
      `  selector.property("Offset").setValueAtTime(${segEnd}, 100);`,
      `} catch(ae) {}`
    );

    return snippetLines.join("\n");
  }
}
