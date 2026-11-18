import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  PhotonicsOrchestrator,
} from "../build/photonics/index.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");

const FOOTAGE_DIR = "E:/Respaldo/Guadalajara junio 23-20231019T123606Z-001/Guadalajara junio 23";
const distDir = path.join(rootDir, "dist");
if (!fs.existsSync(distDir)) fs.mkdirSync(distDir, { recursive: true });

console.log("==================================================================");
console.log("  DEMOSTRACIÓN FASE 27: NOCTURNAL PHOTONICS (AUTEUR ELITE)        ");
console.log("  Shutter Drag, Anamorphic Streak, Prism Stars & FLIR Thermal     ");
console.log("==================================================================");

const videoA = `${FOOTAGE_DIR}/20230621_114030.mp4`.replace(/\\/g, "/");
const videoB = `${FOOTAGE_DIR}/20230621_114258.mp4`.replace(/\\/g, "/");

const photonicsPlan = PhotonicsOrchestrator.compilePlan({
  id: "gdl_music_video_photonics",
  fps: 30.0,
  compVarName: "comp",
  layerVarName: "videoLyrA",
  shutterLayerVarName: "videoLyrA",
  thermalLayerVarName: "videoLyrB",
  shutterDrag: {
    id: "shutter_drag_kinetic_echo",
    startTimeSeconds: 1.0,
    durationSeconds: 2.2,
    echoCount: 6,
    echoTimeStepSeconds: -0.033,
    decay: 0.78,
    blendOperator: "MAXIMUM",
    chromaticDispersion: true,
  },
  flirThermal: {
    id: "flir_ironbow_thermal_vision",
    startTimeSeconds: 3.5,
    durationSeconds: 2.5,
    palette: "IRONBOW",
    thermalNoiseIntensity: 15,
    edgeEnhancement: true,
  },
  anamorphicStreak: {
    id: "anamorphic_cyan_streak_flare",
    startTimeSeconds: 2.0,
    durationSeconds: 2.5,
    thresholdPercent: 82,
    streakLength: 350,
    directionDegrees: 90.0,
    tintColor: [0.0, 0.9, 1.0], // Cian anamórfico neón
    intensity: 1.2,
  },
  prismStar: {
    id: "prism_cross_screen_star",
    startTimeSeconds: 2.8,
    durationSeconds: 2.7,
    points: 4,
    thresholdPercent: 85,
    starLength: 95,
    intensity: 1.0,
    rotationDegrees: 45.0,
  },
});

const jsxLines = [
  "// ============================================================================",
  "//  AUTONOMOUS NOCTURNAL PHOTONICS MASTER — GUADALAJARA 2023",
  "//  Fase 27: Shutter Drag, Anamorphic Streaks, Prism Stars & FLIR Thermal",
  "// ============================================================================",
  "",
  "app.beginUndoGroup('Build Guadalajara Photonics Showcase');",
  "try {",
  "  var proj = app.project || app.newProject();",
  "  var compW = 1080; var compH = 1920;",
  "  var comp = proj.items.addComp('GDL — Shutter Drag, Streaks, Stars & FLIR', compW, compH, 1.0, 7.0, 30.0);",
  "  comp.bgColor = [0.02, 0.02, 0.03];",
  "  comp.motionBlur = true; // Invariante obligatoria",
  "",
  `  var fileA = new File('${videoA}');`,
  "  var videoLyrA = null;",
  "  if (fileA.exists) {",
  "    var itemA = proj.importFile(new ImportOptions(fileA));",
  "    videoLyrA = comp.layers.add(itemA);",
  "    videoLyrA.name = '[SHUTTER DRAG] Guadalajara Scene A';",
  "    videoLyrA.startTime = 0.0; videoLyrA.inPoint = 0.0; videoLyrA.outPoint = 3.6;",
  "    videoLyrA.motionBlur = true;",
  "  }",
  "",
  `  var fileB = new File('${videoB}');`,
  "  var videoLyrB = null;",
  "  if (fileB.exists) {",
  "    var itemB = proj.importFile(new ImportOptions(fileB));",
  "    videoLyrB = comp.layers.add(itemB);",
  "    videoLyrB.name = '[FLIR THERMAL] Guadalajara Scene B';",
  "    videoLyrB.startTime = 3.4; videoLyrB.inPoint = 3.4; videoLyrB.outPoint = 7.0;",
  "    videoLyrB.motionBlur = true;",
  "  }",
  "",
  ...photonicsPlan.extendScriptLines,
  "",
  "  app.endUndoGroup();",
  "  alert('¡Composición de Óptica Fotónica Nocturna (Shutter Drag, Anamorphic Streaks, Prism Stars y FLIR Thermal) generada con éxito!');",
  "} catch(e) {",
  "  app.endUndoGroup();",
  "  alert('Error en Showcase Photonics: ' + e.toString());",
  "}",
];

const jsxPath = path.join(distDir, "guadalajara_photonics_showcase.jsx");
fs.writeFileSync(jsxPath, jsxLines.join("\n"), "utf-8");

console.log(`✓ Plan Fotónico Nocturno compilado (Checksum SHA-256: ${photonicsPlan.checksumSha256.substring(0, 16)}...)`);
console.log(`✓ Líneas ExtendScript generadas: ${photonicsPlan.extendScriptLines.length}`);
console.log(`✓ Archivo ExtendScript generado: ${jsxPath}`);
console.log("\n==================================================================");
console.log("  PROCESO COMPLETADO CON ÉXITO                                    ");
console.log("==================================================================");
