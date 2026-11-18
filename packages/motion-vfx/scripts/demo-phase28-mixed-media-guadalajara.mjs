import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  MixedMediaOrchestrator,
} from "../build/mixed-media/index.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");

const FOOTAGE_DIR = "E:/Respaldo/Guadalajara junio 23-20231019T123606Z-001/Guadalajara junio 23";
const distDir = path.join(rootDir, "dist");
if (!fs.existsSync(distDir)) fs.mkdirSync(distDir, { recursive: true });

console.log("==================================================================");
console.log("  DEMOSTRACIÓN FASE 28: MIXED-MEDIA & ANIME KINETICS              ");
console.log("  Manga Impact, Speed Lines, 35mm Sprockets, Paper Tears & Doodles");
console.log("==================================================================");

const videoA = `${FOOTAGE_DIR}/20230621_114030.mp4`.replace(/\\/g, "/");
const videoB = `${FOOTAGE_DIR}/20230621_114258.mp4`.replace(/\\/g, "/");

const mixedMediaPlan = MixedMediaOrchestrator.compilePlan({
  id: "gdl_music_video_mixed_media",
  fps: 30.0,
  compVarName: "comp",
  layerVarName: "videoLyrA",
  sourceLayerVarName: "videoLyrA",
  destLayerVarName: "videoLyrB",
  impactFrame: {
    id: "manga_beat_drop_impact",
    impactTimeSeconds: 2.0,
    frameDuration: 1,
    mode: "INVERT_NEGATIVE",
  },
  speedLines: {
    id: "anime_shonen_speed_lines",
    startTimeSeconds: 1.5,
    durationSeconds: 2.0,
    centerPoint: [540, 850], // Centro en torso/sujeto
    innerRadiusPx: 280,      // Exclusión limpia del rostro
    lineCount: 70,
    color: [1.0, 1.0, 1.0],
    boilFps: 12,
    density: 0.75,
  },
  sprocketHoles: {
    id: "kodak_35mm_sprockets",
    gauge: "35MM",
    side: "BOTH",
    gateWeaveJitterPx: 2.5,
    keyKodeText: "EASTMAN 5219 48 1024",
    opacity: 90,
  },
  paperTear: {
    id: "collage_paper_tear_wipe",
    startTimeSeconds: 3.2,
    durationSeconds: 1.0,
    direction: "HORIZONTAL",
    tearRoughness: 40,
    fiberFringePx: 14,
  },
  doodleBoil: {
    id: "stop_motion_doodle_aura",
    startTimeSeconds: 0.5,
    durationSeconds: 2.5,
    boilFps: 12,
    jitterAmplitudePx: 4.5,
    strokeColor: [1.0, 0.9, 0.2],
    strokeWidthPx: 3,
  },
});

const jsxLines = [
  "// ============================================================================",
  "//  AUTONOMOUS MIXED-MEDIA & ANIME KINETICS MASTER — GUADALAJARA 2023",
  "//  Fase 28: Manga Impact Frames, Speed Lines, 35mm Sprockets & Paper Tears",
  "// ============================================================================",
  "",
  "app.beginUndoGroup('Build Guadalajara Mixed-Media Showcase');",
  "try {",
  "  var proj = app.project || app.newProject();",
  "  var compW = 1080; var compH = 1920;",
  "  var comp = proj.items.addComp('GDL — Manga, Sprockets & Paper Tears', compW, compH, 1.0, 7.0, 30.0);",
  "  comp.bgColor = [0.02, 0.02, 0.03];",
  "  comp.motionBlur = true; // Invariante obligatoria",
  "",
  `  var fileA = new File('${videoA}');`,
  "  var videoLyrA = null;",
  "  if (fileA.exists) {",
  "    var itemA = proj.importFile(new ImportOptions(fileA));",
  "    videoLyrA = comp.layers.add(itemA);",
  "    videoLyrA.name = '[DOODLE & PRE-TEAR] Guadalajara Scene A';",
  "    videoLyrA.startTime = 0.0; videoLyrA.inPoint = 0.0; videoLyrA.outPoint = 3.6;",
  "    videoLyrA.motionBlur = true;",
  "  }",
  "",
  `  var fileB = new File('${videoB}');`,
  "  var videoLyrB = null;",
  "  if (fileB.exists) {",
  "    var itemB = proj.importFile(new ImportOptions(fileB));",
  "    videoLyrB = comp.layers.add(itemB);",
  "    videoLyrB.name = '[PAPER REVEAL] Guadalajara Scene B';",
  "    videoLyrB.startTime = 3.2; videoLyrB.inPoint = 3.2; videoLyrB.outPoint = 7.0;",
  "    videoLyrB.motionBlur = true;",
  "  }",
  "",
  ...mixedMediaPlan.extendScriptLines,
  "",
  "  app.endUndoGroup();",
  "  alert('¡Composición de Técnicas Mixtas y Cinética Anime (Impact Frames, Speed Lines, Sprockets y Paper Tears) generada con éxito!');",
  "} catch(e) {",
  "  app.endUndoGroup();",
  "  alert('Error en Showcase Mixed-Media: ' + e.toString());",
  "}",
];

const jsxPath = path.join(distDir, "guadalajara_mixed_media_showcase.jsx");
fs.writeFileSync(jsxPath, jsxLines.join("\n"), "utf-8");

console.log(`✓ Plan de Técnicas Mixtas compilado (Checksum SHA-256: ${mixedMediaPlan.checksumSha256.substring(0, 16)}...)`);
console.log(`✓ Líneas ExtendScript generadas: ${mixedMediaPlan.extendScriptLines.length}`);
console.log(`✓ Archivo ExtendScript generado: ${jsxPath}`);
console.log("\n==================================================================");
console.log("  PROCESO COMPLETADO CON ÉXITO                                    ");
console.log("==================================================================");
