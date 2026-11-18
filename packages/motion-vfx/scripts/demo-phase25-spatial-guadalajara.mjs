import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  SpatialCinematographyOrchestrator,
} from "../build/spatial-cinematography/index.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");

const FOOTAGE_DIR = "E:/Respaldo/Guadalajara junio 23-20231019T123606Z-001/Guadalajara junio 23";
const distDir = path.join(rootDir, "dist");
if (!fs.existsSync(distDir)) fs.mkdirSync(distDir, { recursive: true });

console.log("==================================================================");
console.log("  DEMOSTRACIÓN FASE 25: SPATIAL CINEMATOGRAPHY (AUTEUR ELITE)     ");
console.log("  Snorricam Body Lock, Infinite Zoom Portals & Parallax Wipes    ");
console.log("==================================================================");

const videoA = `${FOOTAGE_DIR}/20230621_114030.mp4`.replace(/\\/g, "/");
const videoB = `${FOOTAGE_DIR}/20230621_114258.mp4`.replace(/\\/g, "/");

const spatialPlan = SpatialCinematographyOrchestrator.compilePlan({
  id: "gdl_music_video_spatial",
  fps: 30.0,
  compVarName: "comp",
  sourceLayerVarName: "videoLyrA",
  destLayerVarName: "videoLyrB",
  snorricam: {
    id: "snorricam_subject_lock",
    subjectAnchorPoint: [540, 850], // Centro de gravedad del torso/cabeza
    scaleBufferPercent: 130,        // Margen del 130% para absorber desplazamientos
    motionTileMirror: true,         // Replicación en espejo para eliminar costuras
  },
  portal: {
    id: "wormhole_infinite_zoom",
    startTimeSeconds: 2.0,
    durationSeconds: 1.2,
    portalCenterPoint: [540, 850],  // Colapso super-exponencial hacia el centro
    maxScalePercent: 6000,          // Expansión del 6000%
    accelerationExponent: 3.2,
  },
  occlusionWipe: {
    id: "hiro_murai_occlusion_wipe",
    startTimeSeconds: 3.5,
    durationSeconds: 0.8,
    direction: "LEFT_TO_RIGHT",     // Oclusor pasando de izquierda a derecha
    featherPx: 40,                  // Calado suave que imita desenfoque de movimiento
  },
});

const jsxLines = [
  "// ============================================================================",
  "//  AUTONOMOUS SPATIAL CINEMATOGRAPHY MASTER — GUADALAJARA 2023",
  "//  Fase 25: Snorricam Body Lock, Infinite Zoom Wormholes & Occlusion Wipes",
  "// ============================================================================",
  "",
  "app.beginUndoGroup('Build Guadalajara Spatial Cinematography Showcase');",
  "try {",
  "  var proj = app.project || app.newProject();",
  "  var compW = 1080; var compH = 1920;",
  "  var comp = proj.items.addComp('GDL — Snorricam, Portals & Wipes', compW, compH, 1.0, 7.0, 30.0);",
  "  comp.bgColor = [0.02, 0.02, 0.03];",
  "  comp.motionBlur = true; // Invariante obligatoria",
  "",
  `  var fileA = new File('${videoA}');`,
  "  var videoLyrA = null;",
  "  if (fileA.exists) {",
  "    var itemA = proj.importFile(new ImportOptions(fileA));",
  "    videoLyrA = comp.layers.add(itemA);",
  "    videoLyrA.name = '[SNORRICAM & PORTAL] Guadalajara Subject';",
  "    videoLyrA.startTime = 0.0; videoLyrA.inPoint = 0.0; videoLyrA.outPoint = 4.5;",
  "    videoLyrA.motionBlur = true;",
  "  }",
  "",
  `  var fileB = new File('${videoB}');`,
  "  var videoLyrB = null;",
  "  if (fileB.exists) {",
  "    var itemB = proj.importFile(new ImportOptions(fileB));",
  "    videoLyrB = comp.layers.add(itemB);",
  "    videoLyrB.name = '[OCCLUSION REVEAL] Guadalajara Scene B';",
  "    videoLyrB.startTime = 3.5; videoLyrB.inPoint = 3.5; videoLyrB.outPoint = 7.0;",
  "    videoLyrB.motionBlur = true;",
  "  }",
  "",
  ...spatialPlan.extendScriptLines,
  "",
  "  app.endUndoGroup();",
  "  alert('¡Composición de Cinematografía Espacial (Snorricam, Portales y Wipes) generada con éxito!');",
  "} catch(e) {",
  "  app.endUndoGroup();",
  "  alert('Error en Showcase Spatial: ' + e.toString());",
  "}",
];

const jsxPath = path.join(distDir, "guadalajara_spatial_showcase.jsx");
fs.writeFileSync(jsxPath, jsxLines.join("\n"), "utf-8");

console.log(`✓ Plan de Cinematografía Espacial compilado (Checksum SHA-256: ${spatialPlan.checksumSha256.substring(0, 16)}...)`);
console.log(`✓ Líneas ExtendScript generadas: ${spatialPlan.extendScriptLines.length}`);
console.log(`✓ Archivo ExtendScript generado: ${jsxPath}`);
console.log("\n==================================================================");
console.log("  PROCESO COMPLETADO CON ÉXITO                                    ");
console.log("==================================================================");
