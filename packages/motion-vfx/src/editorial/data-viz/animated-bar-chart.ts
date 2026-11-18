import {
  Dataset,
  ValidationResult,
  NormalizedVisualizationData,
  VisualizationCompileContext,
  DataVisualizationCompiler,
  AxisDisclosure,
} from "./contracts.js";
import { BarChartNode, BarGeometryItem } from "./visualization-base.js";
import { validateCanonicalDataset } from "./validation.js";
import { normalizeRange } from "./normalization.js";
import { ProvenanceTracker } from "./provenance.js";
import { AnimatedBarChartCompiler as InternalCompiler } from "./animated-bar-chart-compiler.js";

export interface AnimatedBarChartConfig {
  orientation?: "VERTICAL" | "HORIZONTAL";
  animationDurationSeconds?: number;
  easing?: "linear" | "easeIn" | "easeOut" | "easeInOut" | "cubic";
  showValues?: boolean;
  showLabels?: boolean;
  showGrid?: boolean;
  showBaseline?: boolean;
  showUnits?: boolean;
  highlightIndex?: number;
  axisPolicy?: "ZERO_BASED" | "DATA_RANGE" | "EXPLICIT";
  minAxisValue?: number;
  maxAxisValue?: number;
}

/**
 * REQ-025 §8, §9 & §10: AnimatedBarChartCompiler
 * Compilador procedural y determinista de gráficos de barras animados.
 */
export class AnimatedBarChartCompiler implements DataVisualizationCompiler<Dataset, BarChartNode> {
  public readonly type = "BAR_CHART" as const;

  public validate(input: Dataset): ValidationResult {
    return validateCanonicalDataset(input);
  }

  public normalize(input: Dataset): NormalizedVisualizationData {
    const values = input.values.map((v) => v.value);
    let min = Math.min(...values);
    let max = Math.max(...values);
    if (min > 0) min = 0; // Default zero-based for bar chart (§23)

    const isConstant = min === max;
    const range = max - min;

    const normalizedPoints = input.values.map((v) => ({
      original: v,
      normalizedValue: normalizeRange(v.value, min, max),
      normalizedTime: v.timestamp !== undefined ? v.timestamp : undefined,
    }));

    return {
      minValue: min,
      maxValue: max,
      range,
      isConstant,
      normalizedPoints,
    };
  }

  public compile(
    input: Dataset | any,
    context: VisualizationCompileContext | any = {}
  ): any {
    // Si se pasa en formato de opciones o spec existente
    if (input && input.dataset && input.spec) {
      return InternalCompiler.compile(input);
    }
    if (input && input.columns && input.rows) {
      return InternalCompiler.compile({
        dataset: input,
        spec: context.spec ?? { categoryColumn: input.columns[0].key, valueColumns: [input.columns[1].key], orientation: context.orientation ?? "VERTICAL", showValues: true, sort: "INPUT" },
        ...context,
      });
    }

    const dataset: Dataset = input;
    const config: AnimatedBarChartConfig = context.config ?? context ?? {};
    const orientation = config.orientation ?? "VERTICAL";
    const width = context.width ?? 1920;
    const height = context.height ?? 1080;

    const norm = this.normalize(dataset);
    const bounds = { x: 100, y: 100, width: width - 200, height: height - 200 };

    const bars: BarGeometryItem[] = [];
    const count = dataset.values.length;
    const barSpacing = bounds.width / Math.max(1, count);
    const barWidth = barSpacing * 0.7;

    // Baseline calculation (§9)
    const zeroRatio = norm.range === 0 ? 0.5 : (0 - norm.minValue) / norm.range;
    const baselineY = bounds.y + bounds.height * (1 - zeroRatio);
    const baseline = {
      x1: bounds.x,
      y1: baselineY,
      x2: bounds.x + bounds.width,
      y2: baselineY,
    };

    let axisDisclosure: AxisDisclosure | undefined = undefined;
    if (config.axisPolicy === "DATA_RANGE") {
      axisDisclosure = {
        truncated: norm.minValue > 0,
        minimum: norm.minValue,
        maximum: norm.maxValue,
        policy: "DATA_RANGE",
        reason: "DATA_RANGE axis requested explicitly",
      };
    }

    for (let i = 0; i < count; i++) {
      const val = dataset.values[i];
      const isNegative = val.value < 0;
      const x = bounds.x + i * barSpacing + (barSpacing - barWidth) / 2;
      const barHeight = Math.abs(val.value / (norm.range || 1)) * bounds.height;
      const y = isNegative ? baselineY : baselineY - barHeight;

      bars.push({
        id: `bar_${i}`,
        category: val.category || val.label,
        label: val.label,
        value: val.value,
        normalizedValue: norm.normalizedPoints[i].normalizedValue,
        x,
        y,
        width: barWidth,
        height: Math.max(2, barHeight),
        isNegative,
        color: config.highlightIndex === i ? "#FF1424" : isNegative ? "#800008" : "#000000",
      });
    }

    const node: BarChartNode = {
      id: `chart_${dataset.id}`,
      type: "BAR_CHART",
      startTimeSeconds: context.startTimeSeconds ?? 0,
      durationSeconds: config.animationDurationSeconds ?? 5.0,
      bounds,
      orientation,
      baseline,
      bars,
      axisDisclosure,
      showGrid: config.showGrid ?? true,
      showLabels: config.showLabels ?? true,
      showValues: config.showValues ?? true,
      style: {
        primaryColor: "#000000",
        accentColor: "#FF1424",
        backgroundColor: "#FFFFFF",
        fontFamily: "Impact",
        fontWeight: 900,
        labelSize: 24,
        valueSize: 32,
      },
      provenance: ProvenanceTracker.createProvenance(dataset.id),
    };

    return node;
  }

  // Compatibilidad estática
  public static compile(params: any): any {
    const inst = new AnimatedBarChartCompiler();
    if (params.dataset && (params.dataset.values || params.dataset.rows)) {
      return inst.compile(params.dataset, params);
    }
    return InternalCompiler.compile(params);
  }
}
