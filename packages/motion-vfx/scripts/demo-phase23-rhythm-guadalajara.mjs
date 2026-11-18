import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  RhythmOrchestrator,
  MusicalGrid,
} from "../build/rhythm/index.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");

const FOOTAGE_DIR = "E:/Respaldo/Guadalajara junio 23-20231019T123606Z-001/Guadalajara junio 23";
const distDir = path.join(rootDir, "dist");
if (!fs.existsSync(distDir)) fs.mkdirSync(distDir, { recursive: true });

console.log("==================================================================");
console.log("  DEMOSTRACIÓN FASE 23: MACHINE-GUN FLASH CUTS & BLACKOUT DROPS   ");
console.log("  135 BPM Syncopated Cuts, Strobe Bursts & Pre-Drop Audio Vacuums ");
console.log("==================================================================");

const videoA = `${FOOTAGE_DIR}/20230621_114030.mp4`.replace(/\\/g, "/");
const videoB = `${FOOTAGE_DIR}/20230621_114258.mp4`.replace(/\\/g, "/");
const videoC = `${FOOTAGE_DIR}/20230621_114704.mp4`.replace(/\\/g, "/");

const bpm = 135.0;
const fps = 30.0;
const beatSec = MusicalGrid.getBeatDurationSeconds(bpm); // ~0.444s

// Diseñar una secuencia rítmica sincopada de 3 tomas en los primeros 3.6s
const cutPoints = [
  { timeSeconds: 0.0, mediaAssetPath: videoA, sourceInPointSeconds: 0.0, durationSeconds: beatSec * 2.0 },
  { timeSeconds: beatSec * 2.0, mediaAssetPath: videoB, sourceInPointSeconds: 1.0, durationSeconds: beatSec * 3.0 },
  { timeSeconds: beatSec * 5.0, mediaAssetPath: videoC, sourceInPointSeconds: 2.0, durationSeconds: beatSec * 3.0 },
];

const rhythmPlan = RhythmOrchestrator.compilePlan({
  id: "gdl_music_video_rhythm",
  bpm,
  fps,
  compVarName: "comp",
  syncopatedCuts: cutPoints,
  bursts: [
    {
      id: "pre_drop_machine_gun_strobe",
      startTimeSeconds: 3.20,
      durationSeconds: 0.40, // 12 fotogramas de ráfaga
      frameHold: 1,          // 1 fotograma por corte (ultra-rápido estilo HUMBLE)
      mode: "CRIMSON_STROBE",// Rojo carmesí editorial #FF1424
    },
  ],
  blackouts: [
    {
      id: "main_beat_drop_vacuum",
      dropTimeSeconds: 4.00, // Momento de la explosión del beat
      vacuumDurationSeconds: 0.16, // ~5 fotogramas de vacío absoluto previo (t = 3.84s a 4.00s)
      impactFlashFrame: true,      // 1 frame de destello blanco en t = 4.00s
      flashColorHex: "#FFFFFF",
    },
  ],
});

const jsxLines = [
  "// ============================================================================",
  "//  AUTONOMOUS RHYTHMIC CUTTING & FLASH BURST MASTER — GUADALAJARA 2023",
  "//  Fase 23: 135 BPM Syncopated Cuts, Crimson Strobe & Blackout Vacuum Drop",
  "// ============================================================================",
  "",
  "app.beginUndoGroup('Build Guadalajara Rhythm & Flash Cuts Showcase');",
  "try {",
  "  var proj = app.project || app.newProject();",
  "  var compW = 1080; var compH = 1920;",
  "  var comp = proj.items.addComp('GDL — Rhythmic Machine-Gun & Blackout', compW, compH, 1.0, 6.0, 30.0);",
  "  comp.bgColor = [0.02, 0.02, 0.03];",
  "  comp.motionBlur = true; // Invariante obligatoria",
  "",
  ...rhythmPlan.extendScriptLines,
  "",
  "  app.endUndoGroup();",
  "  alert('¡Composición de Montaje Rítmico, Machine-Gun Strobe y Blackout generada con éxito!');",
  "} catch(e) {",
  "  app.endUndoGroup();",
  "  alert('Error en Showcase Rhythm: ' + e.toString());",
  "}",
];

const jsxPath = path.join(distDir, "guadalajara_rhythm_showcase.jsx");
fs.writeFileSync(jsxPath, jsxLines.join("\n"), "utf-8");

console.log(`✓ Plan Rítmico compilado (Checksum SHA-256: ${rhythmPlan.checksumSha256.substring(0, 16)}...)`);
console.log(`✓ Líneas ExtendScript generadas: ${rhythmPlan.extendScriptLines.length}`);
console.log(`✓ Archivo ExtendScript generado: ${jsxPath}`);
console.log("\n==================================================================");
console.log("  PROCESO COMPLETADO CON ÉXITO                                    ");
console.log("==================================================================");
