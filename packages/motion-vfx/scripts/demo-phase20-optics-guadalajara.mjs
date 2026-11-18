import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  CameraMotionOrchestrator,
} from "../build/optics/index.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");

const FOOTAGE_DIR = "E:/Respaldo/Guadalajara junio 23-20231019T123606Z-001/Guadalajara junio 23";
const distDir = path.join(rootDir, "dist");
if (!fs.existsSync(distDir)) fs.mkdirSync(distDir, { recursive: true });

console.log("==================================================================");
console.log("  DEMOSTRACIÓN FASE 20: EXTREME OPTICS & CAMERA MOTION SHOWCASE   ");
console.log("  Snap Zooms Inerciales, Fisheye Vintage y Dolly Zoom Vertigo    ");
console.log("==================================================================");

const sampleVideo = `${FOOTAGE_DIR}/20230621_114030.mp4`.replace(/\\/g, "/");

const opticsPlan = CameraMotionOrchestrator.compilePlan({
  id: "gdl_music_video_optics",
  targetCompWidth: 1080,
  targetCompHeight: 1920,
  fps: 30.0,
  snapZooms: [
    {
      id: "snap_drop_1",
      triggerTimeSeconds: 1.0,
      durationSeconds: 0.22,
      startScalePercent: 100.0,
      peakScalePercent: 195.0, // Impacto ultra-rápido estilo Tyler / Dave Free
      settleScalePercent: 108.0,
      dampingRatio: 0.52,
      frequencyHz: 6.5,
      overshootPercent: 18.0,
    },
    {
      id: "snap_drop_2",
      triggerTimeSeconds: 2.5,
      durationSeconds: 0.20,
      startScalePercent: 108.0,
      peakScalePercent: 210.0, // Segundo golpe de caja / snare
      settleScalePercent: 100.0,
      dampingRatio: 0.60,
      frequencyHz: 7.0,
      overshootPercent: 15.0,
    },
  ],
  fisheye: {
    id: "gdl_fisheye_lens",
    distortionFactor: 68.0, // Abombamiento característico de 90s hip-hop
    chromaticAberrationPx: 12.0,
    vignetteAmount: 0.42,
    centerOffsetX: 0,
    centerOffsetY: 0,
  },
  dollyZooms: [
    {
      id: "dolly_vertigo_outro",
      startTimeSeconds: 4.5,
      durationSeconds: 3.5,
      initialFovDegrees: 35.0, // Teleobjetivo comprimido
      finalFovDegrees: 90.0,   // Apertura a gran angular dramático
      subjectScaleLock: true,
    },
  ],
  whipPans: [
    {
      id: "whip_transition",
      triggerTimeSeconds: 4.0,
      durationSeconds: 0.16,
      direction: "RIGHT",
      travelAngleDegrees: 270,
      blurIntensityPx: 55.0,
    },
  ],
  targetLayerVarName: "videoLyr",
  compVarName: "comp",
});

// Envolver el plan en la plantilla ExtendScript de importación de video de Guadalajara
const jsxLines = [
  "// ============================================================================",
  "//  AUTONOMOUS MUSIC VIDEO OPTICS MASTER — GUADALAJARA 2023",
  "//  Fase 20: Extreme Optics, Fisheye, Crash Zooms & Dolly Vertigo",
  "// ============================================================================",
  "",
  "app.beginUndoGroup('Build Guadalajara Extreme Optics Showcase');",
  "try {",
  "  var proj = app.project || app.newProject();",
  `  var footageFile = new File('${sampleVideo}');`,
  "  var importedFootage = null;",
  "  if (footageFile.exists) {",
  "    importedFootage = proj.importFile(new ImportOptions(footageFile));",
  "  }",
  "",
  "  var compW = 1080; var compH = 1920;",
  "  var comp = proj.items.addComp('GDL — Extreme Optics (Tyler/Kendrick Style)', compW, compH, 1.0, 9.0, 30.0);",
  "  comp.bgColor = [0.02, 0.02, 0.03];",
  "  comp.motionBlur = true; // Invariante obligatoria",
  "",
  "  var videoLyr = null;",
  "  if (importedFootage) {",
  "    videoLyr = comp.layers.add(importedFootage);",
  "    videoLyr.name = '[OPTICS TARGET] Centro Histórico';",
  "    videoLyr.startTime = 0.0; videoLyr.inPoint = 0.0; videoLyr.outPoint = 9.0;",
  "    videoLyr.motionBlur = true;",
  "    videoLyr.property('Transform').property('Position').setValue([compW / 2, compH / 2]);",
  "    var sc = Math.max((compW / importedFootage.width), (compH / importedFootage.height)) * 100.0;",
  "    videoLyr.property('Transform').property('Scale').setValue([sc, sc]);",
  "  }",
  "",
  ...opticsPlan.extendScriptLines,
  "",
  "  app.endUndoGroup();",
  "  alert('¡Composición de Óptica Extrema y Cámara generada con éxito!');",
  "} catch(e) {",
  "  app.endUndoGroup();",
  "  alert('Error en Showcase de Óptica: ' + e.toString());",
  "}",
];

const jsxPath = path.join(distDir, "guadalajara_optics_showcase.jsx");
fs.writeFileSync(jsxPath, jsxLines.join("\n"), "utf-8");

console.log(`✓ Plan de Ópticas compilado (Checksum SHA-256: ${opticsPlan.checksumSha256.substring(0, 16)}...)`);
console.log(`✓ Archivo ExtendScript generado: ${jsxPath}`);
console.log("\n==================================================================");
console.log("  PROCESO COMPLETADO CON ÉXITO                                    ");
console.log("==================================================================");
