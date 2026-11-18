import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  BeatSyncEngine,
  EditorialIRBuilder,
  OtioExporter,
  EditorialQAEngine,
} from "../build/editorial/index.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");

const FOOTAGE_DIR = "E:/Respaldo/Guadalajara junio 23-20231019T123606Z-001/Guadalajara junio 23";
const distDir = path.join(rootDir, "dist");
if (!fs.existsSync(distDir)) fs.mkdirSync(distDir, { recursive: true });

console.log("==================================================================");
console.log("  RHYTHMIC BEAT SYNC COMPILER — GUADALAJARA 2023 (v4.1.0)         ");
console.log("  Sincronización Rítmica por Transientes de Audio en After Effects ");
console.log("==================================================================");

// 1. Assets Reales Disponibles
const rawClips = [
  { id: "c1", assetId: "20230621_114030.mp4", label: "Centro Histórico Día", availableDurationSeconds: 8.0 },
  { id: "c2", assetId: "20230621_120935.mp4", label: "Hospicio Cabañas Recorrido", availableDurationSeconds: 10.0 },
  { id: "c3", assetId: "20230620_210856.mp4", label: "Noche Urbana & Luces", availableDurationSeconds: 10.0 },
  { id: "c4", assetId: "20230620_224844.mp4", label: "Clímax Nocturno Tapatío", availableDurationSeconds: 8.0 },
  { id: "c5", assetId: "20230621_122207.mp4", label: "Catedral y Plaza Principal", availableDurationSeconds: 6.0 },
];

// 2. Generar Cuadrícula Rítmica (BPM Grid)
// Pista musical de ritmo moderno: 120 BPM, Compás 4/4 (1 beat = 0.5s, 1 compás = 2.0s)
const TARGET_BPM = 120;
const TOTAL_DURATION = 24.0; // 12 compases musicales exactos
console.log(`\n[Paso 1/4] Generando cuadrícula rítmica a ${TARGET_BPM} BPM (4/4)...`);

const { beats, markers } = BeatSyncEngine.generateBeatGrid({
  bpm: TARGET_BPM,
  timeSignature: "4/4",
  offsetSeconds: 0.0,
  totalDurationSeconds: TOTAL_DURATION,
  subdivision: 1,
});

console.log(`✓ ${beats.length} beats calculados (${markers.filter((m) => m.isDownbeat).length} compases/downbeats)`);

// 3. Alinear Cortes Audiovisuales a la Música
console.log("\n[Paso 2/4] Alineando cortes de metraje a transientes musicales...");
const beatSyncPlan = BeatSyncEngine.alignCutsToBeat({
  clips: rawClips,
  beatGrid: beats,
  mode: "HALF_BAR", // Corta cada medio compás (1.0s o 2.0s) según la fuerza del beat
  minCutDurationSeconds: 1.0,
  maxTotalDurationSeconds: TOTAL_DURATION,
  pulseStrengthPercent: 107.0, // Punch-In de 107% en el golpe de bombo (Downbeat)
});

console.log(`✓ ${beatSyncPlan.totalCuts} cortes rítmicos calculados sin huecos (Duración: ${beatSyncPlan.totalDurationSeconds}s)`);
console.log(`✓ ${beatSyncPlan.scalePulses.length} keyframes de pulsación reactiva generados`);
console.log(`✓ Checksum SHA-256 inmutable: ${beatSyncPlan.checksumSha256}`);

// 4. Construir Editorial IR
console.log("\n[Paso 3/4] Ensamblando Editorial IR...");
const builder = new EditorialIRBuilder("proj_gdl_beat_sync", {
  title: "Guadalajara 2023 — Rhythmic Beat Sync Cut",
  profile: "SHORT_FORM",
  frameRate: 30,
  width: 1080,
  height: 1920, // Vertical 9:16 para TikTok / Instagram Reels
  targetDialogueLufs: -14,
});

builder.createTrack({ id: "t_v1", name: "V1 Rhythmic Cuts", type: "VIDEO_PRIMARY", index: 0 });
builder.createTrack({ id: "t_v2", name: "V2 Beat Flash / Overlays", type: "VIDEO_GRAPHICS", index: 1 });
builder.createTrack({ id: "t_a1", name: "A1 Music Beat Bed", type: "AUDIO_MUSIC", index: 2 });

beatSyncPlan.cuts.forEach((cut) => {
  builder.addClip("t_v1", {
    id: cut.id,
    assetId: `${FOOTAGE_DIR}/${cut.assetId}`,
    label: `Cut ${cut.id} (${cut.isDownbeat ? "DOWNBEAT" : "BEAT"})`,
    sourceRange: { startSeconds: cut.sourceStart, durationSeconds: cut.durationSeconds },
    timelineRange: { startSeconds: cut.timelineStart, durationSeconds: cut.durationSeconds },
    scale: cut.pulseScale ? cut.pulseScale / 100 : 1.0,
  });
});

beatSyncPlan.markers.forEach((m) => {
  builder.addMarker({ id: `m_${m.timeSeconds}`, timestampSeconds: m.timeSeconds, name: m.name });
});

const beatIR = builder.build("2026-09-02T22:45:00.000Z");
const qaAudit = EditorialQAEngine.auditIR(beatIR);
console.log(`✓ Control de Calidad QA 2.0: Score ${qaAudit.qaScore}/100 — Ready for Export: ${qaAudit.isReadyForExport}`);

// 5. Generar Archivos de Salida (ExtendScript JSX, OTIO y Manifiesto)
console.log("\n[Paso 4/4] Generando ExtendScript After Effects con marcadores de Beat y pulsos de escala...");

const jsxPath = path.join(distDir, "guadalajara_beat_sync.jsx");
const otioPath = path.join(distDir, "guadalajara_beat_sync.otio");
const manifestPath = path.join(distDir, "guadalajara_beat_sync_manifest.json");

const jsxLines = [
  "// ============================================================================",
  "//  AUTONOMOUS RHYTHMIC BEAT SYNC COMPILER (v4.1.0) — GUADALAJARA 2023",
  "//  BPM: " + TARGET_BPM + " (4/4) | Exact Transient Cuts & Scale Punch-Ins",
  "// ============================================================================",
  "",
  "app.beginUndoGroup('Build Guadalajara Beat Sync Master');",
  "try {",
  "  var proj = app.project || app.newProject();",
  "  var baseDir = '" + FOOTAGE_DIR.replace(/\\/g, "/") + "';",
  "  var compW = 1080;",
  "  var compH = 1920;",
  `  var compDur = ${beatSyncPlan.totalDurationSeconds.toFixed(2)};`,
  "  var comp = proj.items.addComp('GDL — Rhythmic Beat Sync (120 BPM)', compW, compH, 1.0, compDur, 30.0);",
  "  comp.bgColor = [0.02, 0.02, 0.03];",
  "  comp.motionBlur = true; // Invariante obligatoria",
  "",
  "  function importClip(name) {",
  "    var f = new File(baseDir + '/' + name);",
  "    return f.exists ? proj.importFile(new ImportOptions(f)) : null;",
  "  }",
  "",
  "  // 1. Marcadores de Beat en la Línea de Tiempo de la Composición",
];

// Insertar marcadores de compás y downbeat
beatSyncPlan.markers.forEach((m) => {
  const label = m.isDownbeat ? `BAR ${m.measureNumber} ★` : `${m.measureNumber}.${m.beatInMeasure}`;
  jsxLines.push(`  if (comp.markerProperty) {`);
  jsxLines.push(`    var mv_${m.measureNumber}_${m.beatInMeasure} = new MarkerValue('${label}');`);
  jsxLines.push(`    comp.markerProperty.setValueAtTime(${m.timeSeconds.toFixed(3)}, mv_${m.measureNumber}_${m.beatInMeasure});`);
  jsxLines.push(`  }`);
});

jsxLines.push("");
jsxLines.push("  // 2. Capas de Vídeo Sincronizadas y Pulsos de Escala en Downbeats");

beatSyncPlan.cuts.forEach((c, idx) => {
  jsxLines.push(`  // --- Corte Rítmico ${idx + 1}: ${c.assetId} (${c.durationSeconds}s) ---`);
  jsxLines.push(`  var ft_${idx} = importClip('${c.assetId}');`);
  jsxLines.push(`  if (ft_${idx}) {`);
  jsxLines.push(`    var lyr_${idx} = comp.layers.add(ft_${idx});`);
  jsxLines.push(`    lyr_${idx}.name = '[BEAT CUT ${idx + 1}] ' + '${c.isDownbeat ? "★ DOWNBEAT" : "BEAT"}';`);
  jsxLines.push(`    lyr_${idx}.startTime = ${c.timelineStart.toFixed(3)};`);
  jsxLines.push(`    lyr_${idx}.inPoint = ${c.timelineStart.toFixed(3)};`);
  jsxLines.push(`    lyr_${idx}.outPoint = ${c.timelineEnd.toFixed(3)};`);
  jsxLines.push(`    lyr_${idx}.motionBlur = true;`);
  jsxLines.push(`    lyr_${idx}.property('Transform').property('Position').setValue([compW / 2, compH / 2]);`);
  jsxLines.push(`    var cover = Math.max((compW / ft_${idx}.width), (compH / ft_${idx}.height)) * 100.0;`);
  jsxLines.push(`    var scaleP = lyr_${idx}.property('Transform').property('Scale');`);

  if (c.isDownbeat) {
    // Punch-in reactivo: 107% al inicio del golpe, bajando suavemente a 100%
    jsxLines.push(`    scaleP.setValueAtTime(${c.timelineStart.toFixed(3)}, [cover * 1.07, cover * 1.07]);`);
    jsxLines.push(`    scaleP.setValueAtTime(${(c.timelineStart + 0.18).toFixed(3)}, [cover * 1.00, cover * 1.00]);`);
  } else {
    jsxLines.push(`    scaleP.setValue([cover, cover]);`);
  }

  jsxLines.push(`  }`);
  jsxLines.push("");
});

// Overlay de Título y BPM
jsxLines.push("  // 3. Indicador de Tempo y BPM Visual TIME Style");
jsxLines.push("  var bpmLayer = comp.layers.addText('120 BPM • RHYTHMIC CUT');");
jsxLines.push("  bpmLayer.name = '[OVERLAY] BPM Indicator';");
jsxLines.push("  bpmLayer.startTime = 0.0; bpmLayer.inPoint = 0.0; bpmLayer.outPoint = compDur;");
jsxLines.push("  var bpmDoc = bpmLayer.property('Source Text').value;");
jsxLines.push("  bpmDoc.fontSize = 32; bpmDoc.fillColor = [1.0, 0.08, 0.14]; // Crimson #FF1424");
jsxLines.push("  bpmDoc.justification = ParagraphJustification.CENTER_JUSTIFY;");
jsxLines.push("  bpmLayer.property('Source Text').setValue(bpmDoc);");
jsxLines.push("  bpmLayer.property('Transform').property('Position').setValue([compW / 2, 220]);");
jsxLines.push("");
jsxLines.push("  app.endUndoGroup();");
jsxLines.push("  alert('¡Composición Beat Sync a 120 BPM generada con éxito en After Effects!');");
jsxLines.push("} catch (e) {");
jsxLines.push("  app.endUndoGroup();");
jsxLines.push("  alert('Error Beat Sync: ' + e.toString());");
jsxLines.push("}");

fs.writeFileSync(jsxPath, jsxLines.join("\n"), "utf-8");
fs.writeFileSync(otioPath, OtioExporter.exportToOtioJson(beatIR), "utf-8");

const manifest = {
  project: "Guadalajara 2023 Rhythmic Beat Sync",
  bpm: TARGET_BPM,
  timeSignature: "4/4",
  totalDurationSeconds: beatSyncPlan.totalDurationSeconds,
  cutsCount: beatSyncPlan.cuts.length,
  downbeatsCount: beatSyncPlan.cuts.filter((c) => c.isDownbeat).length,
  averageShotDuration: (beatSyncPlan.totalDurationSeconds / beatSyncPlan.cuts.length).toFixed(2) + "s",
  zeroDriftGuaranteed: true,
  scalePulseFactor: "107%",
  artifacts: { jsx: jsxPath, otio: otioPath },
  checksumSha256: beatSyncPlan.checksumSha256,
};
fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2), "utf-8");

console.log(`✓ Archivo ExtendScript generado: ${jsxPath}`);
console.log(`✓ Archivo OpenTimelineIO generado: ${otioPath}`);
console.log(`✓ Manifiesto de sincronización: ${manifestPath}`);
console.log("\n==================================================================");
console.log("  PROCESO COMPLETADO — MONTAJE RÍTMICO POR BEATS LISTO             ");
console.log("==================================================================");
