import {
  VisualizationDataset,
  AnimatedBarChartConfig,
  VisualizationContext,
  VisualizationIR,
  VisualizationElement,
  VisualizationAnimation,
  DataSet,
  BarChartSpec,
  VisualizationCompilationResult,
} from "./types.js";
import { validateVisualizationDataset } from "./validation.js";
import { DEFAULT_VISUALIZATION_VIEWPORT, DEFAULT_VISUALIZATION_THEME } from "./constants.js";
import { computePlotArea } from "./geometry.js";
import { formatVisualizationNumber } from "./labels.js";
import { computeVisualizationChecksum } from "./checksum.js";
import { validateDataset as legacyValidateDataset } from "./dataset-validator.js";
import { normalizeDataset as legacyNormalizeDataset } from "./dataset-normalizer.js";
import { computeBarLayout } from "./layout-engine.js";
import { createBarId } from "./deterministic-id.js";
import {
  createGrowAnimation as legacyCreateGrowAnimation,
  createCounterAnimation as legacyCreateCounterAnimation,
} from "./animation-utils.js";
import { computeVisualizationChecksum as legacyComputeChecksum } from "./visualization-hash.js";
import { DataVisualizationValidationError } from "./errors.js";

/**
 * REQ-025 §11-§14: Compilador determinista de gráficos de barras animados vectoriales.
 */
export function compileAnimatedBarChart(
  dataset: VisualizationDataset | DataSet | any,
  configOrSpec: AnimatedBarChartConfig | BarChartSpec | any,
  context?: VisualizationContext
): VisualizationIR & VisualizationCompilationResult {
  // 1. Detección de firma canónica REQ-025 (VisualizationDataset con array 'points')
  if (dataset && Array.isArray(dataset.points)) {
    const valResult = validateVisualizationDataset(dataset);
    if (!valResult.valid) {
      const err = valResult.issues.find((i) => i.severity === "ERROR");
      throw new DataVisualizationValidationError(err?.message || "Dataset inválido");
    }

    const config: AnimatedBarChartConfig = {
      orientation: configOrSpec.orientation || "VERTICAL",
      sort: configOrSpec.sort || "INPUT",
      showValues: configOrSpec.showValues !== false,
      showLabels: configOrSpec.showLabels !== false,
      showGrid: configOrSpec.showGrid !== false,
      animationDurationSeconds: configOrSpec.animationDurationSeconds || 1.5,
      staggerSeconds: configOrSpec.staggerSeconds || 0.08,
      easing: configOrSpec.easing || "EASE_OUT",
    };

    // Invariante §2.1: Dataset inmutable (copia defensiva)
    let points = [...dataset.points];
    if (config.sort === "ASCENDING") {
      points.sort((a, b) => (a.value - b.value !== 0 ? a.value - b.value : a.label.localeCompare(b.label)));
    } else if (config.sort === "DESCENDING") {
      points.sort((a, b) => (b.value - a.value !== 0 ? b.value - a.value : a.label.localeCompare(b.label)));
    }

    const viewport = { ...DEFAULT_VISUALIZATION_VIEWPORT, ...context?.viewport };
    const theme = { ...DEFAULT_VISUALIZATION_THEME, ...context?.theme };
    const plot = computePlotArea(viewport);

    const values = points.map((p) => p.value);
    const minVal = Math.min(0, ...values);
    const maxVal = Math.max(0, ...values);
    const range = maxVal - minVal > 1e-12 ? maxVal - minVal : 1;

    const elements: VisualizationElement[] = [];
    const animations: VisualizationAnimation[] = [];

    // Fondo
    elements.push({
      id: "chart-bg",
      type: "RECT",
      x: 0,
      y: 0,
      width: viewport.width,
      height: viewport.height,
      fill: theme.backgroundColor,
      opacity: 1,
    });

    const N = Math.max(1, points.length);

    if (config.orientation === "VERTICAL") {
      const bandWidth = (plot.width / N) * 0.7;
      const step = plot.width / N;

      // Línea de cero (baseline)
      const zeroY = plot.bottom - ((0 - minVal) / range) * plot.height;

      elements.push({
        id: "axis-zero",
        type: "LINE",
        x: plot.x,
        y: Number(zeroY.toFixed(2)),
        width: plot.width,
        height: 0,
        stroke: theme.gridColor,
        strokeWidth: 2,
      });

      for (let i = 0; i < points.length; i++) {
        const p = points[i];
        const barX = plot.x + (i + 0.5) * step - bandWidth / 2;
        const normH = (Math.abs(p.value) / range) * plot.height;
        const barH = Math.max(2, normH);
        const barY = p.value >= 0 ? zeroY - barH : zeroY;

        const barId = `chart-bar-${String(i).padStart(3, "0")}`;
        const valId = `chart-val-${String(i).padStart(3, "0")}`;
        const lblId = `chart-lbl-${String(i).padStart(3, "0")}`;

        elements.push({
          id: barId,
          type: "BAR",
          x: Number(barX.toFixed(2)),
          y: Number(barY.toFixed(2)),
          width: Number(bandWidth.toFixed(2)),
          height: Number(barH.toFixed(2)),
          fill: p.value >= 0 ? theme.primaryColor : theme.negativeColor,
          opacity: 1,
          sourceId: p.id,
        });

        // Animación de barra
        const delay = Number((i * config.staggerSeconds).toFixed(4));
        const duration = Number(config.animationDurationSeconds.toFixed(4));

        animations.push({
          id: `anim-scale-${barId}`,
          elementId: barId,
          property: "scale",
          easing: config.easing,
          keyframes: [
            { timeSeconds: delay, value: 0 },
            { timeSeconds: delay + duration, value: 1 },
          ],
        });

        // Label
        if (config.showLabels) {
          elements.push({
            id: lblId,
            type: "LABEL",
            x: Number((barX + bandWidth / 2).toFixed(2)),
            y: Number((plot.bottom + 25).toFixed(2)),
            text: p.label,
            fill: theme.textColor,
            opacity: 1,
            sourceId: p.id,
          });
        }

        // Valor
        if (config.showValues) {
          const valY = p.value >= 0 ? barY - 15 : barY + barH + 20;
          const formatted = formatVisualizationNumber(p.value, {
            decimals: dataset.precision ?? 0,
            unit: p.unit ?? dataset.unit,
          });

          elements.push({
            id: valId,
            type: "COUNTER",
            x: Number((barX + bandWidth / 2).toFixed(2)),
            y: Number(valY.toFixed(2)),
            text: formatted,
            fill: theme.textColor,
            opacity: 1,
            sourceId: p.id,
          });

          animations.push({
            id: `anim-counter-${valId}`,
            elementId: valId,
            property: "text",
            easing: config.easing,
            keyframes: [
              { timeSeconds: delay, value: formatVisualizationNumber(0, { decimals: dataset.precision ?? 0 }) },
              { timeSeconds: delay + duration, value: formatted },
            ],
          });
        }
      }
    } else {
      // HORIZONTAL
      const bandHeight = (plot.height / N) * 0.7;
      const step = plot.height / N;
      const zeroX = plot.x + ((0 - minVal) / range) * plot.width;

      elements.push({
        id: "axis-zero",
        type: "LINE",
        x: Number(zeroX.toFixed(2)),
        y: plot.y,
        width: 0,
        height: plot.height,
        stroke: theme.gridColor,
        strokeWidth: 2,
      });

      for (let i = 0; i < points.length; i++) {
        const p = points[i];
        const barY = plot.y + (i + 0.5) * step - bandHeight / 2;
        const normW = (Math.abs(p.value) / range) * plot.width;
        const barW = Math.max(2, normW);
        const barX = p.value >= 0 ? zeroX : zeroX - barW;

        const barId = `chart-bar-${String(i).padStart(3, "0")}`;
        const valId = `chart-val-${String(i).padStart(3, "0")}`;
        const lblId = `chart-lbl-${String(i).padStart(3, "0")}`;

        elements.push({
          id: barId,
          type: "BAR",
          x: Number(barX.toFixed(2)),
          y: Number(barY.toFixed(2)),
          width: Number(barW.toFixed(2)),
          height: Number(bandHeight.toFixed(2)),
          fill: p.value >= 0 ? theme.primaryColor : theme.negativeColor,
          opacity: 1,
          sourceId: p.id,
        });

        const delay = Number((i * config.staggerSeconds).toFixed(4));
        const duration = Number(config.animationDurationSeconds.toFixed(4));

        animations.push({
          id: `anim-scale-${barId}`,
          elementId: barId,
          property: "scale",
          easing: config.easing,
          keyframes: [
            { timeSeconds: delay, value: 0 },
            { timeSeconds: delay + duration, value: 1 },
          ],
        });

        if (config.showLabels) {
          elements.push({
            id: lblId,
            type: "LABEL",
            x: Number((plot.x - 15).toFixed(2)),
            y: Number((barY + bandHeight / 2).toFixed(2)),
            text: p.label,
            fill: theme.textColor,
            opacity: 1,
            sourceId: p.id,
          });
        }

        if (config.showValues) {
          const valX = p.value >= 0 ? barX + barW + 15 : barX - 15;
          const formatted = formatVisualizationNumber(p.value, {
            decimals: dataset.precision ?? 0,
            unit: p.unit ?? dataset.unit,
          });

          elements.push({
            id: valId,
            type: "COUNTER",
            x: Number(valX.toFixed(2)),
            y: Number((barY + bandHeight / 2).toFixed(2)),
            text: formatted,
            fill: theme.textColor,
            opacity: 1,
            sourceId: p.id,
          });

          animations.push({
            id: `anim-counter-${valId}`,
            elementId: valId,
            property: "text",
            easing: config.easing,
            keyframes: [
              { timeSeconds: delay, value: formatVisualizationNumber(0, { decimals: dataset.precision ?? 0 }) },
              { timeSeconds: delay + duration, value: formatted },
            ],
          });
        }
      }
    }

    const ir: any = {
      id: `vis-barchart-${dataset.id}`,
      type: "BAR_CHART",
      viewport,
      theme,
      elements,
      animations,
      layers: [],
      metadata: {
        engineVersion: "4.0.0",
        requirementId: "REQ-025",
        datasetId: dataset.id,
        profileId: context?.editorialProfile ?? "TIME_EDITORIAL",
        sourceCount: points.length,
      },
      cognitiveMetadata: {
        activeElements: elements.length,
        textElements: elements.filter((e) => e.type === "TEXT").length,
        numericElements: elements.filter((e) => e.id.includes("val")).length,
        animationCount: animations.length,
      },
      pacingMetadata: {
        visualDurationSeconds: Number((config.animationDurationSeconds + points.length * config.staggerSeconds + 2.0).toFixed(2)),
        animationDurationSeconds: Number((config.animationDurationSeconds + points.length * config.staggerSeconds).toFixed(2)),
      },
      editorialIntensity: "MEDIUM",
      checksumSha256: "",
      // Compatibilidad polimórfica:
      success: true,
      errors: [],
      warnings: [],
    };

    ir.checksumSha256 = computeVisualizationChecksum(ir);
    ir.ir = ir;
    return ir;
  }

  // 2. Ruta legacy para pruebas preexistentes que usan DataSet + BarChartSpec
  const spec: BarChartSpec = configOrSpec;
  const legacyErrors = legacyValidateDataset(dataset, {
    requiredColumns: [spec.categoryColumn, spec.valueColumn],
    allowEmptyRows: false,
  });

  if (legacyErrors.some((e) => e.severity === "BLOCKING")) {
    return {
      success: false,
      errors: legacyErrors,
      warnings: [],
    } as any;
  }

  const normalized = legacyNormalizeDataset(dataset, spec.valueColumn, {
    nullPolicy: spec.nullPolicy ?? "REJECT",
  });

  let rows = [...normalized.rows];
  if (spec.sort === "ASCENDING") {
    rows.sort((a, b) => {
      const diff = Number(a[spec.valueColumn]) - Number(b[spec.valueColumn]);
      return Math.abs(diff) > 1e-6 ? diff : String(a[spec.categoryColumn]).localeCompare(String(b[spec.categoryColumn]));
    });
  } else if (spec.sort === "DESCENDING") {
    rows.sort((a, b) => {
      const diff = Number(b[spec.valueColumn]) - Number(a[spec.valueColumn]);
      return Math.abs(diff) > 1e-6 ? diff : String(a[spec.categoryColumn]).localeCompare(String(b[spec.categoryColumn]));
    });
  }

  if (spec.maxBars && spec.maxBars > 0 && rows.length > spec.maxBars) {
    rows = rows.slice(0, spec.maxBars);
  }

  const barInputs = rows.map((r, idx) => ({
    id: createBarId(spec.id, String(r[spec.categoryColumn]), idx, Number(r[spec.valueColumn])),
    category: String(r[spec.categoryColumn]),
    value: Number(r[spec.valueColumn]),
    normalizedValue: Number(r[`__normalized_${spec.valueColumn}`] ?? 0),
    index: idx,
  }));

  const bars = computeBarLayout({
    canvasWidth: spec.width,
    canvasHeight: spec.height,
    safeZone: spec.safeZone,
    bars: barInputs,
    orientation: spec.orientation,
  });

  const layers: any[] = [];
  layers.push({
    id: `${spec.id}_bg`,
    name: "DV::BACKGROUND",
    type: "SOLID",
    zIndex: 0,
    transform: { position: { x: 0, y: 0 }, scale: { x: 1, y: 1 }, rotation: 0, anchor: { x: 0, y: 0 } },
    opacity: 1,
    inPoint: spec.startTimeSeconds,
    outPoint: spec.startTimeSeconds + spec.durationSeconds,
    color: spec.style.backgroundColor,
  });

  for (let i = 0; i < bars.length; i++) {
    const bar = bars[i];
    const delay = spec.startTimeSeconds + i * (spec.animation.staggerSeconds ?? 0.05);
    const duration = spec.animation.entranceDurationSeconds;
    const growAnim = legacyCreateGrowAnimation("scaleY", 1.0, delay, duration, spec.animation.easing);

    layers.push({
      id: bar.id,
      name: `DV::BAR::${bar.category}`,
      type: "SHAPE",
      zIndex: i + 1,
      transform: { position: { x: bar.x, y: bar.y }, scale: { x: 1, y: 1 }, rotation: 0, anchor: { x: 0, y: 0 } },
      opacity: 1,
      geometry: { kind: "RECT", x: bar.x, y: bar.y, width: bar.width, height: bar.height, fillColor: spec.style.primaryColor },
      inPoint: delay,
      outPoint: spec.startTimeSeconds + spec.durationSeconds,
      bounds: bar.bounds ?? { x: bar.x, y: bar.y, width: bar.width, height: bar.height },
      fillColor: spec.style.primaryColor,
      animation: { properties: [growAnim] },
      animations: [growAnim],
    });

    if (spec.showLabels) {
      layers.push({
        id: `${bar.id}_label`,
        name: `DV::LABEL::${bar.category}`,
        type: "TEXT",
        zIndex: i + 10,
        transform: { position: { x: bar.x, y: bar.y }, scale: { x: 1, y: 1 }, rotation: 0, anchor: { x: 0.5, y: 0.5 } },
        opacity: 1,
        inPoint: delay,
        outPoint: spec.startTimeSeconds + spec.durationSeconds,
        text: { content: bar.category, fontFamily: spec.style.fontFamily, fontSize: 14, fontWeight: 500, fillColor: spec.style.textColor, tracking: 0, justification: "CENTER" },
        position: bar.labelPosition ?? { x: bar.x, y: bar.y },
      });
    }

    if (spec.showValues) {
      const cntAnim = legacyCreateCounterAnimation(bar.value, delay, duration, spec.animation.easing);
      layers.push({
        id: `${bar.id}_value`,
        name: `DV::VALUE::${bar.category}`,
        type: "TEXT",
        zIndex: i + 20,
        transform: { position: { x: bar.x, y: bar.y }, scale: { x: 1, y: 1 }, rotation: 0, anchor: { x: 0.5, y: 0.5 } },
        opacity: 1,
        inPoint: delay,
        outPoint: spec.startTimeSeconds + spec.durationSeconds,
        text: { content: String(bar.value), fontFamily: spec.style.fontFamily, fontSize: 16, fontWeight: 700, fillColor: spec.style.textColor, tracking: 0, justification: "CENTER" },
        position: bar.valuePosition ?? { x: bar.x, y: bar.y },
        animation: { properties: [cntAnim] },
        animations: [cntAnim],
      });
    }
  }

  const legacyIR: any = {
    id: spec.id,
    type: "ANIMATED_BAR_CHART",
    datasetId: dataset.id,
    durationSeconds: spec.durationSeconds,
    startTimeSeconds: spec.startTimeSeconds,
    width: spec.width,
    height: spec.height,
    viewport: {
      width: spec.width,
      height: spec.height,
      safeMarginTop: spec.safeZone.top,
      safeMarginRight: spec.safeZone.right,
      safeMarginBottom: spec.safeZone.bottom,
      safeMarginLeft: spec.safeZone.left,
    },
    theme: {
      backgroundColor: spec.style.backgroundColor,
      primaryColor: spec.style.primaryColor,
      secondaryColor: spec.style.secondaryColor,
      accentColor: spec.style.accentColor,
      textColor: spec.style.textColor,
      mutedTextColor: "#888888",
      gridColor: "#333333",
      negativeColor: "#FF4444",
      fontFamily: spec.style.fontFamily,
      fontWeight: spec.style.fontWeight,
    },
    elements: layers.map((l) => ({
      id: l.id,
      type: l.type === "SHAPE" ? "RECT" : l.type === "TEXT" ? "TEXT" : "RECT",
      x: l.bounds ? l.bounds.x : l.position ? l.position.x : 0,
      y: l.bounds ? l.bounds.y : l.position ? l.position.y : 0,
      width: l.bounds ? l.bounds.width : 50,
      height: l.bounds ? l.bounds.height : 20,
      fill: l.fillColor || spec.style.textColor,
      text: l.text,
      bounds: l.bounds || { x: 0, y: 0, width: 50, height: 20 },
    })),
    layers,
    animations: [],
    metadata: {
      engineVersion: "4.0.0",
      requirementId: "REQ-025",
      datasetId: dataset.id,
      profileId: "TIME_EDITORIAL",
      sourceCount: rows.length,
    },
    checksumSha256: "",
  };

  legacyIR.checksumSha256 = legacyComputeChecksum(legacyIR);

  return {
    success: true,
    ir: legacyIR,
    errors: [],
    warnings: [],
    metrics: {
      dataPointCount: rows.length,
      layerCount: layers.length,
      totalBars: bars.length,
      visibleBars: bars.length,
      clippedBars: 0,
      zeroCrossing: 0,
      pixelRange: { min: 0, max: spec.width },
    },
    ...legacyIR,
  };
}

export class AnimatedBarChartCompiler {
  public static compile(
    datasetOrOptions: any,
    config?: any,
    context?: any
  ): VisualizationIR & VisualizationCompilationResult {
    if (datasetOrOptions && !config && typeof datasetOrOptions === "object" && datasetOrOptions.dataset) {
      const ds = datasetOrOptions.dataset;
      const cfg = datasetOrOptions.config ?? {};
      const asp = datasetOrOptions.aspectRatio;
      const vp = asp === "9:16" ? { width: 1080, height: 1920 } : asp === "1:1" ? { width: 1080, height: 1080 } : { width: 1920, height: 1080 };
      return compileAnimatedBarChart(ds, cfg, { viewport: vp });
    }
    return compileAnimatedBarChart(datasetOrOptions, config, context);
  }
}


