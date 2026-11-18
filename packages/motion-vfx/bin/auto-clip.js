#!/usr/bin/env node
import path from "node:path";
import { AutoClipPipelineOrchestrator } from "../build/automation/pipeline/AutoClipPipelineOrchestrator.js";

const args = process.argv.slice(2);
const inputArg = args.find(a => a.startsWith("--input="))?.split("=")[1] ?? "E:/Respaldo/Guadalajara junio 23-20231019T123606Z-001/Guadalajara junio 23/20230620_210856.mp4";
const styleArg = args.find(a => a.startsWith("--style="))?.split("=")[1] ?? "hormozi_cashflow_captions";
const outDirArg = args.find(a => a.startsWith("--output="))?.split("=")[1] ?? "./dist/autoclip";

console.log("==================================================================");
console.log("  AUTONOMOUS AUTO-CLIP PIPELINE — LONG-TO-SHORTS FACTORY          ");
console.log("==================================================================");
console.log(`Input Video: ${inputArg}`);
console.log(`Style Preset: ${styleArg}`);
console.log(`Output Directory: ${outDirArg}`);

try {
  const result = AutoClipPipelineOrchestrator.run({
    inputVideoPath: inputArg,
    stylePreset: styleArg,
    outputDir: outDirArg,
    topK: 3,
    projectName: "Guadalajara_AutoShorts",
  });

  console.log(`\n🎉 EXITOSA GENERACIÓN DE ${result.totalClipsGenerated} CLIPS VIRALES:`);
  for (const c of result.clips) {
    console.log(` - Clip #${c.clipIndex}: Duración ${c.clipData.duration}s | Score Viral: ${c.clipData.viralityIndex}/100`);
    console.log(`   JSX Script: ${c.jsxScriptPath}`);
    console.log(`   Título Sugerido: ${c.youtubePackage.recommendedTitle}`);
  }
} catch (err) {
  console.error("Error en el pipeline de auto-clip:", err);
  process.exit(1);
}
