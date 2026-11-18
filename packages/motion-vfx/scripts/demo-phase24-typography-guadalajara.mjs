import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  KineticTypographyOrchestrator,
} from "../build/kinetic-typography/index.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");

const FOOTAGE_DIR = "E:/Respaldo/Guadalajara junio 23-20231019T123606Z-001/Guadalajara junio 23";
const distDir = path.join(rootDir, "dist");
if (!fs.existsSync(distDir)) fs.mkdirSync(distDir, { recursive: true });

console.log("==================================================================");
console.log("  DEMOSTRACIÓN FASE 24: BRUTALIST KINETIC TYPOGRAPHY & CHROME     ");
console.log("  TIME Style 140% Stretch, Liquid Chrome Shader & 3D Pavement     ");
console.log("==================================================================");

const sampleVideo = `${FOOTAGE_DIR}/20230621_114030.mp4`.replace(/\\/g, "/");

const typographyPlan = KineticTypographyOrchestrator.compilePlan({
  id: "gdl_music_video_typography",
  fps: 30.0,
  compVarName: "comp",
  layerVarName: "textLyr",
  brutalist: {
    id: "gdl_hero_title",
    text: "máquina culona",
    fontFamily: "Impact",
    fontSizePx: 230,
    verticalStretchPercent: 140, // 140% estiramiento vertical anamórfico estilo TIME / Tyler
    tracking: -75,              // Tracking negativo ultra-condensado
    colorHex: "#FF1424",        // Rojo carmesí TIME / Tyler
    allCaps: true,
  },
  chrome: {
    id: "gdl_liquid_chrome_shader",
    bevelDepthPx: 5.0,
    turbulentAmount: 14.0,
    turbulentSize: 22.0,
    evolutionSpeed: 2.0,
    chromePalette: "PLATINUM",  // Acabado metálico hiper-reflectante
  },
  perspective: {
    id: "gdl_street_3d_anchor",
    position3D: [540, 1100, 200],
    rotation3D: [0, 0, 0],
    vanishingPointAlign: "FLOOR_RECEDING", // Inclinado 72° descansando en perspectiva sobre el asfalto
  },
  slam: {
    id: "gdl_slam_impact",
    triggerTimeSeconds: 1.0, // Impacto al segundo 1.0
    durationSeconds: 0.40,
    initialScalePercent: 280, // Slam desde 280%
    dampingRatio: 0.55,       // Rebote elástico armónico
    naturalFrequency: 24.0,
  },
});

const jsxLines = [
  "// ============================================================================",
  "//  AUTONOMOUS BRUTALIST KINETIC TYPOGRAPHY MASTER — GUADALAJARA 2023",
  "//  Fase 24: TIME Style 140% Vertical Stretch, Liquid Chrome & 3D Pavement Anchor",
  "// ============================================================================",
  "",
  "app.beginUndoGroup('Build Guadalajara Kinetic Typography Showcase');",
  "try {",
  "  var proj = app.project || app.newProject();",
  `  var footageFile = new File('${sampleVideo}');`,
  "  var importedFootage = null;",
  "  if (footageFile.exists) {",
  "    importedFootage = proj.importFile(new ImportOptions(footageFile));",
  "  }",
  "",
  "  var compW = 1080; var compH = 1920;",
  "  var comp = proj.items.addComp('GDL — Brutalist Liquid Chrome 3D', compW, compH, 1.0, 6.0, 30.0);",
  "  comp.bgColor = [0.02, 0.02, 0.03];",
  "  comp.motionBlur = true; // Invariante obligatoria",
  "",
  "  var videoLyr = null;",
  "  if (importedFootage) {",
  "    videoLyr = comp.layers.add(importedFootage);",
  "    videoLyr.name = '[BACKGROUND FOOTAGE] Guadalajara Street';",
  "    videoLyr.startTime = 0.0; videoLyr.inPoint = 0.0; videoLyr.outPoint = 6.0;",
  "    videoLyr.motionBlur = true;",
  "    videoLyr.property('Transform').property('Position').setValue([compW / 2, compH / 2]);",
  "    var sc = Math.max((compW / importedFootage.width), (compH / importedFootage.height)) * 100.0;",
  "    videoLyr.property('Transform').property('Scale').setValue([sc, sc]);",
  "  }",
  "",
  ...typographyPlan.extendScriptLines,
  "",
  "  app.endUndoGroup();",
  "  alert('¡Composición de Tipografía Cinética Brutalista y Cromo Líquido 3D generada con éxito!');",
  "} catch(e) {",
  "  app.endUndoGroup();",
  "  alert('Error en Showcase Typography: ' + e.toString());",
  "}",
];

const jsxPath = path.join(distDir, "guadalajara_typography_showcase.jsx");
fs.writeFileSync(jsxPath, jsxLines.join("\n"), "utf-8");

console.log(`✓ Plan de Tipografía Cinética compilado (Checksum SHA-256: ${typographyPlan.checksumSha256.substring(0, 16)}...)`);
console.log(`✓ Líneas ExtendScript generadas: ${typographyPlan.extendScriptLines.length}`);
console.log(`✓ Archivo ExtendScript generado: ${jsxPath}`);
console.log("\n==================================================================");
console.log("  PROCESO COMPLETADO CON ÉXITO                                    ");
console.log("==================================================================");
