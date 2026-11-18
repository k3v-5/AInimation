import {
  DataVisualizationDataset,
  VisualizationSpec,
  DataVisualizationCompilationResult,
  DataVisualizationDiagnostic,
  DataVisualizationIR,
} from "./types.js";
import { validateDataset } from "./validation.js";
import { normalizeDataset } from "./normalization.js";
import { AnimatedBarChartCompiler } from "./animated-bar-chart-compiler.js";
import { TrendLineGraphCompiler } from "./trend-line-graph-compiler.js";
import { BigStatCardGenerator } from "./big-stat-card-generator.js";
import { ChronologyTimelineGenerator } from "./chronology-timeline-generator.js";
import { DataVisualizationError } from "./errors.js";

export * from "./types.js";
export * from "./schema.js";
export * from "./errors.js";
export * from "./validation.js";
export * from "./normalization.js";
export * from "./statistics.js";
export * from "./scales.js";
export * from "./formatters.js";
export * from "./color-mapping.js";
export * from "./layout.js";
export * from "./animation.js";
export * from "./dataset-hash.js";
export * from "./contracts.js";
export type { ScaleType } from "./types.js";
export type { ScaleType as CanonicalScaleType } from "./contracts.js";
export * from "./number-formatter.js";
export * from "./provenance.js";
export * from "./visualization-base.js";
export type { AnimatedBarChartConfig } from "./animated-bar-chart.js";
export type { TrendLineGraphConfig } from "./trend-line-graph.js";
export type { BigStatConfig } from "./big-stat-card.js";
export type { ChronologyTimelineConfig } from "./chronology-timeline.js";

export {
  AnimatedBarChartCompiler,
  TrendLineGraphCompiler,
  BigStatCardGenerator,
  ChronologyTimelineGenerator,
  validateDataset,
  normalizeDataset,
};

/**
 * REQ-025 §31 & §49: API pública unificada de compilación declarativa de visualizaciones de datos.
 */
export function compileDataVisualization(
  dataset: DataVisualizationDataset | null | undefined,
  spec: VisualizationSpec,
  options: {
    editorialProfile?: string;
    width?: number;
    height?: number;
  } = {}
): DataVisualizationCompilationResult {
  const diagnostics: DataVisualizationDiagnostic[] = [];

  try {
    // 1. Validar dataset si es requerido por el tipo de visualización
    if (spec.type === "BAR_CHART" || spec.type === "TREND_LINE") {
      if (!dataset) {
        throw new DataVisualizationError({
          code: "DATASET_EMPTY",
          message: `El tipo de visualización '${spec.type}' requiere un dataset tabular obligatorio.`,
        });
      }
      const datasetDiags = validateDataset(dataset);
      diagnostics.push(...datasetDiags);
      const blocking = datasetDiags.find((d) => d.severity === "ERROR");
      if (blocking) {
        throw new DataVisualizationError({
          code: blocking.code as any,
          message: blocking.message,
          path: blocking.path,
        });
      }
    }

    let ir: DataVisualizationIR;

    // 2. Despachar al compilador correspondiente
    switch (spec.type) {
      case "BAR_CHART": {
        ir = AnimatedBarChartCompiler.compile({
          dataset: dataset!,
          spec: spec.spec,
          editorialProfile: options.editorialProfile,
          width: options.width,
          height: options.height,
        });
        break;
      }
      case "TREND_LINE": {
        ir = TrendLineGraphCompiler.compile({
          dataset: dataset!,
          spec: spec.spec,
          editorialProfile: options.editorialProfile,
          width: options.width,
          height: options.height,
        });
        break;
      }
      case "BIG_STAT": {
        ir = BigStatCardGenerator.compile({
          dataset: dataset ?? null,
          spec: spec.spec,
          editorialProfile: options.editorialProfile,
          width: options.width,
          height: options.height,
        });
        break;
      }
      case "CHRONOLOGY": {
        ir = ChronologyTimelineGenerator.compile({
          spec: spec.spec,
          editorialProfile: options.editorialProfile,
          width: options.width,
          height: options.height,
        });
        break;
      }
      default: {
        throw new DataVisualizationError({
          code: "UNSUPPORTED_CHART",
          message: `Tipo de visualización '${(spec as any).type}' no soportado.`,
        });
      }
    }

    return {
      status: "SUCCESS",
      visualization: ir,
      diagnostics,
      checksumSha256: ir.checksumSha256,
    };
  } catch (err: any) {
    diagnostics.push({
      severity: "ERROR",
      code: err.code ?? "COMPILATION_ERROR",
      message: err.message ?? String(err),
      path: err.path,
    });
    return {
      status: "FAILED",
      diagnostics,
    };
  }
}
