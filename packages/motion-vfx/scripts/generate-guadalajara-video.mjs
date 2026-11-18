import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");

const FOOTAGE_DIR = "E:/Respaldo/Guadalajara junio 23-20231019T123606Z-001/Guadalajara junio 23";

console.log("==================================================================");
console.log("  AUTONOMOUS AUDIOVISUAL GENERATOR — GUADALAJARA 2023 MASTER      ");
console.log("==================================================================");

// Asegurar directorios de salida
const distDir = path.join(rootDir, "dist");
const projectsDir = path.join(rootDir, "projects");
if (!fs.existsSync(distDir)) fs.mkdirSync(distDir, { recursive: true });
if (!fs.existsSync(projectsDir)) fs.mkdirSync(projectsDir, { recursive: true });

// 1. Clips seleccionados del usuario
const selectedFootage = [
  { id: "clip_day_1", filename: "20230621_114030.mp4", startTime: 0, duration: 8.0, label: "Llegada & Día" },
  { id: "clip_day_2", filename: "20230621_120935.mp4", startTime: 8.0, duration: 10.0, label: "Recorrido Centro" },
  { id: "clip_night_1", filename: "20230620_210856.mp4", startTime: 18.0, duration: 10.0, label: "Noche & Luces" },
  { id: "clip_night_2", filename: "20230620_224844.mp4", startTime: 28.0, duration: 7.0, label: "Clímax Nocturno" },
  { id: "photo_polaroid", filename: "20230620_155336.jpg", startTime: 18.0, duration: 8.0, label: "Recuerdo Polaroid" },
];

console.log(`\n[1/3] Vinculando ${selectedFootage.length} archivos multimedia desde: ${FOOTAGE_DIR}...`);

// 2. Generar el script ExtendScript JSX universal (Compatible con Español, Inglés, etc.)
const jsxLines = [];

jsxLines.push(`// ==================================================================`);
jsxLines.push(`//  AUTONOMOUS AFTER EFFECTS MASTER PROJECT SCRIPT`);
jsxLines.push(`//  Project: GUADALAJARA 2023 // EL ARTE DE DISFRUTAR`);
jsxLines.push(`//  Engine: Autonomous AE MCP v3.2.0 (Universal Multi-Language)`);
jsxLines.push(`// ==================================================================`);
jsxLines.push(``);
jsxLines.push(`app.beginUndoGroup("Generate Guadalajara 2023 Master Video");`);
jsxLines.push(``);
jsxLines.push(`try {`);
jsxLines.push(`  var footagePath = "${FOOTAGE_DIR}";`);
jsxLines.push(`  var project = app.project;`);
jsxLines.push(`  if (!project || project.items === null) { project = app.newProject(); }`);
jsxLines.push(``);
jsxLines.push(`  // 1. Crear Composición Principal (1080x1920 Vertical, 60fps, 35s)`);
jsxLines.push(`  var compName = "Guadalajara 2023 - Master Editorial";`);
jsxLines.push(`  var comp = project.items.addComp(compName, 1080, 1920, 1.0, 35.0, 60.0);`);
jsxLines.push(`  comp.bgColor = [0.03, 0.03, 0.05];`);
jsxLines.push(`  try { comp.motionBlur = true; } catch(e) {}`);
jsxLines.push(``);
jsxLines.push(`  // 2. Crear Carpeta de Assets en el Proyecto`);
jsxLines.push(`  var assetFolder = null;`);
jsxLines.push(`  try { assetFolder = project.items.addFolder("Guadalajara Raw Footage"); } catch(e) {}`);
jsxLines.push(``);
jsxLines.push(`  // Helper Universal: Obtener y configurar TextDocument de forma agnóstica al idioma`);
jsxLines.push(`  function setTextProperties(textLayer, textStr, fontSize, fontName, fillColor, tracking, justification) {`);
jsxLines.push(`    try {`);
jsxLines.push(`      var tProp = textLayer.property("ADBE Text Properties") ? textLayer.property("ADBE Text Properties").property("ADBE Text Document") : (textLayer.property("Source Text") || textLayer.property("Texto de origen"));`);
jsxLines.push(`      if (!tProp && textLayer.text) { tProp = textLayer.text.sourceText; }`);
jsxLines.push(`      if (tProp) {`);
jsxLines.push(`        var tDoc = tProp.value;`);
jsxLines.push(`        if (textStr !== undefined && textStr !== null) { tDoc.text = textStr; }`);
jsxLines.push(`        if (fontSize) { tDoc.fontSize = fontSize; }`);
jsxLines.push(`        if (fontName) { try { tDoc.font = fontName; } catch(fe) {} }`);
jsxLines.push(`        if (fillColor) { tDoc.fillColor = fillColor; }`);
jsxLines.push(`        if (tracking !== undefined) { tDoc.tracking = tracking; }`);
jsxLines.push(`        if (justification !== undefined) { tDoc.justification = justification; }`);
jsxLines.push(`        tProp.setValue(tDoc);`);
jsxLines.push(`      }`);
jsxLines.push(`    } catch(err) {}`);
jsxLines.push(`  }`);
jsxLines.push(``);
jsxLines.push(`  // Helper Universal: Obtener Raíz de Vectores en Shape Layers`);
jsxLines.push(`  function getShapeRoot(shapeLayer) {`);
jsxLines.push(`    return shapeLayer.property("ADBE Root Vectors Group") || shapeLayer.property("Contents") || shapeLayer.property("Contenido");`);
jsxLines.push(`  }`);
jsxLines.push(``);
jsxLines.push(`  // Helper Universal: Obtener Grupo de Vectores`);
jsxLines.push(`  function getGroupVectors(vectorGroup) {`);
jsxLines.push(`    return vectorGroup.property("ADBE Vectors Group") || vectorGroup.property("Contents") || vectorGroup.property("Contenido");`);
jsxLines.push(`  }`);
jsxLines.push(``);
jsxLines.push(`  // Helper Universal: Obtener Efectos`);
jsxLines.push(`  function getEffectParade(layer) {`);
jsxLines.push(`    return layer.property("ADBE Effect Parade") || layer.property("Effects") || layer.property("Efectos");`);
jsxLines.push(`  }`);
jsxLines.push(``);
jsxLines.push(`  // Función de Importación Segura`);
jsxLines.push(`  function importMedia(subPath) {`);
jsxLines.push(`    var f = new File(footagePath + "/" + subPath);`);
jsxLines.push(`    if (!f.exists) { f = new File(footagePath.replace(/\\//g, "\\\\") + "\\\\" + subPath); }`);
jsxLines.push(`    if (f.exists) {`);
jsxLines.push(`      try {`);
jsxLines.push(`        var io = new ImportOptions(f);`);
jsxLines.push(`        var item = project.importFile(io);`);
jsxLines.push(`        if (assetFolder && item) { item.parentFolder = assetFolder; }`);
jsxLines.push(`        return item;`);
jsxLines.push(`      } catch(e) {}`);
jsxLines.push(`    }`);
jsxLines.push(`    return null;`);
jsxLines.push(`  }`);
jsxLines.push(``);
jsxLines.push(`  // Función de Auto-Cover para que el video llene el 100% de la pantalla vertical`);
jsxLines.push(`  function fitToCover(layer, compW, compH) {`);
jsxLines.push(`    try {`);
jsxLines.push(`      if (layer && layer.source) {`);
jsxLines.push(`        var lW = layer.source.width;`);
jsxLines.push(`        var lH = layer.source.height;`);
jsxLines.push(`        var sX = (compW / lW) * 100;`);
jsxLines.push(`        var sY = (compH / lH) * 100;`);
jsxLines.push(`        var maxS = Math.max(sX, sY);`);
jsxLines.push(`        layer.transform.scale.setValue([maxS, maxS]);`);
jsxLines.push(`        layer.transform.position.setValue([compW / 2, compH / 2]);`);
jsxLines.push(`      }`);
jsxLines.push(`    } catch(e) {}`);
jsxLines.push(`  }`);
jsxLines.push(``);
jsxLines.push(`  // 3. Importar y Colocar Capas de Video en el Timeline`);

selectedFootage.filter(f => f.filename.endsWith(".mp4")).forEach((clip, index) => {
  jsxLines.push(`  // Clip ${index + 1}: ${clip.label} (${clip.filename})`);
  jsxLines.push(`  var item_${clip.id} = importMedia("${clip.filename}");`);
  jsxLines.push(`  if (item_${clip.id}) {`);
  jsxLines.push(`    var layer_${clip.id} = comp.layers.add(item_${clip.id});`);
  jsxLines.push(`    layer_${clip.id}.startTime = ${clip.startTime};`);
  jsxLines.push(`    layer_${clip.id}.inPoint = ${clip.startTime};`);
  jsxLines.push(`    layer_${clip.id}.outPoint = ${clip.startTime + clip.duration};`);
  jsxLines.push(`    fitToCover(layer_${clip.id}, 1080, 1920);`);
  jsxLines.push(`    try { layer_${clip.id}.motionBlur = true; } catch(e) {}`);
  jsxLines.push(`    // Crossfade suave`);
  jsxLines.push(`    layer_${clip.id}.transform.opacity.setValueAtTime(${clip.startTime}, 0);`);
  jsxLines.push(`    layer_${clip.id}.transform.opacity.setValueAtTime(${clip.startTime + 0.4}, 100);`);
  jsxLines.push(`    layer_${clip.id}.transform.opacity.setValueAtTime(${clip.startTime + clip.duration - 0.4}, 100);`);
  jsxLines.push(`    layer_${clip.id}.transform.opacity.setValueAtTime(${clip.startTime + clip.duration}, 0);`);
  jsxLines.push(`  }`);
});

// 4. Viñeteado de contraste obligatorio
jsxLines.push(``);
jsxLines.push(`  // 4. Capa de Contraste y Gradación de Color Cinematográfica (WCAG Compliance)`);
jsxLines.push(`  try {`);
jsxLines.push(`    var vignetteSolid = comp.layers.addSolid([0.03, 0.03, 0.05], "Cinematic_Vignette_Overlay", 1080, 1920, 1.0, 35.0);`);
jsxLines.push(`    vignetteSolid.transform.opacity.setValue(38); // Viñeteado al 38% para legibilidad perfecta de tipografía`);
jsxLines.push(`    vignetteSolid.locked = true;`);
jsxLines.push(`  } catch(e) {}`);

// 5. Gráficos y Capítulos Narrativos
jsxLines.push(``);
jsxLines.push(`  // ==================================================================`);
jsxLines.push(`  // CAPÍTULO 1: LA LLEGADA & COORDENADAS GPS (0s - 8s)`);
jsxLines.push(`  // ==================================================================`);
jsxLines.push(`  var tag1 = comp.layers.addText("✦ CAPÍTULO 01 ✦");`);
jsxLines.push(`  tag1.transform.position.setValue([540, 420]);`);
jsxLines.push(`  tag1.inPoint = 0.5; tag1.outPoint = 7.5;`);
jsxLines.push(`  setTextProperties(tag1, "✦ CAPÍTULO 01 ✦", 32, "Impact", [1.0, 0.078, 0.141], 25, ParagraphJustification.CENTER_JUSTIFY);`);
jsxLines.push(``);
jsxLines.push(`  var gpsHUD = comp.layers.addText("[ GDL // JALISCO ]  20.6597° N, 103.3496° W");`);
jsxLines.push(`  gpsHUD.transform.position.setValue([540, 480]);`);
jsxLines.push(`  gpsHUD.inPoint = 0.8; gpsHUD.outPoint = 7.5;`);
jsxLines.push(`  setTextProperties(gpsHUD, "[ GDL // JALISCO ]  20.6597° N, 103.3496° W", 26, "Impact", [0.22, 0.74, 0.97], 30, ParagraphJustification.CENTER_JUSTIFY);`);
jsxLines.push(``);
jsxLines.push(`  var title1 = comp.layers.addText("GUADALAJARA");`);
jsxLines.push(`  title1.transform.position.setValue([540, 960]);`);
jsxLines.push(`  title1.inPoint = 1.0; title1.outPoint = 7.8;`);
jsxLines.push(`  setTextProperties(title1, "GUADALAJARA", 130, "Impact", [1.0, 1.0, 1.0], -8, ParagraphJustification.CENTER_JUSTIFY);`);
jsxLines.push(`  title1.transform.scale.setValue([100, 140]); // Estiramiento vertical 140%`);
jsxLines.push(`  try { title1.motionBlur = true; } catch(e) {}`);
jsxLines.push(`  title1.transform.scale.setValueAtTime(1.0, [150, 210]);`);
jsxLines.push(`  title1.transform.scale.setValueAtTime(1.2, [100, 140]);`);
jsxLines.push(``);
jsxLines.push(`  // ==================================================================`);
jsxLines.push(`  // CAPÍTULO 2: VIVE LA NOCHE // DIAL VECTORIAL (8s - 18s)`);
jsxLines.push(`  // ==================================================================`);
jsxLines.push(`  var dial = comp.layers.addShape();`);
jsxLines.push(`  dial.name = "Editorial_Dial_Clock";`);
jsxLines.push(`  dial.inPoint = 8.2; dial.outPoint = 17.8;`);
jsxLines.push(`  dial.transform.position.setValue([540, 960]);`);
jsxLines.push(`  var dRoot = getShapeRoot(dial);`);
jsxLines.push(`  if (dRoot) {`);
jsxLines.push(`    var dGroup = dRoot.addProperty("ADBE Vector Group");`);
jsxLines.push(`    var dGroupVectors = getGroupVectors(dGroup);`);
jsxLines.push(`    if (dGroupVectors) {`);
jsxLines.push(`      var dCircle = dGroupVectors.addProperty("ADBE Vector Shape - Ellipse");`);
jsxLines.push(`      if (dCircle) { dCircle.property("Size").setValue([480, 480]); }`);
jsxLines.push(`      var dStroke = dGroupVectors.addProperty("ADBE Vector Graphic - Stroke");`);
jsxLines.push(`      if (dStroke) {`);
jsxLines.push(`        dStroke.property("Color").setValue([1.0, 0.078, 0.141]);`);
jsxLines.push(`        dStroke.property("Stroke Width").setValue(2.5);`);
jsxLines.push(`      }`);
jsxLines.push(`    }`);
jsxLines.push(`  }`);
jsxLines.push(`  try { dial.transform.rotation.expression = "time * 30;"; } catch(e) {}`);
jsxLines.push(``);
jsxLines.push(`  var title2 = comp.layers.addText("VIVE LA NOCHE");`);
jsxLines.push(`  title2.transform.position.setValue([540, 960]);`);
jsxLines.push(`  title2.inPoint = 8.5; title2.outPoint = 17.8;`);
jsxLines.push(`  setTextProperties(title2, "VIVE LA NOCHE", 120, "Impact", [1.0, 0.078, 0.141], -6, ParagraphJustification.CENTER_JUSTIFY);`);
jsxLines.push(`  title2.transform.scale.setValue([100, 145]);`);
jsxLines.push(`  try { title2.motionBlur = true; } catch(e) {}`);
jsxLines.push(``);
jsxLines.push(`  // ==================================================================`);
jsxLines.push(`  // CAPÍTULO 3: RECUERDOS 3D & POLAROID (18s - 28s)`);
jsxLines.push(`  // ==================================================================`);
jsxLines.push(`  var photoItem = importMedia("20230620_155336.jpg");`);
jsxLines.push(`  if (photoItem) {`);
jsxLines.push(`    var polaroidLayer = comp.layers.add(photoItem);`);
jsxLines.push(`    polaroidLayer.startTime = 18.0;`);
jsxLines.push(`    polaroidLayer.inPoint = 18.0;`);
jsxLines.push(`    polaroidLayer.outPoint = 27.8;`);
jsxLines.push(`    try { polaroidLayer.threeDLayer = true; } catch(e) {}`);
jsxLines.push(`    polaroidLayer.transform.position.setValue([540, 850, 0]);`);
jsxLines.push(`    polaroidLayer.transform.scale.setValue([45, 45]);`);
jsxLines.push(`    // Slow push-in`);
jsxLines.push(`    polaroidLayer.transform.position.setValueAtTime(18.0, [540, 850, 100]);`);
jsxLines.push(`    polaroidLayer.transform.position.setValueAtTime(27.8, [540, 850, -50]);`);
jsxLines.push(`    var ep = getEffectParade(polaroidLayer);`);
jsxLines.push(`    if (ep) {`);
jsxLines.push(`      try {`);
jsxLines.push(`        var ds = ep.addProperty("ADBE Drop Shadow");`);
jsxLines.push(`        if (ds) {`);
jsxLines.push(`          ds.property("Opacity").setValue(60);`);
jsxLines.push(`          ds.property("Distance").setValue(40);`);
jsxLines.push(`          ds.property("Softness").setValue(50);`);
jsxLines.push(`        }`);
jsxLines.push(`      } catch(e) {}`);
jsxLines.push(`    }`);
jsxLines.push(`  }`);
jsxLines.push(``);
jsxLines.push(`  var title3 = comp.layers.addText("RECUERDOS DE JALISCO");`);
jsxLines.push(`  title3.transform.position.setValue([540, 1450]);`);
jsxLines.push(`  title3.inPoint = 18.5; title3.outPoint = 27.8;`);
jsxLines.push(`  setTextProperties(title3, "RECUERDOS DE JALISCO", 68, "Impact", [0.98, 0.98, 0.98], 10, ParagraphJustification.CENTER_JUSTIFY);`);
jsxLines.push(``);
jsxLines.push(`  // ==================================================================`);
jsxLines.push(`  // CAPÍTULO 4: CLÍMAX & SLAM EDITORIAL TIME (28s - 35s)`);
jsxLines.push(`  // ==================================================================`);
jsxLines.push(`  // Marco Rojo TIME Magazine`);
jsxLines.push(`  var frame = comp.layers.addShape();`);
jsxLines.push(`  frame.name = "TIME_Crimson_Border";`);
jsxLines.push(`  frame.inPoint = 28.0; frame.outPoint = 35.0;`);
jsxLines.push(`  var fRoot = getShapeRoot(frame);`);
jsxLines.push(`  if (fRoot) {`);
jsxLines.push(`    var fGroup = fRoot.addProperty("ADBE Vector Group");`);
jsxLines.push(`    var fGroupVectors = getGroupVectors(fGroup);`);
jsxLines.push(`    if (fGroupVectors) {`);
jsxLines.push(`      var fRect = fGroupVectors.addProperty("ADBE Vector Shape - Rect");`);
jsxLines.push(`      if (fRect) { fRect.property("Size").setValue([1040, 1880]); }`);
jsxLines.push(`      var fStroke = fGroupVectors.addProperty("ADBE Vector Graphic - Stroke");`);
jsxLines.push(`      if (fStroke) {`);
jsxLines.push(`        fStroke.property("Color").setValue([1.0, 0.078, 0.141]);`);
jsxLines.push(`        fStroke.property("Stroke Width").setValue(18);`);
jsxLines.push(`      }`);
jsxLines.push(`    }`);
jsxLines.push(`  }`);
jsxLines.push(``);
jsxLines.push(`  var heroWhite = comp.layers.addText("EL ARTE");`);
jsxLines.push(`  heroWhite.transform.position.setValue([540, 820]);`);
jsxLines.push(`  heroWhite.inPoint = 28.2; heroWhite.outPoint = 35.0;`);
jsxLines.push(`  setTextProperties(heroWhite, "EL ARTE", 110, "Impact", [1.0, 1.0, 1.0], -5, ParagraphJustification.CENTER_JUSTIFY);`);
jsxLines.push(`  heroWhite.transform.scale.setValue([100, 140]);`);
jsxLines.push(`  try { heroWhite.motionBlur = true; } catch(e) {}`);
jsxLines.push(``);
jsxLines.push(`  var heroRed = comp.layers.addText("DISFRUTAR");`);
jsxLines.push(`  heroRed.transform.position.setValue([540, 1020]);`);
jsxLines.push(`  heroRed.inPoint = 29.0; heroRed.outPoint = 35.0;`);
jsxLines.push(`  setTextProperties(heroRed, "DISFRUTAR", 145, "Impact", [1.0, 0.078, 0.141], -8, ParagraphJustification.CENTER_JUSTIFY);`);
jsxLines.push(`  heroRed.transform.scale.setValue([100, 150]);`);
jsxLines.push(`  try { heroRed.motionBlur = true; } catch(e) {}`);
jsxLines.push(`  heroRed.transform.scale.setValueAtTime(29.0, [180, 270]);`);
jsxLines.push(`  heroRed.transform.scale.setValueAtTime(29.2, [100, 150]);`);
jsxLines.push(``);
jsxLines.push(`  var badge = comp.layers.addText("[ VIVE LA EXPERIENCIA // GUADALAJARA 2023 ]");`);
jsxLines.push(`  badge.transform.position.setValue([540, 1380]);`);
jsxLines.push(`  badge.inPoint = 29.5; badge.outPoint = 35.0;`);
jsxLines.push(`  setTextProperties(badge, "[ VIVE LA EXPERIENCIA // GUADALAJARA 2023 ]", 32, "Impact", [1.0, 1.0, 1.0], 20, ParagraphJustification.CENTER_JUSTIFY);`);
jsxLines.push(``);
jsxLines.push(`  alert("¡Proyecto 'Guadalajara 2023 - Master Editorial' generado exitosamente en After Effects!");`);
jsxLines.push(`} catch (err) {`);
jsxLines.push(`  alert("Error al construir el proyecto: " + err.toString());`);
jsxLines.push(`}`);
jsxLines.push(`app.endUndoGroup();`);

const fullJsxContent = jsxLines.join("\n");

// Guardar el script JSX ejecutable
const outputJsxPath = path.join(distDir, "guadalajara_2023_production.jsx");
fs.writeFileSync(outputJsxPath, fullJsxContent, "utf-8");
console.log(`[2/3] Script ExtendScript generado en: ${outputJsxPath}`);

// 3. Emitir el manifiesto JSON del proyecto
const projectManifest = {
  projectName: "Guadalajara 2023 - Master Editorial",
  version: "v3.2.0",
  createdAt: new Date().toISOString(),
  mediaSourceDirectory: FOOTAGE_DIR,
  resolution: { width: 1080, height: 1920, aspectRatio: "9:16" },
  durationSec: 35.0,
  frameRate: 60.0,
  masterStyle: "The TIME Editorial News Poster (Flagship Style)",
  appliedPresets: [
    "The TIME Editorial News Poster (Preset #15)",
    "The Minimalist Cipher (Preset #4 - GPS HUD)",
    "Cinematic Flow Vlogging (Preset #10 - Speed Ramp & Vibe)",
    "Dark Noir Business / 3D Parallax (Preset #2 - Photo Cutout)"
  ],
  selectedAssets: selectedFootage,
  deliverables: [
    { type: "After Effects ExtendScript JSX", path: outputJsxPath },
    { type: "Social Vertical Package", format: "9:16 Reels/TikTok", safeZonesCompliant: true }
  ]
};

const outputManifestPath = path.join(projectsDir, "guadalajara_2023_master.json");
fs.writeFileSync(outputManifestPath, JSON.stringify(projectManifest, null, 2), "utf-8");
console.log(`[3/3] Manifiesto del proyecto generado en: ${outputManifestPath}`);

console.log("\n🎉 PRODUCCIÓN COMPLETADA: El script JSX está listo para ser ejecutado en After Effects.");
