import {
  DataSet,
  VisualizationSpec,
  VisualizationIR,
  compileVisualization,
  validateDataset,
  parseCsv,
  parseJsonDataset,
  VisualizationJsxCompiler,
} from "../../editorial/data-visualization/index.js";

/**
 * REQ-025: Herramientas MCP para el Data Visualization Engine.
 */

export async function editorial_compile_data_visualization(params: {
  dataset?: DataSet | null;
  spec: VisualizationSpec;
}) {
  const result = compileVisualization(params.dataset ?? null, params.spec);
  return result;
}

export async function data_visualization_compile(params: {
  dataset?: any;
  visualizationSpec: any;
  editorialProfile?: string;
}) {
  const { compileDataVisualization } = await import("../../editorial/data-viz/index.js");
  const result = compileDataVisualization(params.dataset, params.visualizationSpec, {
    editorialProfile: params.editorialProfile,
  });
  return result;
}

export async function editorial_dataviz_to_jsx(params: {
  ir: VisualizationIR;
}) {
  const jsxScript = VisualizationJsxCompiler.compileToJsx(params.ir);
  return {
    success: true,
    jsxScript,
    checksumSha256: params.ir.checksumSha256,
  };
}

export async function editorial_parse_dataset(params: {
  format: "CSV" | "JSON";
  content: string;
  title?: string;
}) {
  const dataset =
    params.format === "CSV"
      ? parseCsv(params.content, { title: params.title })
      : parseJsonDataset(params.content);
  return {
    success: true,
    dataset,
  };
}

export async function editorial_validate_dataset(params: {
  dataset: DataSet;
  requiredColumns?: string[];
}) {
  const errors = validateDataset(params.dataset, {
    requiredColumns: params.requiredColumns,
  });
  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * REQ-025 §31: Canonical MCP Tools
 */

export async function data_viz_validate_dataset(params: {
  dataset: any;
}) {
  const { validateCanonicalDataset } = await import("../../editorial/data-viz/index.js");
  const result = validateCanonicalDataset(params.dataset);
  return result;
}

export async function data_viz_compile_bar_chart(params: {
  dataset: any;
  config?: any;
  width?: number;
  height?: number;
}) {
  const { AnimatedBarChartCompiler } = await import("../../editorial/data-viz/animated-bar-chart.js");
  const compiler = new AnimatedBarChartCompiler();
  const ir = compiler.compile(params.dataset, { config: params.config, width: params.width, height: params.height });
  return { ir };
}

export async function data_viz_compile_trend_line(params: {
  dataset: any;
  config?: any;
  width?: number;
  height?: number;
}) {
  const { TrendLineGraphCompiler } = await import("../../editorial/data-viz/trend-line-graph.js");
  const compiler = new TrendLineGraphCompiler();
  const ir = compiler.compile(params.dataset, { config: params.config, width: params.width, height: params.height });
  return { ir };
}

export async function data_viz_generate_stat_card(params: {
  dataset?: any;
  value?: number;
  label?: string;
  unit?: string;
  subtitle?: string;
}) {
  const { BigStatCardGenerator } = await import("../../editorial/data-viz/big-stat-card.js");
  const generator = new BigStatCardGenerator();
  const ir = generator.compile(params.dataset ?? params, { config: params });
  return { ir };
}

export async function data_viz_generate_timeline(params: {
  events: any[];
  config?: any;
}) {
  const { ChronologyTimelineGenerator } = await import("../../editorial/data-viz/chronology-timeline.js");
  const generator = new ChronologyTimelineGenerator();
  const ir = generator.compile({ events: params.events }, { config: params.config });
  return { ir };
}
