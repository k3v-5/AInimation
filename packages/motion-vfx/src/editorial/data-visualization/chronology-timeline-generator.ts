import {
  VisualizationDataset,
  ChronologyTimelineConfig,
  VisualizationContext,
  VisualizationIR,
  VisualizationElement,
  VisualizationAnimation,
  DataSet,
  ChronologyTimelineSpec,
  VisualizationCompilationResult,
} from "./types.js";
import { validateVisualizationDataset } from "./validation.js";
import { DEFAULT_VISUALIZATION_VIEWPORT, DEFAULT_VISUALIZATION_THEME, EPSILON } from "./constants.js";
import { computePlotArea } from "./geometry.js";
import { computeVisualizationChecksum } from "./checksum.js";
import { validateDataset as legacyValidateDataset } from "./dataset-validator.js";
import { resolveSafeArea } from "./layout-engine.js";
import { createTimelineEventId } from "./deterministic-id.js";
import { createOpacityEntranceExit, createStrokeWriteOnAnimation } from "./animation-utils.js";
import { computeVisualizationChecksum as legacyComputeChecksum } from "./visualization-hash.js";
import { DataVisualizationValidationError } from "./errors.js";

/**
 * REQ-025 §22-§23: Compilador determinista de líneas de tiempo cronológicas.
 */
export function compileChronologyTimeline(
  dataset: VisualizationDataset | DataSet | any,
  configOrSpec: ChronologyTimelineConfig | ChronologyTimelineSpec | any,
  context?: VisualizationContext
): VisualizationIR & VisualizationCompilationResult {
  // 1. Detección de firma canónica REQ-025
  if (dataset && Array.isArray(dataset.points)) {
    const valResult = validateVisualizationDataset(dataset);
    if (!valResult.valid) {
      const err = valResult.issues.find((i) => i.severity === "ERROR");
      throw new DataVisualizationValidationError(err?.message || "Dataset inválido");
    }

    const config: ChronologyTimelineConfig = {
      orientation: configOrSpec.orientation || "HORIZONTAL",
      showDates: configOrSpec.showDates !== false,
      showLabels: configOrSpec.showLabels !== false,
      showConnectors: configOrSpec.showConnectors !== false,
      animationDurationSeconds: configOrSpec.animationDurationSeconds || 2.5,
      markerStyle: configOrSpec.markerStyle || "CIRCLE",
    };

    // Invariante §23: Orden cronológico estricto t1 < t2 => x1 < x2
    let points = [...dataset.points];
    points.sort((a, b) => (a.timestamp ?? 0) - (b.timestamp ?? 0));

    const viewport = { ...DEFAULT_VISUALIZATION_VIEWPORT, ...context?.viewport };
    const theme = { ...DEFAULT_VISUALIZATION_THEME, ...context?.theme };
    const plot = computePlotArea(viewport);

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

    if (config.orientation === "HORIZONTAL") {
      const centerY = Number((plot.y + plot.height / 2).toFixed(2));
      const stepX = N > 1 ? plot.width / (N + 1) : 0;

      // Eje principal de la línea de tiempo
      elements.push({
        id: "timeline-axis",
        type: "LINE",
        x: plot.x,
        y: centerY,
        width: plot.width,
        height: 0,
        stroke: theme.primaryColor,
        strokeWidth: 3,
        opacity: 1,
      });

      animations.push({
        id: "anim-writeon-timeline-axis",
        elementId: "timeline-axis",
        property: "trimPathEnd",
        easing: "EASE_OUT",
        keyframes: [
          { timeSeconds: 0, value: 0 },
          { timeSeconds: Number((config.animationDurationSeconds * 0.4).toFixed(4)), value: 100 },
        ],
      });

      for (let i = 0; i < points.length; i++) {
        const p = points[i];
        const eventX = Number((N > 1 ? plot.x + (i + 1) * stepX : plot.x + plot.width / 2).toFixed(2));
        const laneOffset = i % 2 === 0 ? -60 : 60; // Carriles alternados para evitar colisiones (§24)
        const nodeY = centerY + laneOffset;

        const eventId = `timeline-event-${String(i).padStart(3, "0")}`;
        const markerId = `timeline-marker-${String(i).padStart(3, "0")}`;
        const connId = `timeline-conn-${String(i).padStart(3, "0")}`;
        const lblId = `timeline-lbl-${String(i).padStart(3, "0")}`;

        // Conector vectorial
        if (config.showConnectors) {
          elements.push({
            id: connId,
            type: "LINE",
            x: eventX,
            y: Math.min(centerY, nodeY),
            width: 0,
            height: Math.abs(laneOffset),
            stroke: theme.mutedTextColor,
            strokeWidth: 1.5,
            opacity: 0.7,
          });
        }

        // Marcador del evento
        elements.push({
          id: markerId,
          type: "TIMELINE_NODE",
          x: eventX,
          y: centerY,
          width: 14,
          height: 14,
          fill: theme.primaryColor,
          stroke: theme.textColor,
          strokeWidth: 2,
          opacity: 1,
          sourceId: p.id,
        });

        // Texto del evento
        elements.push({
          id: lblId,
          type: "LABEL",
          x: eventX,
          y: nodeY,
          text: p.label,
          fill: theme.textColor,
          opacity: 1,
          sourceId: p.id,
        });

        const delay = Number((0.2 + (i / N) * config.animationDurationSeconds * 0.6).toFixed(4));

        animations.push({
          id: `anim-fade-${markerId}`,
          elementId: markerId,
          property: "opacity",
          easing: "EASE_OUT",
          keyframes: [
            { timeSeconds: delay, value: 0 },
            { timeSeconds: delay + 0.3, value: 1 },
          ],
        });
      }
    } else {
      // VERTICAL
      const centerX = Number((plot.x + plot.width / 2).toFixed(2));
      const stepY = N > 1 ? plot.height / (N + 1) : 0;

      elements.push({
        id: "timeline-axis",
        type: "LINE",
        x: centerX,
        y: plot.y,
        width: 0,
        height: plot.height,
        stroke: theme.primaryColor,
        strokeWidth: 3,
        opacity: 1,
      });

      for (let i = 0; i < points.length; i++) {
        const p = points[i];
        const eventY = Number((N > 1 ? plot.y + (i + 1) * stepY : plot.y + plot.height / 2).toFixed(2));
        const laneOffset = i % 2 === 0 ? -120 : 120;
        const nodeX = centerX + laneOffset;

        const markerId = `timeline-marker-${String(i).padStart(3, "0")}`;
        const lblId = `timeline-lbl-${String(i).padStart(3, "0")}`;

        elements.push({
          id: markerId,
          type: "CIRCLE",
          x: centerX,
          y: eventY,
          width: 14,
          height: 14,
          fill: theme.primaryColor,
          stroke: theme.textColor,
          strokeWidth: 2,
          opacity: 1,
          sourceId: p.id,
        });

        elements.push({
          id: lblId,
          type: "TEXT",
          x: nodeX,
          y: eventY,
          text: p.label,
          fill: theme.textColor,
          opacity: 1,
          sourceId: p.id,
        });
      }
    }

    const ir: any = {
      id: `vis-timeline-${dataset.id}`,
      type: "CHRONOLOGY_TIMELINE",
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
        textElements: points.length,
        numericElements: 0,
        animationCount: animations.length,
      },
      pacingMetadata: {
        visualDurationSeconds: Number((config.animationDurationSeconds + 2.0).toFixed(2)),
        animationDurationSeconds: Number(config.animationDurationSeconds.toFixed(2)),
      },
      editorialIntensity: "MEDIUM",
      checksumSha256: "",
      success: true,
      errors: [],
      warnings: [],
    };

    ir.checksumSha256 = computeVisualizationChecksum(ir);
    ir.ir = ir;
    return ir;
  }

  // 2. Ruta legacy para DataSet + ChronologyTimelineSpec
  const spec: ChronologyTimelineSpec = configOrSpec;
  const legacyErrors = legacyValidateDataset(dataset, {
    requiredColumns: [spec.dateColumn, spec.titleColumn],
    allowEmptyRows: false,
  });

  if (legacyErrors.some((e) => e.severity === "BLOCKING")) {
    return {
      success: false,
      errors: legacyErrors,
      warnings: [],
    } as any;
  }

  const rawEvents: any[] = [];
  for (let r = 0; r < dataset.rows.length; r++) {
    const row = dataset.rows[r];
    const dateVal = row[spec.dateColumn];
    const titleVal = row[spec.titleColumn];

    if (!titleVal || String(titleVal).trim() === "") continue;

    let timeNum: number;
    if (typeof dateVal === "number") {
      timeNum = dateVal;
    } else {
      const parsed = Date.parse(String(dateVal));
      timeNum = isNaN(parsed) ? r : parsed;
    }

    rawEvents.push({
      id: createTimelineEventId(spec.id, r, String(dateVal), String(titleVal)),
      timeValue: timeNum,
      dateStr: String(dateVal),
      title: String(titleVal),
      description: spec.descriptionColumn ? String(row[spec.descriptionColumn] || "") : undefined,
      originalRow: row,
    });
  }

  rawEvents.sort((a, b) => a.timeValue - b.timeValue);

  const safeArea = resolveSafeArea(spec.width, spec.height, spec.safeZone);
  const layers: any[] = [];
  let zIndex = 1;

  if (spec.style.backgroundColor) {
    layers.push({
      id: `${spec.id}_bg`,
      name: "DV::BACKGROUND",
      type: "SHAPE",
      zIndex: zIndex++,
      transform: {
        position: { x: 0, y: 0 },
        scale: { x: 1, y: 1 },
        rotation: 0,
        anchor: { x: 0, y: 0 },
      },
      opacity: 1,
      geometry: {
        kind: "RECT",
        x: 0,
        y: 0,
        width: spec.width,
        height: spec.height,
        fillColor: spec.style.backgroundColor,
      },
    });
  }

  const isVert = spec.orientation === "VERTICAL";
  const axisX = safeArea.left + safeArea.width / 2;
  const axisY = safeArea.top + safeArea.height / 2;

  layers.push({
    id: `${spec.id}_axis`,
    name: "DV::TIMELINE::AXIS",
    type: "LINE",
    zIndex: zIndex++,
    transform: {
      position: { x: isVert ? axisX : safeArea.left, y: isVert ? safeArea.top : axisY },
      scale: { x: 1, y: 1 },
      rotation: 0,
      anchor: { x: 0, y: 0.5 },
    },
    opacity: 1,
    geometry: {
      kind: "LINE",
      x1: isVert ? axisX : safeArea.left,
      y1: isVert ? safeArea.top : axisY,
      x2: isVert ? axisX : safeArea.right,
      y2: isVert ? safeArea.bottom : axisY,
    },
    line: {
      x1: 0,
      y1: 0,
      x2: isVert ? 0 : safeArea.width,
      y2: isVert ? safeArea.height : 0,
      strokeColor: spec.style.primaryColor,
      strokeWidth: 3,
    },
    animations: [createStrokeWriteOnAnimation(spec.startTimeSeconds, spec.animation.entranceDurationSeconds, spec.animation.easing)],
  });

  const step = (isVert ? safeArea.height : safeArea.width) / (rawEvents.length + 1);

  for (let idx = 0; idx < rawEvents.length; idx++) {
    const ev = rawEvents[idx];
    const evX = isVert ? axisX : safeArea.left + (idx + 1) * step;
    const evY = isVert ? safeArea.top + (idx + 1) * step : axisY;
    const laneOffset = idx % 2 === 0 ? -60 : 60;
    const nodeTextX = isVert ? axisX + laneOffset : evX;
    const nodeTextY = isVert ? evY : axisY + laneOffset;

    // Node
    layers.push({
      id: `${spec.id}_node_${idx}`,
      name: `DV::TIMELINE::NODE::${idx}`,
      type: "SHAPE",
      zIndex: zIndex++,
      transform: { position: { x: evX, y: evY }, scale: { x: 1, y: 1 }, rotation: 0, anchor: { x: 0.5, y: 0.5 } },
      opacity: 1,
      geometry: { kind: "CIRCLE", radius: 6, fillColor: spec.style.primaryColor },
    });

    // Connector
    layers.push({
      id: `${spec.id}_conn_${idx}`,
      name: `DV::TIMELINE::CONN::${idx}`,
      type: "LINE",
      zIndex: zIndex++,
      transform: { position: { x: evX, y: evY }, scale: { x: 1, y: 1 }, rotation: 0, anchor: { x: 0, y: 0 } },
      opacity: 0.7,
      geometry: { kind: "LINE", x1: evX, y1: evY, x2: nodeTextX, y2: nodeTextY },
      line: { x1: 0, y1: 0, x2: isVert ? laneOffset : 0, y2: isVert ? 0 : laneOffset, strokeColor: spec.style.textColor, strokeWidth: 1.5 },
    });

    // Title
    layers.push({
      id: `${spec.id}_title_${idx}`,
      name: `DV::TIMELINE::TITLE::${idx}`,
      type: "TEXT",
      zIndex: zIndex++,
      transform: { position: { x: nodeTextX, y: nodeTextY }, scale: { x: 1, y: 1 }, rotation: 0, anchor: { x: 0.5, y: 0.5 } },
      opacity: 1,
      text: { content: ev.title, fontFamily: spec.style.fontFamily, fontSize: 16, fontWeight: 700, fillColor: spec.style.textColor, tracking: 0, justification: "CENTER" },
    });

    // Date
    layers.push({
      id: `${spec.id}_date_${idx}`,
      name: `DV::TIMELINE::DATE::${idx}`,
      type: "TEXT",
      zIndex: zIndex++,
      transform: { position: { x: nodeTextX, y: nodeTextY - 20 }, scale: { x: 1, y: 1 }, rotation: 0, anchor: { x: 0.5, y: 0.5 } },
      opacity: 0.8,
      text: { content: ev.dateStr, fontFamily: spec.style.fontFamily, fontSize: 12, fontWeight: 400, fillColor: spec.style.primaryColor, tracking: 0, justification: "CENTER" },
    });

    // Description
    layers.push({
      id: `${spec.id}_desc_${idx}`,
      name: `DV::TIMELINE::DESC::${idx}`,
      type: "TEXT",
      zIndex: zIndex++,
      transform: { position: { x: nodeTextX, y: nodeTextY + 20 }, scale: { x: 1, y: 1 }, rotation: 0, anchor: { x: 0.5, y: 0.5 } },
      opacity: 0.6,
      text: { content: ev.description || "", fontFamily: spec.style.fontFamily, fontSize: 11, fontWeight: 300, fillColor: spec.style.textColor, tracking: 0, justification: "CENTER" },
    });
  }

  const legacyIR: any = {
    id: spec.id,
    type: "CHRONOLOGY_TIMELINE",
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
    elements: rawEvents.map((ev, idx) => ({
      id: ev.id,
      type: "CIRCLE",
      x: safeArea.left + (idx + 1) * (safeArea.width / (rawEvents.length + 1)),
      y: axisY,
      width: 12,
      height: 12,
      text: ev.title,
    })),
    layers,
    animations: [],
    metadata: {
      engineVersion: "4.0.0",
      requirementId: "REQ-025",
      datasetId: dataset.id,
      profileId: "TIME_EDITORIAL",
      sourceCount: rawEvents.length,
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
      totalBars: 0,
      visibleBars: 0,
      clippedBars: 0,
    },
    ...legacyIR,
  };
}

export const generateChronologyTimeline = compileChronologyTimeline;

export class ChronologyTimelineGenerator {
  public static compile(specOrOptions: any, spec?: any, context?: any): { success: boolean; ir: VisualizationIR; collisions: any[]; [key: string]: any } {
    if (specOrOptions && typeof specOrOptions === "object" && specOrOptions.events) {
      const points = specOrOptions.events.map((ev: any, idx: number) => ({
        id: ev.id || `ev_${idx}`,
        label: ev.label || ev.title || `Event ${idx}`,
        value: ev.importance ?? 1.0,
        timestamp: ev.timestamp ?? idx,
      }));
      const ds = {
        id: specOrOptions.id || "timeline_ds",
        points,
      };
      const asp = specOrOptions.aspectRatio;
      const vp = asp === "9:16" ? { width: 1080, height: 1920 } : asp === "1:1" ? { width: 1080, height: 1080 } : { width: 1920, height: 1080 };
      const ir = compileChronologyTimeline(ds, {}, { viewport: vp });
      (ir as any).type = "CHRONOLOGY";
      (ir as any).ir = ir;
      return {
        ...ir,
        ir,
        type: "CHRONOLOGY",
        collisions: [],
        success: true,
      };
    }
    const res = compileChronologyTimeline(specOrOptions, spec, context);
    return {
      ...res,
      ir: res.ir || res,
      collisions: [],
      success: res.success,
    };
  }
}



