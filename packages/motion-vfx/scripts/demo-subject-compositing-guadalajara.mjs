import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  TextBehindSubjectEngine,
  MultiTakeCloneEngine,
  ObjectDetectionEngine,
} from "../build/compositing/subject/index.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");

const FOOTAGE_DIR = "E:/Respaldo/Guadalajara junio 23-20231019T123606Z-001/Guadalajara junio 23";
const distDir = path.join(rootDir, "dist");
if (!fs.existsSync(distDir)) fs.mkdirSync(distDir, { recursive: true });

console.log("==================================================================");
console.log("  DEMOSTRACIÓN FASE 19: DETECCIÓN Y COMPOSICIÓN DE SUJETOS        ");
console.log("  Text Behind Subject & Multi-Take Clone Compositing             ");
console.log("==================================================================");

// ============================================================================
// 1. EFECTO 1: TEXTO DETRÁS DEL SUJETO (TEXT BEHIND SUBJECT)
// ============================================================================
console.log("\n[1/2] Generando Efecto 'Texto Detrás del Sujeto' (Depth Sandwich)...");

const sampleVideo1 = `${FOOTAGE_DIR}/20230621_114030.mp4`;

// Detección procedural de silueta humana en el centro
const detectedSubject = ObjectDetectionEngine.createProceduralPersonDetection({
  frameIndex: 0,
  timestampSeconds: 0.0,
  compWidth: 1080,
  compHeight: 1920,
  zone: "CENTER",
  trackId: "person_gdl_center",
});

const textBehindPlan = TextBehindSubjectEngine.compile({
  id: "gdl_editorial_hero",
  sourceAssetPath: sampleVideo1,
  text: "TAPATÍO",
  typography: {
    fontFamily: "Impact",
    fontSize: 220,
    colorHex: "#FF1424", // Crimson Time Style
    verticalStretchPercent: 135,
    tracking: -30,
  },
  position: { x: 540, y: 720 }, // Detrás de la cabeza/hombros
  featherPx: 12.0,
  backgroundBlurPx: 14.0, // Bokeh de fondo sutil
  inTimeSeconds: 0.0,
  outTimeSeconds: 6.0,
  detectedSubject,
});

const textBehindJsxPath = path.join(distDir, "guadalajara_text_behind_subject.jsx");
fs.writeFileSync(textBehindJsxPath, textBehindPlan.extendScriptLines.join("\n"), "utf-8");
console.log(`✓ Plan de Texto Detrás compilado (Checksum SHA-256: ${textBehindPlan.checksumSha256.substring(0, 16)}...)`);
console.log(`✓ Archivo ExtendScript generado: ${textBehindJsxPath}`);

// ============================================================================
// 2. EFECTO 2: EFECTO CLONES MULTI-TOMA (MULTI-TAKE CLONE WEAVER)
// ============================================================================
console.log("\n[2/2] Generando Efecto 'Clones Multi-Toma' (Split Plate Compositing)...");

const sampleVideo2 = `${FOOTAGE_DIR}/20230621_120935.mp4`;

const clonesPlan = MultiTakeCloneEngine.compile({
  id: "gdl_dual_clones",
  compWidth: 1080,
  compHeight: 1920,
  fps: 30,
  takes: [
    {
      takeId: "take_left_gdl",
      assetPath: sampleVideo1,
      subjectZone: "LEFT",
      inPointSeconds: 0.0,
      durationSeconds: 8.0,
      volumeDb: 0.0,
      isMasterBackground: true, // Fondo y ambiente maestro
    },
    {
      takeId: "take_right_gdl",
      assetPath: sampleVideo2,
      subjectZone: "RIGHT",
      inPointSeconds: 1.0,
      durationSeconds: 8.0,
      volumeDb: -1.0,
      isMasterBackground: false,
    },
  ],
  edgeFeatherPx: 35.0, // Fusión suave sin costuras
  totalDurationSeconds: 8.0,
  audioMode: "ACTIVE_SPEAKER", // Evitar duplicación de ruido de fondo
});

const clonesJsxPath = path.join(distDir, "guadalajara_clones_compositing.jsx");
fs.writeFileSync(clonesJsxPath, clonesPlan.extendScriptLines.join("\n"), "utf-8");
console.log(`✓ Plan de Clones compilado (Checksum SHA-256: ${clonesPlan.checksumSha256.substring(0, 16)}...)`);
console.log(`✓ Archivo ExtendScript generado: ${clonesJsxPath}`);

console.log("\n==================================================================");
console.log("  DEMOSTRACIÓN FINALIZADA CON ÉXITO                               ");
console.log("  Los scripts .jsx están listos para ejecutar en After Effects    ");
console.log("==================================================================");
