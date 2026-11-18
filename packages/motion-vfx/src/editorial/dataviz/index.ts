import { AfterEffectsDataVizCompiler } from "./compilers/after-effects-dataviz-compiler.js";
import { AnimatedBarChartCompiler } from "./animated-bar-chart-compiler.js";
import { BigStatCardGenerator } from "./big-stat-card-generator.js";
import { ChronologyTimelineGenerator } from "./chronology-timeline-generator.js";
import { DataVizValidator } from "./dataviz-validator.js";
import { TrendLineGraphCompiler } from "./trend-line-graph-compiler.js";
import {
  BarChartOptions,
  BigStatData,
  BigStatOptions,
  ChronologyOptions,
  DataSet,
  DataVisualizationEngine,
  DataVizCompilationResult,
  DataVizIR,
  TimelineEvent,
  TrendLineOptions,
} from "./types.js";

export * from "./types.js";
export * from "./constants.js";
export * from "./errors.js";
export * from "./validators.js";
export * from "./data-normalizer.js";
export * from "./scale-engine.js";
export * from "./number-formatter.js";
export * from "./color-resolver.js";
export * from "./layout-engine.js";
export * from "./safe-zone-engine.js";
export * from "./animation-planner.js";
export * from "./label-engine.js";
export * from "./axis-engine.js";
export * from "./legend-engine.js";
export * from "./dataviz-ir.js";
export * from "./dataviz-validator.js";
export * from "./dataviz-hash.js";
export * from "./animated-bar-chart-compiler.js";
export * from "./trend-line-graph-compiler.js";
export * from "./big-stat-card-generator.js";
export * from "./chronology-timeline-generator.js";
export * from "./compilers/after-effects-dataviz-compiler.js";

/**
 * REQ-025 §63, §64, §65: Main Data Visualization Engine Implementation.
 */
export class DataVisualizationEngineImpl implements DataVisualizationEngine {
  public compileBarChart(dataset: DataSet, options: BarChartOptions = {}): DataVizCompilationResult {
    const ir = AnimatedBarChartCompiler.compile(dataset, options);
    return this.produceResult(ir, options.executionMode ?? "COMPILE");
  }

  public compileTrendLine(dataset: DataSet, options: TrendLineOptions = {}): DataVizCompilationResult {
    const ir = TrendLineGraphCompiler.compile(dataset, options);
    return this.produceResult(ir, options.executionMode ?? "COMPILE");
  }

  public generateBigStat(data: BigStatData, options: BigStatOptions = {}): DataVizCompilationResult {
    const ir = BigStatCardGenerator.compile(data, options);
    return this.produceResult(ir, options.executionMode ?? "COMPILE");
  }

  public generateChronology(events: TimelineEvent[], options: ChronologyOptions = {}): DataVizCompilationResult {
    const ir = ChronologyTimelineGenerator.compile(events, options);
    return this.produceResult(ir, options.executionMode ?? "COMPILE");
  }

  private produceResult(ir: DataVizIR, mode: "VALIDATE_ONLY" | "IR_ONLY" | "COMPILE"): DataVizCompilationResult {
    const report = DataVizValidator.validate(ir);

    if (mode === "VALIDATE_ONLY") {
      return { ir, report };
    }

    if (mode === "IR_ONLY") {
      return { ir, report };
    }

    // COMPILE mode: emit deterministic JSX
    const jsx = AfterEffectsDataVizCompiler.compileToJsx(ir);
    return { ir, report, jsx };
  }
}

export const dataVisualizationEngine = new DataVisualizationEngineImpl();
