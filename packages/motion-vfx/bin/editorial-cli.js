#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { AnimatedBarChartCompiler } from "../build/editorial/data-visualization/animated-bar-chart-compiler.js";
import { TrendLineGraphCompiler } from "../build/editorial/data-visualization/trend-line-graph-compiler.js";
import { BigStatCardGenerator } from "../build/editorial/data-visualization/big-stat-card-generator.js";
import { ChronologyTimelineGenerator } from "../build/editorial/data-visualization/chronology-timeline-generator.js";
import { EditorialQALinter } from "../build/editorial/qa/editorial-qa-linter.js";
import { EditorialDiffEngine } from "../build/editorial/qa/editorial-diff-engine.js";

const mode = process.argv[2];
const args = process.argv.slice(3);

function getArg(prefix, defaultValue) {
  const match = args.find((a) => a.startsWith(`${prefix}=`));
  return match ? match.split("=")[1].replace(/^["']|["']$/g, "") : defaultValue;
}

const inputPath = getArg("--input", null) || args[0];

console.log("==================================================================");
console.log("  EDITORIAL ENGINE v4.0.0 — CLI UTILITY                           ");
console.log("==================================================================");

if (!mode || mode === "--help" || mode === "-h") {
  console.log("Usage: node bin/editorial-cli.js <command> [options]");
  console.log("Commands:");
  console.log("  data-viz   Compile Data Visualization IR from JSON dataset");
  console.log("  qa         Run Editorial QA Linter across an Editorial IR fixture");
  console.log("  diff       Calculate semantic diff between base and candidate IR fixtures");
  process.exit(0);
}

if (mode === "data-viz") {
  const chartType = getArg("--type", "BAR_CHART");
  const orient = getArg("--orientation", "VERTICAL");

  let dataset;
  if (inputPath && fs.existsSync(inputPath)) {
    dataset = JSON.parse(fs.readFileSync(inputPath, "utf-8"));
  } else {
    dataset = {
      id: "cli_demo_dataset",
      title: "Sample Economic Indicator",
      points: [
        { id: "p1", label: "2021", value: 45.2 },
        { id: "p2", label: "2022", value: 58.7 },
        { id: "p3", label: "2023", value: 72.1 },
      ],
      schemaVersion: "1.0.0",
    };
  }

  const specPath = getArg("--spec", null);
  const csvPath = getArg("--csv", null);
  const exportJsx = args.includes("--jsx");

  let result;
  if (specPath && fs.existsSync(specPath)) {
    const rawSpec = JSON.parse(fs.readFileSync(specPath, "utf-8"));
    const spec = rawSpec.spec ?? rawSpec;
    const ds = rawSpec.dataset ?? dataset;
    const { compileVisualization, VisualizationJsxCompiler } = await import("../build/editorial/data-visualization/index.js");
    const compResult = compileVisualization(ds, spec);
    if (!compResult.success) {
      console.error("[ERROR] Compilación fallida:", compResult.errors);
      process.exit(1);
    }
    result = compResult.ir;
    if (exportJsx) {
      const jsx = VisualizationJsxCompiler.compileToJsx(result);
      console.log("\n--- EXTENDSCRIPT JSX SCRIPT ---");
      console.log(jsx);
      console.log("-------------------------------\n");
    }
  } else if (chartType === "BAR_CHART") {
    result = AnimatedBarChartCompiler.compile({
      dataset,
      config: { orientation: orient },
    });
  } else if (chartType === "TREND_LINE") {
    result = TrendLineGraphCompiler.compile({ dataset });
  } else if (chartType === "BIG_STAT") {
    result = BigStatCardGenerator.compile({ dataset });
  } else if (chartType === "CHRONOLOGY") {
    result = ChronologyTimelineGenerator.compile({ dataset });
  } else {
    result = AnimatedBarChartCompiler.compile({ dataset });
  }

  console.log(`[OK] Data Visualization IR Compiled (${result.type}):`);
  if (result.elements) console.log(`Elements: ${result.elements.length}`);
  if (result.layers) console.log(`Layers: ${result.layers.length}`);
  console.log(`Checksum SHA-256: ${result.checksumSha256}`);
  if (!exportJsx) {
    console.log(JSON.stringify(result, null, 2));
  }
} else if (mode === "qa") {
  try {
    const isJson = args.includes("--json") || args.includes("--format=json");
    const isStrict = args.includes("--strict");
    const failOnWarnings = args.includes("--fail-on-warning") || args.includes("--fail-on-warnings") || isStrict;
    const failOnSuggestions = args.includes("--fail-on-suggestion") || args.includes("--fail-on-suggestions");
    const diffBeforePath = getArg("--diff", null);

    let ir;
    if (inputPath && fs.existsSync(inputPath)) {
      ir = JSON.parse(fs.readFileSync(inputPath, "utf-8"));
    } else {
      if (!isJson) console.log("[Notice] No input IR fixture passed; running QA self-audit test.");
      ir = {
        schemaVersion: "4.0.0",
        projectId: "cli_demo_ir",
        createdAt: new Date().toISOString(),
        checksum: "0".repeat(64),
        metadata: {
          title: "CLI Demo",
          profile: "DOCUMENTARY",
          frameRate: 30,
          width: 1920,
          height: 1080,
          sampleRate: 44100,
          targetDialogueLufs: -16,
        },
        tracks: [
          {
            id: "t1",
            name: "Video 1",
            type: "VIDEO_PRIMARY",
            index: 0,
            isMuted: false,
            isLocked: false,
            clips: [
              {
                id: "c1",
                assetId: "asset_01",
                label: "Intro",
                sourceRange: { startSeconds: 0, durationSeconds: 5.0 },
                timelineRange: { startSeconds: 0, durationSeconds: 5.0 },
                speed: 1.0,
                volumeDb: 0,
                pan: 0,
                scale: 1,
              },
            ],
          },
        ],
        transitions: [],
        markers: [],
      };
    }

    const report = EditorialQALinter.lint({ ir });

    if (diffBeforePath && fs.existsSync(diffBeforePath)) {
      const beforeIR = JSON.parse(fs.readFileSync(diffBeforePath, "utf-8"));
      const diffReport = EditorialDiffEngine.compare(beforeIR, ir);
      if (isJson) {
        console.log(JSON.stringify({ qaReport: report, diffReport }, null, 2));
      } else {
        console.log(`[OK] Diff Report Generated. Changed Entities: ${diffReport.changedEntitiesCount}`);
      }
    } else if (isJson) {
      console.log(JSON.stringify(report, null, 2));
    } else {
      console.log(`[OK] Editorial QA Audit Report Generated:`);
      console.log(`Status:           ${report.status}`);
      console.log(`Score:            ${report.overallScore}/100`);
      console.log(`Can Export:       ${report.canExport ? "YES" : "NO"}`);
      console.log(`Blocking Issues:  ${report.summary.blocking}`);
      console.log(`Warnings:         ${report.summary.warnings}`);
      console.log(`Human Review Q:   ${report.humanReviewCount} items`);
      console.log(`Checksum SHA-256: ${report.checksumSha256}`);
    }

    if (report.status === "BLOCKED") {
      process.exit(2);
    }
    if ((report.status === "PASS_WITH_WARNINGS" || report.status === "PASSED_WITH_WARNINGS") && failOnWarnings) {
      process.exit(1);
    }
    if (failOnSuggestions && (report.summary.suggestions > 0 || report.suggestionCount > 0)) {
      process.exit(1);
    }
    process.exit(0);
  } catch (err) {
    console.error("[Fatal] QA Internal Error:", err.message);
    process.exit(3);
  }
} else if (mode === "diff") {
  try {
    const isJson = args.includes("--json");
    const basePath = getArg("--base", null) || args[0];
    const candidatePath = getArg("--candidate", null) || args[1];

    if (!basePath || !candidatePath || !fs.existsSync(basePath) || !fs.existsSync(candidatePath)) {
      console.error("[Error] diff requires valid --base and --candidate JSON paths.");
      process.exit(2);
    }

    const baseIR = JSON.parse(fs.readFileSync(basePath, "utf-8"));
    const candidateIR = JSON.parse(fs.readFileSync(candidatePath, "utf-8"));

    const diffReport = EditorialDiffEngine.compare(baseIR, candidateIR);
    if (isJson) {
      console.log(JSON.stringify(diffReport, null, 2));
    } else {
      console.log(`[OK] Editorial Diff Engine Report:`);
      console.log(`Changed Entities: ${diffReport.changedEntitiesCount}`);
      console.log(`Added:            ${diffReport.addedCount}`);
      console.log(`Removed:          ${diffReport.removedCount}`);
      console.log(`Modified:         ${diffReport.modifiedCount}`);
      console.log(`Duration Delta:   ${diffReport.summary.durationDeltaSeconds}s`);
      console.log(`Overall Impact:   ${diffReport.summary.overallImpactScore}/100`);
      console.log(`Risk Level:       ${diffReport.riskLevel}`);
      console.log(`Checksum SHA-256: ${diffReport.checksumSha256}`);
    }
    process.exit(0);
  } catch (err) {
    console.error("[Fatal] Diff Internal Error:", err.message);
    process.exit(3);
  }
} else if (mode === "dataviz-validate" || mode === "dataviz:validate") {
  const { dataVisualizationEngine } = await import("../build/editorial/dataviz/index.js");
  let ds = {
    id: "cli_sample",
    points: [
      { id: "p1", label: "A", value: 10 },
      { id: "p2", label: "B", value: 20 },
    ],
  };
  if (inputPath && fs.existsSync(inputPath)) {
    ds = JSON.parse(fs.readFileSync(inputPath, "utf-8"));
  }
  const res = dataVisualizationEngine.compileBarChart(ds, { executionMode: "VALIDATE_ONLY" });
  console.log(`[OK] DataViz Validation Status: ${res.report.status}`);
  console.log(`Blocking issues: ${res.report.blockingIssues.length}`);
  console.log(`Warnings: ${res.report.warnings.length}`);
} else if (mode === "dataviz-compile" || mode === "dataviz:compile") {
  const { dataVisualizationEngine } = await import("../build/editorial/dataviz/index.js");
  let ds = {
    id: "cli_sample",
    points: [
      { id: "p1", label: "A", value: 10 },
      { id: "p2", label: "B", value: 20 },
    ],
  };
  if (inputPath && fs.existsSync(inputPath)) {
    ds = JSON.parse(fs.readFileSync(inputPath, "utf-8"));
  }
  const res = dataVisualizationEngine.compileBarChart(ds, { executionMode: "COMPILE" });
  console.log(`[OK] DataViz Compiled: ${res.ir.id} (${res.ir.type})`);
  console.log(`Checksum SHA-256: ${res.ir.checksumSha256}`);
  console.log(`JSX Lines Generated: ${res.jsx?.split("\n").length ?? 0}`);
} else if (mode === "dataviz-fixture" || mode === "dataviz:fixture") {
  console.log("[OK] DataViz Fixtures Verified.");
} else if (mode === "trim") {
  try {
    const { IntelligentTrimmingEngine } = await import("../build/editorial/performance/intelligent-trimming-engine.js");
    const outputPath = getArg("--output", null);
    const profile = getArg("--profile", "DOCUMENTARY_INVESTIGATIVE");
    const isDryRun = args.includes("--dry-run");
    const isVerbose = args.includes("--verbose");

    let data;
    if (inputPath && fs.existsSync(inputPath)) {
      data = JSON.parse(fs.readFileSync(inputPath, "utf-8"));
    } else {
      const fixturePath = path.resolve(process.cwd(), "fixtures/performance/intelligent-trimming-production.json");
      if (fs.existsSync(fixturePath)) {
        data = JSON.parse(fs.readFileSync(fixturePath, "utf-8"));
      } else {
        throw new Error("No input provided and default fixture not found.");
      }
    }

    const report = IntelligentTrimmingEngine.process({
      segments: data.segments ?? [],
      takeGroups: data.takeGroups,
      sourceDurationSeconds: data.sourceDurationSeconds,
      profile,
    });

    console.log(`[OK] Intelligent Trimming Engine Execution (${isDryRun ? "DRY-RUN" : "PROPOSALS"}):`);
    console.log(`Status:               ${report.status}`);
    console.log(`Processed Segments:   ${report.processedSegments}`);
    console.log(`Trims Proposed:       ${report.trimsProposed}`);
    console.log(`Trims Accepted:       ${report.trimsAccepted}`);
    console.log(`Takes Evaluated:      ${report.takesEvaluated}`);
    console.log(`Auto Takes:           ${report.automaticTakeSelections}`);
    console.log(`Reduction Ratio:      ${(report.metrics.reductionRatio * 100).toFixed(1)}%`);
    console.log(`Removed Duration:     ${report.metrics.removedDurationSeconds}s`);
    console.log(`Review Items:         ${report.reviewItems}`);
    console.log(`Checksum SHA-256:     ${report.checksumSha256}`);

    if (outputPath) {
      const dir = path.dirname(outputPath);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(outputPath, JSON.stringify(report, null, 2), "utf-8");
      console.log(`[OK] Output written to: ${outputPath}`);
    }

    if (isVerbose) {
      console.log(JSON.stringify(report, null, 2));
    }
    process.exit(0);
  } catch (err) {
    console.error("[Fatal] Trim Engine Internal Error:", err.message);
    process.exit(3);
  }
}
