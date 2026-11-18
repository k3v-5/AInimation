import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  FilmOrchestrator,
} from "../build/film/index.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");

const FOOTAGE_DIR = "E:/Respaldo/Guadalajara junio 23-20231019T123606Z-001/Guadalajara junio 23";
const distDir = path.join(rootDir, "dist");
if (!fs.existsSync(distDir)) fs.mkdirSync(distDir, { recursive: true });

console.log("==================================================================");
console.log("  DEMOSTRACIÓN FASE 22: ANALOG FILM EMULATION & AUTEUR COLOR      ");
console.log("  16mm Grain, Kodak Halation, Shutter Flicker & Tyler 70s Grading ");
console.log("==================================================================");

const sampleVideo = `${FOOTAGE_DIR}/20230621_114030.mp4`.replace(/\\/g, "/");

const filmPlan = FilmOrchestrator.compilePlan({
  id: "gdl_music_video_film_emulation",
  targetLayerVarName: "videoLyr",
  compVarName: "comp",
  grain: {
    id: "gdl_16mm_grain",
    gauge: "16MM",
    intensity: 0.45,
    luminanceCoupling: true,
    colorNoise: false,
  },
  halation: {
    id: "gdl_kodak_halation",
    threshold: 0.82,
    radiusPx: 32.0,
    intensity: 0.75,
    tintRgb: [1.0, 0.08, 0.05], // Rojo carmesí halation característico
  },
  flicker: {
    id: "gdl_rotary_shutter",
    frequencyHz: 18.0,
    amplitudeEv: 0.04,
    gateWeavePx: 1.4,
  },
  colorGrading: {
    id: "gdl_auteur_grade",
    profile: "TYLER_PASTEL_70S", // Paleta vintage analógica cálida estilo Tyler, The Creator
  },
});

const jsxLines = [
  "// ============================================================================",
  "//  AUTONOMOUS ANALOG FILM & AUTEUR COLOR MASTER — GUADALAJARA 2023",
  "//  Fase 22: 16mm Grain, Kodak Vision3 Halation, Rotary Shutter & Tyler 70s",
  "// ============================================================================",
  "",
  "app.beginUndoGroup('Build Guadalajara Film & Color Showcase');",
  "try {",
  "  var proj = app.project || app.newProject();",
  `  var footageFile = new File('${sampleVideo}');`,
  "  var importedFootage = null;",
  "  if (footageFile.exists) {",
  "    importedFootage = proj.importFile(new ImportOptions(footageFile));",
  "  }",
  "",
  "  var compW = 1080; var compH = 1920;",
  "  var comp = proj.items.addComp('GDL — Film Emulation (16mm & Tyler 70s)', compW, compH, 1.0, 6.0, 30.0);",
  "  comp.bgColor = [0.02, 0.02, 0.03];",
  "  comp.motionBlur = true; // Invariante obligatoria",
  "",
  "  var videoLyr = null;",
  "  if (importedFootage) {",
  "    videoLyr = comp.layers.add(importedFootage);",
  "    videoLyr.name = '[FILM MASTER] Guadalajara Street';",
  "    videoLyr.startTime = 0.0; videoLyr.inPoint = 0.0; videoLyr.outPoint = 6.0;",
  "    videoLyr.motionBlur = true;",
  "    videoLyr.property('Transform').property('Position').setValue([compW / 2, compH / 2]);",
  "    var sc = Math.max((compW / importedFootage.width), (compH / importedFootage.height)) * 100.0;",
  "    videoLyr.property('Transform').property('Scale').setValue([sc, sc]);",
  "  }",
  "",
  ...filmPlan.extendScriptLines,
  "",
  "  app.endUndoGroup();",
  "  alert('¡Composición de Textura Analógica y Color de Autor generada con éxito!');",
  "} catch(e) {",
  "  app.endUndoGroup();",
  "  alert('Error en Showcase Film & Color: ' + e.toString());",
  "}",
];

const jsxPath = path.join(distDir, "guadalajara_film_showcase.jsx");
fs.writeFileSync(jsxPath, jsxLines.join("\n"), "utf-8");

console.log(`✓ Plan de Emulación Fílmica compilado (Checksum SHA-256: ${filmPlan.checksumSha256.substring(0, 16)}...)`);
console.log(`✓ Líneas ExtendScript generadas: ${filmPlan.extendScriptLines.length}`);
console.log(`✓ Archivo ExtendScript generado: ${jsxPath}`);
console.log("\n==================================================================");
console.log("  PROCESO COMPLETADO CON ÉXITO                                    ");
console.log("==================================================================");
