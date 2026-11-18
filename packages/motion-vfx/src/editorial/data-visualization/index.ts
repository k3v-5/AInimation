import {
  DataSet,
  VisualizationSpec,
  VisualizationCompilationResult,
} from "./types.js";
import { compileAnimatedBarChart } from "./animated-bar-chart-compiler.js";
import { compileTrendLineGraph } from "./trend-line-graph-compiler.js";
import { generateBigStatCard } from "./big-stat-card-generator.js";
import { generateChronologyTimeline } from "./chronology-timeline-generator.js";

export * from "./types.js";
export * from "./errors.js";
export * from "./constants.js";
export * from "./validation.js";
export * from "./normalization.js";
export { normalizeDataset, DataNormalizer } from "./dataset-normalizer.js";
export * from "./scales.js";
export * from "./geometry.js";
export * from "./animation.js";
export * from "./labels.js";
export * from "./accessibility.js";
export * from "./checksum.js";
export * from "./visualization-engine.js";
export * from "./dataset-parser.js";
export * from "./dataset-validator.js";
export * from "./deterministic-id.js";
export * from "./color-utils.js";
export * from "./layout-engine.js";
export * from "./animated-bar-chart-compiler.js";
export * from "./trend-line-graph-compiler.js";
export * from "./big-stat-card-generator.js";
export * from "./chronology-timeline-generator.js";
export * from "./visualization-validator.js";
export * from "./visualization-jsx-compiler.js";

/**
 * REQ-025 §54: API unificada para compilación declarativa de visualizaciones de datos.
 */
export function compileVisualization(
  dataset: DataSet | null,
  spec: VisualizationSpec
): VisualizationCompilationResult {
  switch (spec.type) {
    case "ANIMATED_BAR_CHART": {
      if (!dataset) {
        return {
          success: false,
          errors: [
            {
              code: "DATASET_REQUIRED",
              message: "AnimatedBarChart requiere un dataset estructurado válido.",
              severity: "BLOCKING",
            },
          ],
          warnings: [],
        };
      }
      return compileAnimatedBarChart(dataset, spec);
    }
    case "TREND_LINE": {
      if (!dataset) {
        return {
          success: false,
          errors: [
            {
              code: "DATASET_REQUIRED",
              message: "TrendLine requiere un dataset estructurado válido.",
              severity: "BLOCKING",
            },
          ],
          warnings: [],
        };
      }
      return compileTrendLineGraph(dataset, spec);
    }
    case "BIG_STAT_CARD": {
      return generateBigStatCard(spec, dataset);
    }
    case "CHRONOLOGY_TIMELINE": {
      if (!dataset) {
        return {
          success: false,
          errors: [
            {
              code: "DATASET_REQUIRED",
              message: "ChronologyTimeline requiere un dataset estructurado válido.",
              severity: "BLOCKING",
            },
          ],
          warnings: [],
        };
      }
      return generateChronologyTimeline(dataset, spec);
    }
    default: {
      return {
        success: false,
        errors: [
          {
            code: "UNKNOWN_VISUALIZATION_TYPE",
            message: `Tipo de visualización desconocido: ${(spec as any)?.type}`,
            severity: "BLOCKING",
          },
        ],
        warnings: [],
      };
    }
  }
}
