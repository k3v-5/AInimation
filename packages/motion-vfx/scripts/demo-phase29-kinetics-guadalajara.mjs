import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  StemKineticsOrchestrator,
} from "../build/stem-kinetics/index.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");

const FOOTAGE_DIR = "E:/Respaldo/Guadalajara junio 23-20231019T123606Z-001/Guadalajara junio 23";
const distDir = path.join(rootDir, "dist");
if (!fs.existsSync(distDir)) fs.mkdirSync(distDir, { recursive: true });

console.log("==================================================================");
console.log("  DEMOSTRACIÓN FASE 29: AUDIO STEMS, ASPECT RATIO & DATAMOSH      ");
console.log("  808 Sub-Bass Bounce, Dynamic Letterboxing Scope & Y2K Datamosh  ");
console.log("==================================================================");

const videoA = `${FOOTAGE_DIR}/20230621_114030.mp4`.replace(/\\/g, "/");
const videoB = `${FOOTAGE_DIR}/20230621_114258.mp4`.replace(/\\/g, "/");

const stemPlan = StemKineticsOrchestrator.compilePlan({
  id: "gdl_music_video_stem_kinetics",
  fps: 30.0,
  compVarName: "comp",
  layerVarName: "videoLyrA",
  sourceLayerVarName: "videoLyrA",
  destLayerVarName: "videoLyrB",
  subBass: {
    id: "sub_808_beat_reaction",
    hitTimesSeconds: [1.0, 1.8, 2.6, 3.4],
    bounceScalePercent: 9.5, // +9.5% de impacto de escala
    decaySeconds: 0.28,
    resonanceHz: 12.0,
    chromaticAberrationPx: 4.0,
  },
  datamosh: {
    id: "y2k_mosh_cut_glitch",
    cutTimeSeconds: 3.5,
    durationSeconds: 0.45,
    macroblockSize: 16,
    displacementIntensity: 65.0,
  },
  aspectRatioBreathing: {
    id: "cinematic_aspect_ratio_breathing",
    transitions: [
      { targetFormat: "4:3", startTimeSeconds: 1.2, durationSeconds: 0.8 },
      { targetFormat: "2.39:1", startTimeSeconds: 3.2, durationSeconds: 0.6 },
    ],
    barColor: [0.0, 0.0, 0.0],
  },
});

const jsxLines = [
  "// ============================================================================",
  "//  AUTONOMOUS STEM KINETICS & ASPECT RATIO MASTER — GUADALAJARA 2023",
  "//  Fase 29: 808 Sub-Bass Elastic Bounce, Dynamic Letterbox & Y2K Datamosh",
  "// ============================================================================",
  "",
  "app.beginUndoGroup('Build Guadalajara Stem Kinetics Showcase');",
  "try {",
  "  var proj = app.project || app.newProject();",
  "  var compW = 1080; var compH = 1920;",
  "  var comp = proj.items.addComp('GDL — 808 Sub-Bass, Letterbox & Datamosh', compW, compH, 1.0, 7.0, 30.0);",
  "  comp.bgColor = [0.02, 0.02, 0.03];",
  "  comp.motionBlur = true; // Invariante obligatoria",
  "",
  `  var fileA = new File('${videoA}');`,
  "  var videoLyrA = null;",
  "  if (fileA.exists) {",
  "    var itemA = proj.importFile(new ImportOptions(fileA));",
  "    videoLyrA = comp.layers.add(itemA);",
  "    videoLyrA.name = '[808 BOUNCE & MOSH SOURCE] Guadalajara Scene A';",
  "    videoLyrA.startTime = 0.0; videoLyrA.inPoint = 0.0; videoLyrA.outPoint = 3.8;",
  "    videoLyrA.motionBlur = true;",
  "  }",
  "",
  `  var fileB = new File('${videoB}');`,
  "  var videoLyrB = null;",
  "  if (fileB.exists) {",
  "    var itemB = proj.importFile(new ImportOptions(fileB));",
  "    videoLyrB = comp.layers.add(itemB);",
  "    videoLyrB.name = '[MOSH DESTINATION & 2.39 SCOPE] Guadalajara Scene B';",
  "    videoLyrB.startTime = 3.2; videoLyrB.inPoint = 3.2; videoLyrB.outPoint = 7.0;",
  "    videoLyrB.motionBlur = true;",
  "  }",
  "",
  ...stemPlan.extendScriptLines,
  "",
  "  app.endUndoGroup();",
  "  alert('¡Composición de Cinética de Stems de Audio (808 Bounce, Letterbox Dinámico y Datamosh Y2K) generada con éxito!');",
  "} catch(e) {",
  "  app.endUndoGroup();",
  "  alert('Error en Showcase Stem Kinetics: ' + e.toString());",
  "}",
];

const jsxPath = path.join(distDir, "guadalajara_stem_kinetics_showcase.jsx");
fs.writeFileSync(jsxPath, jsxLines.join("\n"), "utf-8");

console.log(`✓ Plan de Cinética de Stems compilado (Checksum SHA-256: ${stemPlan.checksumSha256.substring(0, 16)}...)`);
console.log(`✓ Líneas ExtendScript generadas: ${stemPlan.extendScriptLines.length}`);
console.log(`✓ Archivo ExtendScript generado: ${jsxPath}`);
console.log("\n==================================================================");
console.log("  PROCESO COMPLETADO CON ÉXITO                                    ");
console.log("==================================================================");
