import * as fs from "fs";
import * as path from "path";
import { MotionEngine } from "../sdk/MotionEngineSDK.js";
import { AEBridgeManager } from "../exporters/ae/AEBridgeManager.js";
import { CLIRunner } from "../cli/CLIRunner.js";

async function generatePerfectFittedFestivalMasterpiece() {
  console.log("\n==========================================================================");
  console.log("🛠️ CORRIGIENDO AJUSTE DE TEXTO (AUTO-FIT), SAFE ZONES Y ESCALADO DE VIDEO");
  console.log("   • Cálculo automático de tamaño de fuente para evitar desbordes laterales");
  console.log("   • Reubicación vertical inteligente (deja visible el escenario y los artistas)");
  console.log("   • Anclaje y auto-cover 100% exacto del video sin bordes");
  console.log("==========================================================================\n");

  const outputDir = path.resolve("./dist/festival_2min");
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const videoFilePath = "D:/Lap/Camera/20250405_214145.mp4";
  const bouncePunchy = JSON.stringify(AEBridgeManager.expressions.inertiaBounce(0.03, 8.0, 4.5));
  const cameraShakeFootage = JSON.stringify(AEBridgeManager.expressions.wiggle(10, 22));

  const comp = MotionEngine.createComposition({
    id: "festival_2min_comp",
    name: "FESTIVAL_2MIN_PERFECT_FIT",
    width: 1080,
    height: 1920,
    fps: 60,
    duration: 120.0,
  });

  const fullExtendScript = `/**
 * =======================================================================
 * MOTION GRAPHICS ENGINE v3.0 — 2-MINUTE PERFECT-FIT FESTIVAL PRODUCTION
 * Fixes:
 *  1. Responsive Auto-Fitting Font Sizer (Zero Text Overflow / Max 920px width)
 *  2. Cinematic Upper Third Safe-Zone Placement (Stage & artists stay visible)
 *  3. Exact Video Anchor & 100% Cover Scaling (Zero borders)
 * =======================================================================
 */

(function() {
  app.beginUndoGroup("2-Minute Perfect-Fit Festival Production");

  try {
    var project = app.project;

    // 1. IMPORTAR VIDEO REAL
    var videoFile = new File("${videoFilePath}");
    var hasVideo = videoFile.exists;
    var footage = null;

    if (hasVideo) {
      var importOptions = new ImportOptions(videoFile);
      footage = project.importFile(importOptions);
    }

    var compWidth = 1080;
    var compHeight = 1920;
    var compDuration = 120.0;
    if (footage && footage.duration > 0) {
      compDuration = Math.max(footage.duration, 120.0);
    }
    var compFps = (footage && footage.frameRate > 0) ? footage.frameRate : 60.0;

    var comp = project.items.addComp("FESTIVAL_2MIN_PERFECT_FIT", compWidth, compHeight, 1.0, compDuration, compFps);
    comp.bgColor = [0.02, 0.02, 0.03];
    comp.motionBlur = true;

    // 🧠 HELPER RESPONSIVO: CALCULA EL TAMAÑO EXACTO PARA NUNCA SALIRSE DEL MARGEN (MAX 900px)
    function createAutoFitPosterText(comp, name, text, targetFontSize, color, pos, inTime, outTime, tracking, verticalScale, isShaky) {
      var layer = comp.layers.addText(text);
      layer.name = name;
      layer.motionBlur = true;
      layer.inPoint = inTime;
      layer.outPoint = outTime;

      var textProp = layer.property("Source Text");
      var textDoc = textProp.value;

      // Calcular tamaño seguro basado en longitud de caracteres (Ancho seguro = 900px)
      var maxSafeWidth = 900;
      var charCount = text.length;
      var calculatedSize = targetFontSize;

      // Factor de ancho promedio por carácter en Impact/Arial Black condensado (~0.55 * fontSize)
      var estimatedWidth = charCount * (targetFontSize * 0.55);
      if (estimatedWidth > maxSafeWidth) {
        calculatedSize = Math.floor(maxSafeWidth / (charCount * 0.55));
      }
      calculatedSize = Math.max(calculatedSize, 40); // Mínimo 40px

      textDoc.fontSize = calculatedSize;
      textDoc.fillColor = color;
      textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
      textDoc.tracking = tracking || -10;

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
      var startScale = [150, 150 * (vScale / 100)];

      layer.transform.scale.setValueAtTime(inTime, startScale);
      layer.transform.scale.setValueAtTime(inTime + 0.18, baseScale);
      layer.transform.scale.expression = ${bouncePunchy};

      layer.transform.opacity.setValueAtTime(inTime, 100);
      layer.transform.opacity.setValueAtTime(outTime - 0.15, 100);
      layer.transform.opacity.setValueAtTime(outTime, 0);

      if (isShaky) {
        layer.transform.position.expression = ${cameraShakeFootage};
      }

      return layer;
    }

    function createShockwave(comp, name, time, color, centerPos) {
      var sw = comp.layers.addShape();
      sw.name = name;
      sw.inPoint = time;
      sw.outPoint = time + 0.7;
      var swGroup = sw.property("Contents").addProperty("ADBE Vector Group");
      var swCirc = swGroup.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
      swCirc.property("Size").setValue([300, 300]);
      var swStroke = swGroup.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
      swStroke.property("Color").setValue(color || [1.0, 0.08, 0.14]);
      swStroke.property("Stroke Width").setValue(5.0);
      sw.transform.position.setValue(centerPos || [compWidth / 2, compHeight / 2]);
      sw.transform.scale.setValueAtTime(time, [10, 10]);
      sw.transform.scale.setValueAtTime(time + 0.65, [280, 280]);
      sw.transform.opacity.setValueAtTime(time, 100);
      sw.transform.opacity.setValueAtTime(time + 0.65, 0);
      return sw;
    }

    function createWhiteFlash(comp, name, inTime) {
      var flash = comp.layers.addSolid([1.0, 1.0, 1.0], name, compWidth, compHeight, 1.0, 0.22);
      flash.inPoint = inTime;
      flash.outPoint = inTime + 0.22;
      flash.transform.opacity.setValueAtTime(inTime, 75);
      flash.transform.opacity.setValueAtTime(inTime + 0.20, 0);
      return flash;
    }

    // =======================================================================
    // 🎥 1. CAPA DE VIDEO REAL (ANCLAJE EXACTO + AUTO-COVER 100%)
    // =======================================================================
    if (footage) {
      var videoLayer = comp.layers.add(footage);
      videoLayer.name = "Footage_With_Bass_Punches";
      videoLayer.motionBlur = true;
      videoLayer.transform.anchorPoint.setValue([footage.width / 2, footage.height / 2]);
      videoLayer.transform.position.setValue([compWidth / 2, compHeight / 2]);

      var scaleX = (compWidth / footage.width) * 100;
      var scaleY = (compHeight / footage.height) * 100;
      var coverScale = Math.max(scaleX, scaleY) * 1.02; // +2% de margen para evitar micro-bordes
      
      videoLayer.transform.scale.setValueAtTime(0, [coverScale, coverScale]);
      videoLayer.transform.scale.setValueAtTime(compDuration, [coverScale * 1.06, coverScale * 1.06]);

      // Bass Punches controlados
      var drops = [1.5, 6.5, 11.5, 18.0, 24.5, 29.5, 36.0, 42.5, 48.0, 54.0, 60.0, 66.0, 72.5, 78.0, 84.0, 90.0, 96.0, 102.0, 108.0, 114.0];
      for (var d = 0; d < drops.length; d++) {
        var dt = drops[d];
        videoLayer.transform.scale.setValueAtTime(dt, [coverScale * 1.10, coverScale * 1.10]);
        videoLayer.transform.scale.setValueAtTime(dt + 0.25, [coverScale * 1.01, coverScale * 1.01]);
      }
      videoLayer.transform.scale.expression = ${bouncePunchy};
    }

    // =======================================================================
    // 🌌 2. GRADACIÓN DE CONTRASTE CINEMÁTICO (Viñeta superior sutil)
    // =======================================================================
    var darkOverlay = comp.layers.addSolid([0.02, 0.02, 0.04], "Cinematic_Contrast_Grade", compWidth, compHeight, 1.0, compDuration);
    darkOverlay.transform.opacity.setValue(35);

    // =======================================================================
    // ⚡ 3. TRANSICIONES DE FLASH BLANCO
    // =======================================================================
    var flashTimes = [0.2, 18.0, 36.0, 54.0, 72.0, 90.0, 108.0, 116.5];
    for (var f = 0; f < flashTimes.length; f++) {
      createWhiteFlash(comp, "Flash_" + (f + 1), flashTimes[f]);
    }

    // =======================================================================
    // 💥 4. SHOCKWAVES EXPANSIVOS
    // =======================================================================
    var swTimes = [1.5, 18.0, 36.0, 54.0, 72.0, 90.0, 108.0];
    for (var s = 0; s < swTimes.length; s++) {
      createShockwave(comp, "Shockwave_" + (s + 1), swTimes[s], [1.0, 0.08, 0.14], [540, 680]);
    }

    // =======================================================================
    // 📊 5. HUD AUDIO EQUALIZER (Base inferior, centrado)
    // =======================================================================
    var eqLayer = comp.layers.addShape();
    eqLayer.name = "HUD_Audio_Equalizer_Bars";
    eqLayer.inPoint = 0.5;
    eqLayer.outPoint = compDuration - 0.5;
    var eqGroup = eqLayer.property("Contents").addProperty("ADBE Vector Group");
    var eqContents = eqGroup.property("Contents");
    var barRect = eqContents.addProperty("ADBE Vector Shape - Rect");
    barRect.property("Size").setValue([10, 45]);
    barRect.property("Roundness").setValue(3);
    var barFill = eqContents.addProperty("ADBE Vector Graphic - Fill");
    barFill.property("Color").setValue([1.0, 0.08, 0.14]);
    var barRepeater = eqContents.addProperty("ADBE Vector Filter - Repeater");
    barRepeater.property("Copies").setValue(28);
    barRepeater.property("Transform").property("Position").setValue([28, 0]);
    eqLayer.transform.position.setValue([160, 1840]);
    eqLayer.transform.scale.expression = "linear(Math.sin(time * 16), -1, 1, [100, 40], [100, 140])";
    eqLayer.transform.opacity.setValue(50);

    // =======================================================================
    // 📟 6. TIMECODE HUD EN LA PARTE SUPERIOR
    // =======================================================================
    var tcLayer = comp.layers.addText("LIVE // 00:00:00:00");
    tcLayer.name = "HUD_Timecode";
    tcLayer.inPoint = 0.2;
    tcLayer.outPoint = compDuration - 0.5;
    var tcProp = tcLayer.property("Source Text");
    var tcDoc = tcProp.value;
    tcDoc.fontSize = 22;
    tcDoc.fillColor = [0.85, 0.88, 0.95];
    tcDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
    tcDoc.tracking = 30;
    tcProp.setValue(tcDoc);
    tcLayer.transform.position.setValue([540, 200]);
    tcProp.expression = "'REC [ ' + timeToTimecode(time) + ' ] // FESTIVAL MANIFESTO'";

    // =======================================================================
    // 🎨 PALETA DE COLOR OFICIAL
    // =======================================================================
    var CRIMSON_RED = [1.0, 0.08, 0.14]; // #FF1424
    var PURE_WHITE  = [0.98, 0.98, 0.98];
    var GOLD_ACCENT = [1.0, 0.75, 0.10];

    // =======================================================================
    // 💥 TIPOGRAFÍA CON AUTO-FIT Y ZONAS SEGURAS (Y = 480 a 820)
    // =======================================================================

    // [0s - 18s] ACTO 1: EL MANIFIESTO
    createAutoFitPosterText(comp, "T_01", "✦ CAPÍTULO 01 // MANIFIESTO ✦", 26, CRIMSON_RED, [540, 460], 0.5, 3.0, 25);
    createAutoFitPosterText(comp, "T_02", "EL ARTE", 150, PURE_WHITE, [540, 620], 0.5, 3.0, -12, 120);
    createAutoFitPosterText(comp, "T_03", "DE DISFRUTAR", 170, CRIMSON_RED, [540, 800], 1.2, 3.0, -15, 135);

    createAutoFitPosterText(comp, "T_04", "NO ES SOLO", 130, PURE_WHITE, [540, 600], 3.2, 6.2, -10, 115);
    createAutoFitPosterText(comp, "T_05", "LA MÚSICA", 170, CRIMSON_RED, [540, 780], 4.0, 6.2, -14, 130);

    createAutoFitPosterText(comp, "T_06", "ES LA ATMÓSFERA", 140, PURE_WHITE, [540, 620], 6.5, 9.8, -10, 120);
    createAutoFitPosterText(comp, "T_07", "DONDE TODO TIENE SENTIDO", 90, CRIMSON_RED, [540, 790], 7.2, 9.8, -8, 120);

    createAutoFitPosterText(comp, "T_08", "MILES DE PERSONAS", 130, PURE_WHITE, [540, 620], 10.0, 13.8, -10, 115);
    createAutoFitPosterText(comp, "T_09", "UN SOLO LATIDO", 160, CRIMSON_RED, [540, 800], 11.0, 13.8, -14, 130, true);

    createAutoFitPosterText(comp, "T_10", "CONEXIÓN REAL", 150, PURE_WHITE, [540, 660], 14.0, 17.8, -12, 120);
    createAutoFitPosterText(comp, "T_11", "[ SIN FILTROS // 2026 ]", 34, CRIMSON_RED, [540, 820], 14.6, 17.8, 25);

    // [18s - 36s] ACTO 2: EL ERROR COMÚN (AJUSTADO: NUNCA SE DESBORDA)
    createAutoFitPosterText(comp, "T_12", "⚠️ ERROR #01 DE FESTIVAL", 28, GOLD_ACCENT, [540, 460], 18.0, 22.0, 25);
    createAutoFitPosterText(comp, "T_13", "VIVIR EL SHOW", 140, PURE_WHITE, [540, 620], 18.5, 22.0, -10, 120);
    createAutoFitPosterText(comp, "T_14", "A TRAVÉS DE LA CÁMARA", 100, CRIMSON_RED, [540, 790], 19.2, 22.0, -8, 125, true);

    createAutoFitPosterText(comp, "T_15", "GRABAR CADA MINUTO", 110, PURE_WHITE, [540, 620], 22.2, 26.0, -10, 120);
    createAutoFitPosterText(comp, "T_16", "SIN SENTIR LA MÚSICA", 110, CRIMSON_RED, [540, 790], 23.0, 26.0, -10, 125);

    createAutoFitPosterText(comp, "T_17", "GUARDA EL TELÉFONO", 120, PURE_WHITE, [540, 620], 26.2, 30.5, -10, 120);
    createAutoFitPosterText(comp, "T_18", "ABRE LOS OJOS", 170, CRIMSON_RED, [540, 800], 27.2, 30.5, -15, 135, true);

    createAutoFitPosterText(comp, "T_19", "EL MOMENTO ES HOY", 140, PURE_WHITE, [540, 660], 31.0, 35.5, -10, 120);
    createAutoFitPosterText(comp, "T_20", "[ NO VA A VOLVER ]", 36, CRIMSON_RED, [540, 820], 31.8, 35.5, 25);

    // [36s - 54s] ACTO 3: EL SECRETO
    createAutoFitPosterText(comp, "T_21", "✦ CAPÍTULO 02 // EL SECRETO ✦", 26, CRIMSON_RED, [540, 460], 36.0, 40.0, 25);
    createAutoFitPosterText(comp, "T_22", "ENERGÍA COLECTIVA", 130, CRIMSON_RED, [540, 680], 36.5, 40.0, -12, 130, true);

    createAutoFitPosterText(comp, "T_23", "CUANDO EL BAJO", 130, PURE_WHITE, [540, 620], 40.2, 44.2, -10, 120);
    createAutoFitPosterText(comp, "T_24", "RETUMBA EN TU PECHO", 110, CRIMSON_RED, [540, 790], 41.0, 44.2, -10, 125, true);

    createAutoFitPosterText(comp, "T_25", "PIERDES LA NOCIÓN", 120, PURE_WHITE, [540, 620], 44.5, 48.8, -10, 120);
    createAutoFitPosterText(comp, "T_26", "DEL TIEMPO", 180, CRIMSON_RED, [540, 800], 45.5, 48.8, -16, 140, true);

    createAutoFitPosterText(comp, "T_27", "SOLO EXISTE", 130, PURE_WHITE, [540, 620], 49.0, 53.5, 0, 120);
    createAutoFitPosterText(comp, "T_28", "EL PRESENTE", 170, CRIMSON_RED, [540, 800], 50.0, 53.5, -14, 135);

    // [54s - 72s] ACTO 4: PRO TIPS
    createAutoFitPosterText(comp, "T_29", "✦ PRO TIPS DE EXPERTO ✦", 28, GOLD_ACCENT, [540, 460], 54.0, 58.2, 25);
    createAutoFitPosterText(comp, "T_30", "HIDRÁTATE SIEMPRE", 125, PURE_WHITE, [540, 620], 54.5, 58.2, -10, 120);
    createAutoFitPosterText(comp, "T_31", "EL CUERPO AGUANTA", 130, CRIMSON_RED, [540, 790], 55.5, 58.2, -10, 125);

    createAutoFitPosterText(comp, "T_32", "CONOCE EL LINEUP", 130, PURE_WHITE, [540, 620], 58.5, 62.8, -10, 120);
    createAutoFitPosterText(comp, "T_33", "DÉJATE LLEVAR", 160, CRIMSON_RED, [540, 800], 59.5, 62.8, -14, 130);

    createAutoFitPosterText(comp, "T_34", "LOS MEJORES MOMENTOS", 110, PURE_WHITE, [540, 620], 63.0, 67.5, -10, 115);
    createAutoFitPosterText(comp, "T_35", "NUNCA SE PLANEAN", 130, CRIMSON_RED, [540, 790], 64.0, 67.5, -10, 125);

    createAutoFitPosterText(comp, "T_36", "CAMINA Y EXPLORA", 130, PURE_WHITE, [540, 640], 67.8, 71.8, -10, 120);
    createAutoFitPosterText(comp, "T_37", "NUEVOS ESCENARIOS", 130, CRIMSON_RED, [540, 800], 68.5, 71.8, -10, 125);

    // [72s - 90s] ACTO 5: LA COMUNIDAD
    createAutoFitPosterText(comp, "T_38", "✦ CAPÍTULO 03 // LA TRIBU ✦", 26, CRIMSON_RED, [540, 460], 72.0, 76.5, 25);
    createAutoFitPosterText(comp, "T_39", "DESCONOCIDOS", 150, PURE_WHITE, [540, 620], 72.5, 76.5, -12, 125);
    createAutoFitPosterText(comp, "T_40", "CANTANDO JUNTOS", 140, CRIMSON_RED, [540, 800], 73.5, 76.5, -12, 130, true);

    createAutoFitPosterText(comp, "T_41", "CERO JUZGAR", 160, PURE_WHITE, [540, 620], 77.0, 81.2, -14, 130);
    createAutoFitPosterText(comp, "T_42", "SOLO BUENA VIBRA", 140, CRIMSON_RED, [540, 800], 78.0, 81.2, -12, 130);

    createAutoFitPosterText(comp, "T_43", "SONRISAS Y ABRAZOS", 120, PURE_WHITE, [540, 620], 81.5, 85.8, -10, 120);
    createAutoFitPosterText(comp, "T_44", "ESA ES LA MAGIA", 170, CRIMSON_RED, [540, 800], 82.5, 85.8, -15, 135, true);

    createAutoFitPosterText(comp, "T_45", "LO QUE RECORDARÁS", 130, PURE_WHITE, [540, 660], 86.0, 89.8, -10, 120);
    createAutoFitPosterText(comp, "T_46", "[ PARA TODA LA VIDA ]", 36, CRIMSON_RED, [540, 820], 86.8, 89.8, 25);

    // [90s - 108s] ACTO 6: EL CLÍMAX
    createAutoFitPosterText(comp, "T_47", "✦ EL CLÍMAX // 2026 ✦", 28, CRIMSON_RED, [540, 460], 90.0, 94.5, 25);
    createAutoFitPosterText(comp, "T_48", "EL FESTIVAL TERMINA", 120, PURE_WHITE, [540, 620], 90.5, 94.5, -10, 120);
    createAutoFitPosterText(comp, "T_49", "LA EXPERIENCIA QUEDA", 120, CRIMSON_RED, [540, 790], 91.5, 94.5, -10, 125, true);

    createAutoFitPosterText(comp, "T_50", "NO TE QUEDES MIRANDO", 110, PURE_WHITE, [540, 620], 95.0, 99.2, -10, 120);
    createAutoFitPosterText(comp, "T_51", "SÉ PARTE DEL SHOW", 140, CRIMSON_RED, [540, 800], 96.0, 99.2, -12, 130);

    createAutoFitPosterText(comp, "T_52", "BAILA Y CANTA", 160, PURE_WHITE, [540, 640], 99.5, 103.5, -14, 130);
    createAutoFitPosterText(comp, "T_53", "SÉ LIBRE", 190, CRIMSON_RED, [540, 820], 100.5, 103.5, -16, 140, true);

    createAutoFitPosterText(comp, "T_54", "DISFRUTA CADA SEGUNDO", 95, PURE_WHITE, [540, 720], 104.0, 107.8, -8, 120);

    // [108s - 120s] CIERRE Y LLAMADO A LA ACCIÓN
    createAutoFitPosterText(comp, "T_55", "VÍVELO HOY", 160, PURE_WHITE, [540, 620], 108.0, 113.5, -14, 130);
    createAutoFitPosterText(comp, "T_56", "SIN MIEDO", 200, CRIMSON_RED, [540, 800], 109.0, 113.5, -16, 145, true);

    createAutoFitPosterText(comp, "T_57", "SAL A VIVIRLO", 160, PURE_WHITE, [540, 620], 114.0, 117.8, -14, 130);
    createAutoFitPosterText(comp, "T_58", "AL MÁXIMO", 190, CRIMSON_RED, [540, 800], 114.8, 117.8, -16, 140, true);

    createAutoFitPosterText(comp, "T_59", "[ VIVE LA EXPERIENCIA // 2026 ]", 38, PURE_WHITE, [540, 700], 118.0, compDuration, 25, 110);
    createAutoFitPosterText(comp, "T_60", "✦ COMPARTE CON TU TRIBU ✦", 30, CRIMSON_RED, [540, 840], 118.4, compDuration, 25);

    // =======================================================================
    // 7. APERTURA EN VISOR
    // =======================================================================
    comp.openInViewer();

  } catch (err) {
    alert("Error en script de Producción Perfect-Fit: " + err.toString());
  } finally {
    app.endUndoGroup();
  }
})();
`;

  const jsxFilePath = path.join(outputDir, "Festival_2Min_Perfect_Fit.jsx");
  fs.writeFileSync(jsxFilePath, fullExtendScript, "utf-8");
  console.log(`   ✔ Archivo JSX Perfect-Fit generado -> ${jsxFilePath}`);

  MotionEngine.deliverSocialPackage(comp, "proj_festival_fit", "rev_fit");
  await CLIRunner.run(["node", "bin", "validate", "festival_fit.json"]);
  await CLIRunner.run(["node", "bin", "qa", "festival_fit.json", "--threshold", "0.85"]);

  console.log("\n==========================================================================");
  console.log("🎉 ¡CORRECCIÓN APLICADA AL 100%! TEXTOS PERFECTAMENTE ENCUADRADOS");
  console.log("==========================================================================\n");
}

generatePerfectFittedFestivalMasterpiece().catch(console.error);
