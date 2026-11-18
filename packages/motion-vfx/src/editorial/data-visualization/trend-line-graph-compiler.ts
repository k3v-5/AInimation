import {
  VisualizationDataset,
  TrendLineGraphConfig,
  VisualizationContext,
  VisualizationIR,
  VisualizationElement,
  VisualizationAnimation,
  DataSet,
  TrendLineSpec,
  VisualizationCompilationResult,
} from "./types.js";
import { validateVisualizationDataset } from "./validation.js";
import { DEFAULT_VISUALIZATION_VIEWPORT, DEFAULT_VISUALIZATION_THEME, EPSILON } from "./constants.js";
import { computePlotArea } from "./geometry.js";
import { formatVisualizationNumber } from "./labels.js";
import { computeVisualizationChecksum } from "./checksum.js";
import { validateDataset as legacyValidateDataset } from "./dataset-validator.js";
import { resolveSafeArea } from "./layout-engine.js";
import { createTrendPointId } from "./deterministic-id.js";
import { createStrokeWriteOnAnimation, createOpacityEntranceExit } from "./animation-utils.js";
import { computeVisualizationChecksum as legacyComputeChecksum } from "./visualization-hash.js";
import { DataVisualizationValidationError } from "./errors.js";

/**
 * REQ-025 §15-§18: Compilador determinista de gráficos de líneas de tendencia.
 */
export function compileTrendLineGraph(
  dataset: VisualizationDataset | DataSet | any,
  configOrSpec: TrendLineGraphConfig | TrendLineSpec | any,
  context?: VisualizationContext
): VisualizationIR & VisualizationCompilationResult {
  // 1. Detección de firma canónica REQ-025
  if (dataset && Array.isArray(dataset.points)) {
    const valResult = validateVisualizationDataset(dataset);
    if (!valResult.valid) {
      const err = valResult.issues.find((i) => i.severity === "ERROR");
      throw new DataVisualizationValidationError(err?.message || "Dataset inválido");
    }

    const config: TrendLineGraphConfig = {
      showPoints: configOrSpec.showPoints !== false,
      showLabels: configOrSpec.showLabels !== false,
      showGrid: configOrSpec.showGrid !== false,
      showAreaFill: configOrSpec.showAreaFill || false,
      animationDurationSeconds: configOrSpec.animationDurationSeconds || 2.0,
      lineWidth: configOrSpec.lineWidth || 4,
      pointRadius: configOrSpec.pointRadius || 6,
      smoothing: configOrSpec.smoothing || "NONE",
    };

    // Invariante §2.1 & §16: Orden temporal sobre copia
    let points = [...dataset.points];
    const hasTimestamps = points.some((p) => p.timestamp !== undefined);
    if (hasTimestamps) {
      points.sort((a, b) => (a.timestamp ?? 0) - (b.timestamp ?? 0));
    }

    const viewport = { ...DEFAULT_VISUALIZATION_VIEWPORT, ...context?.viewport };
    const theme = { ...DEFAULT_VISUALIZATION_THEME, ...context?.theme };
    const plot = computePlotArea(viewport);

    const values = points.map((p) => p.value);
    const minVal = Math.min(...values);
    const maxVal = Math.max(...values);
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
    const stepX = N > 1 ? plot.width / (N - 1) : 0;

    // Calcular coordenadas de la polilínea P0 -> P1 -> ... -> Pn
    const chartPoints: Array<{ x: number; y: number; id: string; label: string; value: number }> = [];

    for (let i = 0; i < points.length; i++) {
      const p = points[i];
      const px = N > 1 ? plot.x + i * stepX : plot.x + plot.width / 2;
      const py = plot.bottom - ((p.value - minVal) / range) * plot.height;

      chartPoints.push({
        x: Number(px.toFixed(2)),
        y: Number(py.toFixed(2)),
        id: p.id,
        label: p.label,
        value: p.value,
      });
    }

    // Cálculo de longitud acumulada para write-on proporcional (§18)
    let totalLength = 0;
    for (let i = 1; i < chartPoints.length; i++) {
      const dx = chartPoints[i].x - chartPoints[i - 1].x;
      const dy = chartPoints[i].y - chartPoints[i - 1].y;
      totalLength += Math.hypot(dx, dy);
    }
    totalLength = Math.max(1, totalLength);

    // Path de la línea de tendencia
    const pathCommands = chartPoints.map((cp, idx) => `${idx === 0 ? "M" : "L"} ${cp.x} ${cp.y}`).join(" ");

    elements.push({
      id: "trend-line-stroke",
      type: "LINE_SEGMENT",
      x: 0,
      y: 0,
      width: plot.width,
      height: plot.height,
      stroke: theme.primaryColor,
      strokeWidth: config.lineWidth,
      fill: "none",
      pathData: pathCommands,
      opacity: 1,
    });

    animations.push({
      id: "anim-writeon-trend-line",
      elementId: "trend-line-stroke",
      property: "trimPathEnd",
      easing: "EASE_OUT",
      keyframes: [
        { timeSeconds: 0, value: 0 },
        { timeSeconds: Number(config.animationDurationSeconds.toFixed(4)), value: 100 },
      ],
    });

    // Puntos y labels
    let accumLength = 0;
    for (let i = 0; i < chartPoints.length; i++) {
      const cp = chartPoints[i];
      if (i > 0) {
        accumLength += Math.hypot(cp.x - chartPoints[i - 1].x, cp.y - chartPoints[i - 1].y);
      }
      const pointTime = (accumLength / totalLength) * config.animationDurationSeconds;

      if (config.showPoints) {
        const ptId = `trend-point-${String(i).padStart(3, "0")}`;
        elements.push({
          id: ptId,
          type: "KEY_POINT",
          x: cp.x,
          y: cp.y,
          width: config.pointRadius * 2,
          height: config.pointRadius * 2,
          fill: theme.textColor,
          stroke: theme.primaryColor,
          strokeWidth: 2,
          opacity: 1,
          sourceId: cp.id,
        });

        animations.push({
          id: `anim-fade-${ptId}`,
          elementId: ptId,
          property: "opacity",
          easing: "EASE_OUT",
          keyframes: [
            { timeSeconds: Number(Math.max(0, pointTime - 0.1).toFixed(4)), value: 0 },
            { timeSeconds: Number(pointTime.toFixed(4)), value: 1 },
          ],
        });
      }

      if (config.showLabels) {
        const lblId = `trend-lbl-${String(i).padStart(3, "0")}`;
        elements.push({
          id: lblId,
          type: "TEXT",
          x: cp.x,
          y: cp.y - 15,
          text: formatVisualizationNumber(cp.value, { decimals: dataset.precision ?? 0, unit: dataset.unit }),
          fill: theme.textColor,
          opacity: 1,
          sourceId: cp.id,
        });
      }
    }

    const ir: any = {
      id: `vis-trend-${dataset.id}`,
      type: "TREND_LINE",
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
        numericElements: elements.filter((e) => e.id.includes("lbl")).length,
        animationCount: animations.length,
      },
      pacingMetadata: {
        visualDurationSeconds: Number((config.animationDurationSeconds + 2.0).toFixed(2)),
        animationDurationSeconds: Number(config.animationDurationSeconds.toFixed(2)),
      },
      editorialIntensity: "HIGH",
      checksumSha256: "",
      success: true,
      errors: [],
      warnings: [],
    };

    ir.checksumSha256 = computeVisualizationChecksum(ir);
    ir.ir = ir;
    return ir;
  }

  // 2. Ruta legacy para DataSet + TrendLineSpec
  const spec: TrendLineSpec = configOrSpec;
  const legacyErrors = legacyValidateDataset(dataset, {
    requiredColumns: [spec.xColumn, spec.yColumn],
    allowEmptyRows: false,
  });

  if (legacyErrors.some((e) => e.severity === "BLOCKING")) {
    return {
      success: false,
      errors: legacyErrors,
      warnings: [],
    } as any;
  }

  const rawPoints: Array<{ x: number; y: number; originalX: any; originalY: any }> = [];
  for (let r = 0; r < dataset.rows.length; r++) {
    const row = dataset.rows[r];
    const xVal = row[spec.xColumn];
    const yVal = row[spec.yColumn];

    if (xVal === null || xVal === undefined || yVal === null || yVal === undefined) {
      if (spec.nullPolicy === "SKIP") continue;
      if (spec.nullPolicy === "ZERO") {
        rawPoints.push({ x: 0, y: 0, originalX: xVal, originalY: yVal });
        continue;
      }
    }

    let parsedX: number;
    if (typeof xVal === "number") {
      parsedX = xVal;
    } else {
      const ts = Date.parse(String(xVal));
      parsedX = isNaN(ts) ? r : ts;
    }

    const parsedY = Number(yVal);
    if (!Number.isFinite(parsedY)) continue;

    rawPoints.push({ x: parsedX, y: parsedY, originalX: xVal, originalY: yVal });
  }

  rawPoints.sort((a, b) => a.x - b.x);

  const safeArea = resolveSafeArea(spec.width, spec.height, spec.safeZone);

  let minY = Infinity;
  let maxY = -Infinity;
  let minX = Infinity;
  let maxX = -Infinity;

  for (const pt of rawPoints) {
    if (pt.y < minY) minY = pt.y;
    if (pt.y > maxY) maxY = pt.y;
    if (pt.x < minX) minX = pt.x;
    if (pt.x > maxX) maxX = pt.x;
  }

  if (Math.abs(maxY - minY) < EPSILON) {
    minY = minY - 1;
    maxY = maxY + 1;
  }
  if (Math.abs(maxX - minX) < EPSILON) {
    minX = minX - 1;
    maxX = maxX + 1;
  }

  const screenPoints = rawPoints.map((pt, idx) => {
    const normX = (pt.x - minX) / (maxX - minX);
    const normY = (pt.y - minY) / (maxY - minY);
    const sx = safeArea.left + normX * safeArea.width;
    const sy = safeArea.top + (1 - normY) * safeArea.height;

    return {
      id: createTrendPointId(spec.id, idx, pt.x, pt.y),
      screenX: Number(sx.toFixed(2)),
      screenY: Number(sy.toFixed(2)),
      value: pt.y,
      originalX: pt.originalX,
      originalY: pt.originalY,
    };
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

  const isSmooth = spec.interpolation === "SMOOTH";
  const commands: any[] = [];
  for (let idx = 0; idx < screenPoints.length; idx++) {
    const pt = screenPoints[idx];
    if (idx === 0) {
      commands.push({ type: "M", x: pt.screenX, y: pt.screenY });
    } else if (isSmooth) {
      const prev = screenPoints[idx - 1];
      const dx = (pt.screenX - prev.screenX) / 3;
      commands.push({
        type: "C",
        cp1x: Number((prev.screenX + dx).toFixed(2)),
        cp1y: prev.screenY,
        cp2x: Number((pt.screenX - dx).toFixed(2)),
        cp2y: pt.screenY,
        x: pt.screenX,
        y: pt.screenY,
      });
    } else {
      commands.push({ type: "L", x: pt.screenX, y: pt.screenY });
    }
  }

  const pathCommands = commands
    .map((c) => (c.type === "C" ? `C ${c.cp1x} ${c.cp1y} ${c.cp2x} ${c.cp2y} ${c.x} ${c.y}` : `${c.type} ${c.x} ${c.y}`))
    .join(" ");
  const writeOn = createStrokeWriteOnAnimation(spec.startTimeSeconds, spec.animation.entranceDurationSeconds, spec.animation.easing);

  layers.push({
    id: `${spec.id}_stroke`,
    name: "DV::TREND::PATH",
    type: "SHAPE",
    zIndex: 1,
    transform: { position: { x: 0, y: 0 }, scale: { x: 1, y: 1 }, rotation: 0, anchor: { x: 0, y: 0 } },
    opacity: 1,
    inPoint: spec.startTimeSeconds,
    outPoint: spec.startTimeSeconds + spec.durationSeconds,
    geometry: { kind: "PATH", commands },
    pathData: pathCommands,
    strokeColor: spec.style.primaryColor,
    strokeWidth: 4,
    animation: { properties: [writeOn] },
    animations: [writeOn],
  });

  const gridSteps = 3;
  for (let g = 0; g <= gridSteps; g++) {
    const gy = safeArea.top + (g / gridSteps) * safeArea.height;
    layers.push({
      id: `${spec.id}_grid_${g}`,
      name: `DV::GRID::${g}`,
      type: "LINE",
      zIndex: 2,
      transform: { position: { x: safeArea.left, y: gy }, scale: { x: 1, y: 1 }, rotation: 0, anchor: { x: 0, y: 0 } },
      opacity: 0.3,
      line: { x1: 0, y1: 0, x2: safeArea.width, y2: 0, strokeColor: (spec.style as any).gridColor || "#333333", strokeWidth: 1 },
    });
  }

  for (let idx = 0; idx < screenPoints.length; idx++) {
    const pt = screenPoints[idx];
    const isExtreme = pt.value === minY || pt.value === maxY;
    layers.push({
      id: pt.id,
      name: `DV::TREND::POINT::${idx}`,
      type: "SHAPE",
      zIndex: 10 + idx,
      transform: { position: { x: pt.screenX, y: pt.screenY }, scale: { x: 1, y: 1 }, rotation: 0, anchor: { x: 0.5, y: 0.5 } },
      opacity: 1,
      geometry: { kind: "CIRCLE", radius: isExtreme ? 8 : 5, fillColor: spec.style.primaryColor },
    });
  }

  const legacyIR: any = {
    id: spec.id,
    type: "TREND_LINE",
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
    elements: screenPoints.map((sp) => ({
      id: sp.id,
      type: "CIRCLE",
      x: sp.screenX,
      y: sp.screenY,
      width: 10,
      height: 10,
      fill: spec.style.textColor,
      stroke: spec.style.primaryColor,
    })),
    layers,
    animations: [],
    metadata: {
      engineVersion: "4.0.0",
      requirementId: "REQ-025",
      datasetId: dataset.id,
      profileId: "TIME_EDITORIAL",
      sourceCount: rawPoints.length,
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
      totalPoints: screenPoints.length,
      visiblePoints: screenPoints.length,
      clippedPoints: 0,
      domainRange: { min: minX, max: maxX },
      valueRange: { min: minY, max: maxY },
    },
    ...legacyIR,
  };
}

export class TrendLineGraphCompiler {
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
      return compileTrendLineGraph(ds, cfg, { viewport: vp });
    }
    return compileTrendLineGraph(datasetOrOptions, config, context);
  }
}

