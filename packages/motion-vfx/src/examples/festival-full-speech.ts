import * as fs from "fs";
import * as path from "path";
import { MotionEngine } from "../sdk/MotionEngineSDK.js";
import { AEBridgeManager } from "../exporters/ae/AEBridgeManager.js";

async function generateFullFestivalSpeechProduction() {
  console.log("\n==========================================================================");
  console.log("🔥 GENERANDO SPEECH COMPLETO EDITORIAL: 'EL ARTE DE DISFRUTAR LOS FESTIVALES'");
  console.log("   • Pacing dinámico y rápido (sin ralentizaciones)");
  console.log("   • Distribución espacial variada a lo largo de todo el video");
  console.log("   • Estilo: USER_DESIGN_PREFERENCES.md (TIME Poster Style #FF1424 + Blanco)");
  console.log("==========================================================================\n");

  const outputDir = path.resolve("./dist/festival_speech");
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const videoFilePath = "D:/Lap/Camera/20250405_214145.mp4";
  const bouncePunchy = JSON.stringify(AEBridgeManager.expressions.inertiaBounce(0.03, 8.0, 4.5));

  const fullExtendScript = `/**
 * =======================================================================
 * MOTION GRAPHICS ENGINE v3.0 — FULL SPEECH EDITORIAL POSTER PRODUCTION
 * Project: EL ARTE DE DISFRUTAR LOS FESTIVALES (FULL TIMELINE DYNAMIC PACING)
 * Style: TIME Editorial Poster (#FF1424 Crimson + FAFAFA White + Variable Layouts)
 * Video Source: "${videoFilePath}"
 * =======================================================================
 */

(function() {
  app.beginUndoGroup("Full Festival Speech Production");

  try {
    var project = app.project;

    // 1. IMPORTAR VIDEO REAL DEL USUARIO
    var videoFile = new File("${videoFilePath}");
    var hasVideo = videoFile.exists;
    var footage = null;

    if (hasVideo) {
      var importOptions = new ImportOptions(videoFile);
      footage = project.importFile(importOptions);
    }

    var compWidth = 1080;
    var compHeight = 1920;
    var compDuration = (footage && footage.duration > 0) ? footage.duration : 13.0;
    var compFps = (footage && footage.frameRate > 0) ? footage.frameRate : 60.0;

    var comp = project.items.addComp("FESTIVAL_FULL_SPEECH", compWidth, compHeight, 1.0, compDuration, compFps);
    comp.bgColor = [0.03, 0.03, 0.04];
    comp.motionBlur = true; // Activar desenfoque de movimiento nativo

    // Helper profesional para texto con soporte de alineación y posicionamiento dinámico
    function createDynamicPosterText(comp, name, text, fontSize, color, pos, inTime, outTime, tracking, verticalScale, inScale, justification) {
      var layer = comp.layers.addText(text);
      layer.name = name;
      layer.motionBlur = true;
      layer.inPoint = inTime;
      layer.outPoint = outTime;

      var textProp = layer.property("Source Text");
      var textDoc = textProp.value;
      textDoc.fontSize = fontSize;
      textDoc.fillColor = color;
      textDoc.justification = justification || ParagraphJustification.CENTER_JUSTIFY;
      textDoc.tracking = tracking || -10;

      // Fuentes display ultra-bold (Impact / Arial Black / Haettenschweiler)
      var fonts = ["Impact", "Arial-Black", "Haettenschweiler", "Anton", "Arial-BoldMT", "TrebuchetMS-Bold"];
      for (var f = 0; f < fonts.length; f++) {
        try {
          textDoc.font = fonts[f];
          break;
        } catch(e) {}
      }

      textProp.setValue(textDoc);
      layer.transform.position.setValue(pos);

      var vScale = verticalScale || 100;
      var baseScale = [100, vScale];
      var startScale = inScale ? [inScale[0], inScale[1] * (vScale / 100)] : [160, 160 * (vScale / 100)];

      // Animación de Entrada Rápida y Fluida (0.18s)
      layer.transform.scale.setValueAtTime(inTime, startScale);
      layer.transform.scale.setValueAtTime(inTime + 0.18, baseScale);
      layer.transform.scale.expression = ${bouncePunchy};

      // Animación de Salida Suave (Fade out de 0.12s)
      layer.transform.opacity.setValueAtTime(inTime, 100);
      layer.transform.opacity.setValueAtTime(outTime - 0.12, 100);
      layer.transform.opacity.setValueAtTime(outTime, 0);

      return layer;
    }

    // =======================================================================
    // 🎥 1. CAPA DE VIDEO REAL (AUTO-FIT Y ZOOM SUAVE)
    // =======================================================================
    if (footage) {
      var videoLayer = comp.layers.add(footage);
      videoLayer.name = "Footage_Background";
      videoLayer.transform.position.setValue([compWidth / 2, compHeight / 2]);
      var scaleX = (compWidth / footage.width) * 100;
      var scaleY = (compHeight / footage.height) * 100;
      var coverScale = Math.max(scaleX, scaleY);
      
      videoLayer.transform.scale.setValueAtTime(0, [coverScale, coverScale]);
      videoLayer.transform.scale.setValueAtTime(compDuration, [coverScale * 1.05, coverScale * 1.05]);
    }

    // =======================================================================
    // 🌌 2. DEGRADADO OSCURO DE CONTRASTE CINEMÁTICO
    // =======================================================================
    var darkOverlay = comp.layers.addSolid([0.02, 0.02, 0.04], "Contrast_Grade", compWidth, compHeight, 1.0, compDuration);
    darkOverlay.transform.opacity.setValue(40);

    // =======================================================================
    // 🎨 PALETA DE COLOR OFICIAL (USER_DESIGN_PREFERENCES.md)
    // =======================================================================
    var CRIMSON_RED = [1.0, 0.08, 0.14]; // #FF1424 Rojo Póster Impactante
    var PURE_WHITE  = [0.98, 0.98, 0.98];
    var MUTED_GRAY  = [0.75, 0.75, 0.80];

    // =======================================================================
    // ⏱️ 3. SPEECH EDITORIAL DINÁMICO CON VARIACIÓN ESPACIAL CONTINUA
    // =======================================================================

    // --- BLOQUE 1: HOOK INICIAL (0.2s - 1.2s) [Centro Superior] ---
    createDynamicPosterText(
      comp, "Hook_Tag", "✦ MANIFIESTO FESTIVAL ✦", 28, CRIMSON_RED,
      [540, 540], 0.2, 1.2, 35, 100, [100, 100]
    );
    createDynamicPosterText(
      comp, "W1_EL_ARTE", "EL ARTE", 170, PURE_WHITE,
      [540, 720], 0.2, 1.2, -15, 130, [180, 234]
    );

    // --- BLOQUE 2: CONECTOR (1.2s - 1.7s) [Centro] ---
    createDynamicPosterText(
      comp, "W2_DE", "DE", 130, PURE_WHITE,
      [540, 740], 1.2, 1.7, 0, 110, [70, 77]
    );

    // --- BLOQUE 3: HERO SLAM (1.7s - 2.9s) [Centro Completo - Rojo Masivo] ---
    createDynamicPosterText(
      comp, "W3_DISFRUTAR", "DISFRUTAR", 240, CRIMSON_RED,
      [540, 760], 1.7, 2.9, -18, 150, [230, 345]
    );
    createDynamicPosterText(
      comp, "W3_Sub", "EN SU MÁXIMA EXPRESIÓN", 36, PURE_WHITE,
      [540, 1040], 1.85, 2.9, 20, 100, [100, 100]
    );

    // Shockwave ligero y optimizado al entrar "DISFRUTAR"
    var sw1 = comp.layers.addShape();
    sw1.name = "Shockwave_Disfrutar";
    sw1.inPoint = 1.7; sw1.outPoint = 2.4;
    var sw1Group = sw1.property("Contents").addProperty("ADBE Vector Group");
    var sw1Circ = sw1Group.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
    sw1Circ.property("Size").setValue([400, 400]);
    var sw1Stroke = sw1Group.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
    sw1Stroke.property("Color").setValue(CRIMSON_RED);
    sw1Stroke.property("Stroke Width").setValue(5.0);
    sw1.transform.position.setValue([540, 760]);
    sw1.transform.scale.setValueAtTime(1.7, [10, 10]);
    sw1.transform.scale.setValueAtTime(2.3, [260, 260]);
    sw1.transform.opacity.setValueAtTime(1.7, 100);
    sw1.transform.opacity.setValueAtTime(2.3, 0);

    // --- BLOQUE 4: CONECTOR (2.9s - 3.4s) [Centro] ---
    createDynamicPosterText(
      comp, "W4_LOS", "LOS", 140, PURE_WHITE,
      [540, 740], 2.9, 3.4, 0, 115, [140, 161]
    );

    // --- BLOQUE 5: SLAM FESTIVALES (3.4s - 4.6s) [Centro Inferior] ---
    createDynamicPosterText(
      comp, "W5_FESTIVALES", "FESTIVALES", 210, CRIMSON_RED,
      [540, 760], 3.4, 4.6, -15, 140, [240, 336]
    );

    // --- BLOQUE 6: CAMBIO DE LAYOUT -> SUPERIOR IZQUIERDA (4.6s - 5.8s) ---
    // Badge y texto alineados a la izquierda para dinamismo visual
    createDynamicPosterText(
      comp, "W6_Tag", "[ 02 // LA REALIDAD ]", 26, MUTED_GRAY,
      [540, 480], 4.6, 5.8, 25, 100, [100, 100]
    );
    createDynamicPosterText(
      comp, "W6_NO_ES_SOLO", "NO ES SOLO", 150, PURE_WHITE,
      [540, 680], 4.6, 5.8, -12, 125, [180, 225]
    );

    // --- BLOQUE 7: LAYOUT CENTRADO CON ROJO Y BLANCO (5.8s - 7.0s) ---
    createDynamicPosterText(
      comp, "W7_LA_MUSICA", "LA MÚSICA", 180, CRIMSON_RED,
      [540, 740], 5.8, 7.0, -15, 140, [220, 308]
    );
    createDynamicPosterText(
      comp, "W7_Sub", "ES LO QUE SIENTES DENTRO", 34, PURE_WHITE,
      [540, 980], 6.0, 7.0, 15, 100, [100, 100]
    );

    // --- BLOQUE 8: CAMBIO DE LAYOUT -> GIGANTE "LA ENERGÍA" (7.0s - 8.4s) ---
    createDynamicPosterText(
      comp, "W8_ES_LA", "ES LA", 110, PURE_WHITE,
      [540, 580], 7.0, 8.4, 10, 110, [100, 110]
    );
    createDynamicPosterText(
      comp, "W8_ENERGIA", "ENERGÍA", 230, CRIMSON_RED,
      [540, 780], 7.0, 8.4, -18, 150, [240, 360]
    );

    // Línea de acento horizontal inferior
    var accLine1 = comp.layers.addShape();
    accLine1.name = "Accent_Line_Energia";
    accLine1.inPoint = 7.0; accLine1.outPoint = 8.4;
    var al1Group = accLine1.property("Contents").addProperty("ADBE Vector Group");
    var al1Rect = al1Group.property("Contents").addProperty("ADBE Vector Shape - Rect");
    al1Rect.property("Size").setValue([780, 4]);
    var al1Fill = al1Group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
    al1Fill.property("Color").setValue(CRIMSON_RED);
    accLine1.transform.position.setValue([540, 1000]);
    accLine1.transform.scale.setValueAtTime(7.0, [0, 100]);
    accLine1.transform.scale.setValueAtTime(7.25, [100, 100]);

    // --- BLOQUE 9: POSICIÓN INFERIOR / LOWER CALLOUT (8.4s - 9.8s) ---
    createDynamicPosterText(
      comp, "W9_Tag", "✦ MOMENTO PRESENTE ✦", 28, CRIMSON_RED,
      [540, 1160], 8.4, 9.8, 30, 100, [100, 100]
    );
    createDynamicPosterText(
      comp, "W9_CONECTAR", "CONECTAR", 180, PURE_WHITE,
      [540, 1340], 8.4, 9.8, -15, 130, [190, 247]
    );

    // --- BLOQUE 10: CLÍMAX FINAL EDITORIAL SLAM (9.8s - 12.0s) ---
    createDynamicPosterText(
      comp, "W10_VIVELO", "VÍVELO", 150, PURE_WHITE,
      [540, 620], 9.8, 12.0, -10, 120, [180, 216]
    );
    createDynamicPosterText(
      comp, "W10_AL_MAXIMO", "AL MÁXIMO", 220, CRIMSON_RED,
      [540, 840], 9.8, 12.0, -18, 150, [250, 375]
    );
    createDynamicPosterText(
      comp, "W10_Final_Badge", "[ VIVE LA EXPERIENCIA // 2026 ]", 36, PURE_WHITE,
      [540, 1120], 10.0, 12.0, 25, 100, [100, 100]
    );

    // =======================================================================
    // 4. APERTURA AUTOMÁTICA EN VISOR DE AFTER EFFECTS
    // =======================================================================
    comp.openInViewer();

  } catch (err) {
    alert("Error en script de Full Speech Editorial: " + err.toString());
  } finally {
    app.endUndoGroup();
  }
})();
`;

  const jsxFilePath = path.join(outputDir, "Festival_Full_Speech.jsx");
  fs.writeFileSync(jsxFilePath, fullExtendScript, "utf-8");
  console.log(`   ✔ Archivo JSX con Speech Completo y Layouts Dinámicos generado -> ${jsxFilePath}`);
}

generateFullFestivalSpeechProduction().catch(console.error);
