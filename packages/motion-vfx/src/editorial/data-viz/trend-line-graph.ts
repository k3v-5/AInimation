import {
  Dataset,
  ValidationResult,
  NormalizedVisualizationData,
  VisualizationCompileContext,
  DataVisualizationCompiler,
  DataPointAnnotation,
} from "./contracts.js";
import { TrendLineNode } from "./visualization-base.js";
import { validateCanonicalDataset } from "./validation.js";
import { normalizeRange } from "./normalization.js";
import { ProvenanceTracker } from "./provenance.js";
import { TrendLineGraphCompiler as InternalCompiler } from "./trend-line-graph-compiler.js";

export interface TrendLineGraphConfig {
  animationDurationSeconds?: number;
  showPoints?: boolean;
  showLabels?: boolean;
  showGrid?: boolean;
  showArea?: boolean;
  scaleType?: "LINEAR" | "LOGARITHMIC";
  highlightExtrema?: boolean;
}

/**
 * REQ-025 §11, §12 & §13: TrendLineGraphCompiler
 * Compilador determinista de gráficos de líneas de tendencia y detección de extremos.
 */
export class TrendLineGraphCompiler implements DataVisualizationCompiler<Dataset, TrendLineNode> {
  public readonly type = "TREND_LINE" as const;

  public validate(input: Dataset): ValidationResult {
    return validateCanonicalDataset(input);
  }

  public normalize(input: Dataset): NormalizedVisualizationData {
    const values = input.values.map((v) => v.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const isConstant = min === max;
    const range = max - min;

    const timestamps = input.values
      .map((v, i) => v.timestamp ?? i)
      .sort((a, b) => a - b);
    const minTime = timestamps[0];
    const maxTime = timestamps[timestamps.length - 1];
    const timeRange = maxTime === minTime ? 1 : maxTime - minTime;

    const normalizedPoints = input.values.map((v, i) => {
      const t = v.timestamp ?? i;
      return {
        original: v,
        normalizedValue: normalizeRange(v.value, min, max),
        normalizedTime: (t - minTime) / timeRange,
      };
    });

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
    if (input && input.dataset && input.spec) {
      return InternalCompiler.compile(input);
    }
    if (input && input.columns && input.rows) {
      return InternalCompiler.compile({
        dataset: input,
        spec: context.spec ?? { xColumn: input.columns[0].key, yColumns: [input.columns[1].key], showPoints: true },
        ...context,
      });
    }

    const dataset: Dataset = input;
    const config: TrendLineGraphConfig = context.config ?? context ?? {};
    const width = context.width ?? 1920;
    const height = context.height ?? 1080;

    const norm = this.normalize(dataset);
    const bounds = { x: 100, y: 100, width: width - 200, height: height - 200 };

    // Geometría §12: x = normalizedTime * chartWidth, y = chartHeight - normalizedValue * chartHeight
    const points = norm.normalizedPoints.map((p, i) => {
      const x = bounds.x + (p.normalizedTime ?? 0) * bounds.width;
      const y = bounds.y + bounds.height - p.normalizedValue * bounds.height;
      return {
        id: `pt_${i}`,
        label: p.original.label,
        value: p.original.value,
        normalizedValue: p.normalizedValue,
        normalizedTime: p.normalizedTime ?? 0,
        x,
        y,
      };
    });

    // Detección de Extremos §13
    const extrema: DataPointAnnotation[] = [];
    if (config.highlightExtrema !== false && points.length > 0) {
      let minIdx = 0;
      let maxIdx = 0;
      for (let i = 1; i < points.length; i++) {
        if (points[i].value < points[minIdx].value) minIdx = i;
        if (points[i].value > points[maxIdx].value) maxIdx = i;
      }
      extrema.push({ type: "MINIMUM", index: minIdx, value: points[minIdx].value });
      if (maxIdx !== minIdx) {
        extrema.push({ type: "MAXIMUM", index: maxIdx, value: points[maxIdx].value });
      }

      // Máximos y mínimos locales
      for (let i = 1; i < points.length - 1; i++) {
        if (points[i].value > points[i - 1].value && points[i].value > points[i + 1].value) {
          if (i !== maxIdx) extrema.push({ type: "LOCAL_MAXIMUM", index: i, value: points[i].value });
        } else if (points[i].value < points[i - 1].value && points[i].value < points[i + 1].value) {
          if (i !== minIdx) extrema.push({ type: "LOCAL_MINIMUM", index: i, value: points[i].value });
        }
      }
    }

    // Path SVG
    let svgPath = "";
    if (points.length > 0) {
      svgPath = `M ${points[0].x.toFixed(2)} ${points[0].y.toFixed(2)}`;
      for (let i = 1; i < points.length; i++) {
        svgPath += ` L ${points[i].x.toFixed(2)} ${points[i].y.toFixed(2)}`;
      }
    }

    const node: TrendLineNode = {
      id: `trend_${dataset.id}`,
      type: "TREND_LINE",
      startTimeSeconds: context.startTimeSeconds ?? 0,
      durationSeconds: config.animationDurationSeconds ?? 6.0,
      bounds,
      points,
      svgPath,
      extrema,
      showGrid: config.showGrid ?? true,
      showPoints: config.showPoints ?? true,
      showArea: config.showArea ?? false,
      style: {
        primaryColor: "#000000",
        accentColor: "#FF1424",
        backgroundColor: "#FFFFFF",
        fontFamily: "Impact",
        fontWeight: 900,
        labelSize: 20,
        valueSize: 24,
      },
      provenance: ProvenanceTracker.createProvenance(dataset.id),
    };

    return node;
  }

  // Compatibilidad estática
  public static compile(params: any): any {
    const inst = new TrendLineGraphCompiler();
    if (params.dataset && (params.dataset.values || params.dataset.rows)) {
      return inst.compile(params.dataset, params);
    }
    return InternalCompiler.compile(params);
  }
}
