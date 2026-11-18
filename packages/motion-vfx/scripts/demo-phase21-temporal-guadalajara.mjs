import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  TemporalOrchestrator,
} from "../build/temporal/index.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");

const FOOTAGE_DIR = "E:/Respaldo/Guadalajara junio 23-20231019T123606Z-001/Guadalajara junio 23";
const distDir = path.join(rootDir, "dist");
if (!fs.existsSync(distDir)) fs.mkdirSync(distDir, { recursive: true });

console.log("==================================================================");
console.log("  DEMOSTRACIÓN FASE 21: TEMPORAL RATE & SPEED RAMPING SHOWCASE   ");
console.log("  Posterize Time (12fps), Speed Ramp (300% -> 40%) & Stutter Hold ");
console.log("==================================================================");

const sampleVideo = `${FOOTAGE_DIR}/20230621_114030.mp4`.replace(/\\/g, "/");

const temporalPlan = TemporalOrchestrator.compilePlan({
  id: "gdl_music_video_temporal",
  fps: 30.0,
  targetLayerVarName: "videoLyr",
  compVarName: "comp",
  posterizeTime: {
    id: "gdl_12fps_texture",
    targetFps: 12, // Look de película analógica 16mm / animación a doses estilo Ralphie Choo
  },
  speedRamps: [
    {
      id: "ramp_beat_drop_1",
      sourceClipDurationSeconds: 15.0,
      targetBeatDropTimeSeconds: 2.0, // Impacto exacto del bombo / drop
      fastMultiplier: 3.2,           // 320% en compás de aceleración
      slowMultiplier: 0.38,          // 38% cámara lenta suave en el drop
      transitionDurationSeconds: 0.28,
      totalTimelineDurationSeconds: 7.0,
    },
  ],
  stutters: [
    {
      id: "syncopated_stutter_snare",
      triggerTimeSeconds: 3.5,       // Síncopa de caja / snare
      freezeDurationSeconds: 0.12,   // 3-4 fotogramas de congelamiento repentino
      postResumeSpeedMultiplier: 0.8,
    },
  ],
});

const jsxLines = [
  "// ============================================================================",
  "//  AUTONOMOUS TEMPORAL MODULATION MASTER — GUADALAJARA 2023",
  "//  Fase 21: Posterize Time (12fps), Quantized Speed Ramp & Stutter Freeze",
  "// ============================================================================",
  "",
  "app.beginUndoGroup('Build Guadalajara Temporal Showcase');",
  "try {",
  "  var proj = app.project || app.newProject();",
  `  var footageFile = new File('${sampleVideo}');`,
  "  var importedFootage = null;",
  "  if (footageFile.exists) {",
  "    importedFootage = proj.importFile(new ImportOptions(footageFile));",
  "  }",
  "",
  "  var compW = 1080; var compH = 1920;",
  "  var comp = proj.items.addComp('GDL — Temporal Stylization (12fps & Speed Ramp)', compW, compH, 1.0, 7.0, 30.0);",
  "  comp.bgColor = [0.02, 0.02, 0.03];",
  "  comp.motionBlur = true; // Invariante obligatoria",
  "",
  "  var videoLyr = null;",
  "  if (importedFootage) {",
  "    videoLyr = comp.layers.add(importedFootage);",
  "    videoLyr.name = '[TEMPORAL TARGET] Centro Histórico';",
  "    videoLyr.startTime = 0.0; videoLyr.inPoint = 0.0; videoLyr.outPoint = 7.0;",
  "    videoLyr.motionBlur = true;",
  "    videoLyr.property('Transform').property('Position').setValue([compW / 2, compH / 2]);",
  "    var sc = Math.max((compW / importedFootage.width), (compH / importedFootage.height)) * 100.0;",
  "    videoLyr.property('Transform').property('Scale').setValue([sc, sc]);",
  "  }",
  "",
  ...temporalPlan.extendScriptLines,
  "",
  "  app.endUndoGroup();",
  "  alert('¡Composición de Modulación Temporal y Speed Ramping generada con éxito!');",
  "} catch(e) {",
  "  app.endUndoGroup();",
  "  alert('Error en Showcase Temporal: ' + e.toString());",
  "}",
];

const jsxPath = path.join(distDir, "guadalajara_temporal_showcase.jsx");
fs.writeFileSync(jsxPath, jsxLines.join("\n"), "utf-8");

console.log(`✓ Plan Temporal compilado (Checksum SHA-256: ${temporalPlan.checksumSha256.substring(0, 16)}...)`);
console.log(`✓ Keyframes de Time Remap generados: ${temporalPlan.timeRemapKeyframes.length}`);
console.log(`✓ Archivo ExtendScript generado: ${jsxPath}`);
console.log("\n==================================================================");
console.log("  PROCESO COMPLETADO CON ÉXITO                                    ");
console.log("==================================================================");
