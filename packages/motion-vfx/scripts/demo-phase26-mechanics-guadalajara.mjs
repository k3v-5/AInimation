import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  DynamicMechanicsOrchestrator,
} from "../build/dynamic-mechanics/index.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");

const FOOTAGE_DIR = "E:/Respaldo/Guadalajara junio 23-20231019T123606Z-001/Guadalajara junio 23";
const distDir = path.join(rootDir, "dist");
if (!fs.existsSync(distDir)) fs.mkdirSync(distDir, { recursive: true });

console.log("==================================================================");
console.log("  DEMOSTRACIÓN FASE 26: DYNAMIC OPTICS & MECHANICS (AUTEUR ELITE) ");
console.log("  360° Gyro Rolls, Directional Whip-Pans & Lens Breathing         ");
console.log("==================================================================");

const videoA = `${FOOTAGE_DIR}/20230621_114030.mp4`.replace(/\\/g, "/");
const videoB = `${FOOTAGE_DIR}/20230621_114258.mp4`.replace(/\\/g, "/");

const mechanicsPlan = DynamicMechanicsOrchestrator.compilePlan({
  id: "gdl_music_video_mechanics",
  fps: 30.0,
  compVarName: "comp",
  sourceLayerVarName: "videoLyrA",
  destLayerVarName: "videoLyrB",
  gyroRoll: {
    id: "gyro_360_centrifugal_roll",
    startTimeSeconds: 1.0,
    durationSeconds: 1.5,
    rotations: 1.0, // 360 grados
    direction: "CLOCKWISE",
    scaleBufferPercent: 145, // >= 141.42% para evitar esquinas vacías en rotación
    motionTileMirror: true,
    centrifugalDistortion: 25,
  },
  whipPan: {
    id: "whip_pan_match_cut",
    cutTimeSeconds: 3.5,
    durationSeconds: 0.6,
    directionAngleDegrees: 90, // Hacia la derecha (X-axis pan)
    maxBlurLength: 75,
  },
  lensBreathing: {
    id: "anamorphic_lens_breathing",
    startTimeSeconds: 4.5,
    durationSeconds: 1.2,
    breathingScalePercent: 4.5, // 4.5% focal expansion
    rackBlurPx: 12,
  },
});

const jsxLines = [
  "// ============================================================================",
  "//  AUTONOMOUS DYNAMIC OPTICS & MECHANICS MASTER — GUADALAJARA 2023",
  "//  Fase 26: 360° Gyro Barrel Rolls, Directional Whip-Pans & Lens Breathing",
  "// ============================================================================",
  "",
  "app.beginUndoGroup('Build Guadalajara Dynamic Mechanics Showcase');",
  "try {",
  "  var proj = app.project || app.newProject();",
  "  var compW = 1080; var compH = 1920;",
  "  var comp = proj.items.addComp('GDL — Gyro Rolls, Whip-Pans & Lens Breathing', compW, compH, 1.0, 7.0, 30.0);",
  "  comp.bgColor = [0.02, 0.02, 0.03];",
  "  comp.motionBlur = true; // Invariante obligatoria",
  "",
  `  var fileA = new File('${videoA}');`,
  "  var videoLyrA = null;",
  "  if (fileA.exists) {",
  "    var itemA = proj.importFile(new ImportOptions(fileA));",
  "    videoLyrA = comp.layers.add(itemA);",
  "    videoLyrA.name = '[GYRO ROLL & OUT-WHIP] Guadalajara Scene A';",
  "    videoLyrA.startTime = 0.0; videoLyrA.inPoint = 0.0; videoLyrA.outPoint = 3.8;",
  "    videoLyrA.motionBlur = true;",
  "  }",
  "",
  `  var fileB = new File('${videoB}');`,
  "  var videoLyrB = null;",
  "  if (fileB.exists) {",
  "    var itemB = proj.importFile(new ImportOptions(fileB));",
  "    videoLyrB = comp.layers.add(itemB);",
  "    videoLyrB.name = '[IN-WHIP & BREATHING] Guadalajara Scene B';",
  "    videoLyrB.startTime = 3.2; videoLyrB.inPoint = 3.2; videoLyrB.outPoint = 7.0;",
  "    videoLyrB.motionBlur = true;",
  "  }",
  "",
  ...mechanicsPlan.extendScriptLines,
  "",
  "  app.endUndoGroup();",
  "  alert('¡Composición de Óptica Dinámica y Mecánicas (Gyro Rolls, Whip-Pans y Lens Breathing) generada con éxito!');",
  "} catch(e) {",
  "  app.endUndoGroup();",
  "  alert('Error en Showcase Mechanics: ' + e.toString());",
  "}",
];

const jsxPath = path.join(distDir, "guadalajara_mechanics_showcase.jsx");
fs.writeFileSync(jsxPath, jsxLines.join("\n"), "utf-8");

console.log(`✓ Plan de Mecánicas Dinámicas compilado (Checksum SHA-256: ${mechanicsPlan.checksumSha256.substring(0, 16)}...)`);
console.log(`✓ Líneas ExtendScript generadas: ${mechanicsPlan.extendScriptLines.length}`);
console.log(`✓ Archivo ExtendScript generado: ${jsxPath}`);
console.log("\n==================================================================");
console.log("  PROCESO COMPLETADO CON ÉXITO                                    ");
console.log("==================================================================");
