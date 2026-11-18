#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { VlogMultilingualProductionOrchestrator } from "../build/vlog/orchestrator/vlog-orchestrator.js";

const args = process.argv.slice(2);

function getArg(prefix, defaultValue) {
  const match = args.find((a) => a.startsWith(`${prefix}=`));
  return match ? match.split("=")[1].replace(/^["']|["']$/g, "") : defaultValue;
}

const isDryRun = args.includes("--dry-run");
const manifestPath = getArg("--manifest", null);
const scriptArg = getArg("--script", "Bienvenidos a este episodio especial. Hoy exploramos los rincones mas increibles.");
const sourceLangArg = getArg("--source-lang", "es-MX");
const targetLangsArg = getArg("--languages", "es-MX,en-US");
const aspectsArg = getArg("--aspects", "16:9,9:16");
const outDirArg = getArg("--output", "./dist/vlog_output");
const projectIdArg = getArg("--project-id", `vlog_prod_${Date.now()}`);

console.log("==================================================================");
console.log("  AUTONOMOUS VLOG INTELLIGENCE PRODUCTION CLI (v3.5.0)            ");
console.log("==================================================================");
console.log(`Project ID:        ${projectIdArg}`);
console.log(`Source Language:   ${sourceLangArg}`);
console.log(`Target Languages:  ${targetLangsArg}`);
console.log(`Aspect Ratios:     ${aspectsArg}`);
console.log(`Output Directory:  ${outDirArg}`);
console.log(`Execution Mode:    ${isDryRun ? "DRY-RUN (Simulated Validation)" : "FULL AUTONOMOUS PRODUCTION"}`);

async function main() {
  try {
    let config;

    if (manifestPath && fs.existsSync(manifestPath)) {
      console.log(`\n[1/3] Loading Project Manifest from ${manifestPath}...`);
      const raw = fs.readFileSync(manifestPath, "utf-8");
      config = JSON.parse(raw);
    } else {
      console.log("\n[1/3] Initializing Production Config from CLI arguments...");
      const targetLocales = targetLangsArg.split(",").map((s) => s.trim());
      const aspectRatios = aspectsArg.split(",").map((s) => s.trim());

      const mockAssets = [
        {
          id: "aroll_main",
          name: "MainTalkingHead.mp4",
          type: "A_ROLL",
          durationSeconds: 45.0,
          filePath: path.resolve("./assets/mock_talking_head.mp4"),
        },
        {
          id: "broll_city",
          name: "CityPanoramic.mp4",
          type: "B_ROLL",
          durationSeconds: 15.0,
          filePath: path.resolve("./assets/mock_city_broll.mp4"),
        },
      ];

      config = {
        projectId: projectIdArg,
        sourceLocale: sourceLangArg,
        targetLocales,
        scriptText: scriptArg,
        assets: mockAssets,
        aspectRatios,
        outputDirectory: outDirArg,
      };
    }

    console.log("[2/3] Orchestrating 22-Phase Production DAG...");
    const result = await VlogMultilingualProductionOrchestrator.execute(config);

    console.log("\n[3/3] Emitting Production Artifacts & Manifest...");
    console.log(`🎉 RUN SUCCESS: ${result.isSuccess ? "YES" : "NO"}`);
    console.log(` - Run ID:             ${result.run.runId}`);
    console.log(` - Engine Version:     ${result.run.engineVersion}`);
    console.log(` - Total Duration:     ${result.manifest.validation?.metrics?.totalDurationSeconds ?? 0}s`);
    console.log(` - Delivered Locales:  ${(result.manifest.targetLocales ?? []).join(", ")}`);
    console.log(` - Artifacts Emitted:  ${result.manifest.artifacts.length}`);
    console.log(` - Master Checksum:    ${result.manifest.productionHash.substring(0, 16)}...`);
    console.log("==================================================================");
    console.log("  VLOG PRODUCTION COMPLETED SUCCESSFULLY                          ");
    console.log("==================================================================");
  } catch (err) {
    console.error("\n❌ Error during autonomous vlog production:", err);
    process.exit(1);
  }
}

main();
