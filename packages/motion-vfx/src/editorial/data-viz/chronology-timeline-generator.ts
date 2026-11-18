import {
  ChronologyTimelineSpec,
  ChronologyEvent,
  DataVisualizationIR,
  VisualizationElement,
} from "./types.js";
import { resolveCanvasDimensions, computeSafeZone, computePlotArea } from "./layout.js";
import { AnimationPlanBuilder } from "./animation.js";
import { formatDate } from "./formatters.js";
import { TIME_COLOR_PALETTE } from "./color-mapping.js";
import { generateDeterministicId, computeVisualizationChecksum } from "./dataset-hash.js";
import { DataVisualizationError } from "./errors.js";

/**
 * REQ-025 §18, §19 & §20: Generador determinista de líneas de tiempo cronológicas (Chronology Timeline).
 */

export class ChronologyTimelineGenerator {
  public static compile(params: {
    spec: ChronologyTimelineSpec;
    editorialProfile?: string;
    width?: number;
    height?: number;
  }): DataVisualizationIR {
    const { spec } = params;
    const dims = resolveCanvasDimensions(params.width ?? 1920, params.height ?? 1080);
    const safeZone = computeSafeZone(dims);
    const plot = computePlotArea(safeZone, true, false);

    if (!spec.events || spec.events.length === 0) {
      throw new DataVisualizationError({
        code: "DATASET_EMPTY",
        message: "La cronología debe contener al menos un evento.",
      });
    }

    // Procesar y ordenar eventos
    interface ParsedEvent extends ChronologyEvent {
      timestamp: number;
      displayDate: string;
      index: number;
    }

    const parsedEvents: ParsedEvent[] = [];
    const undatedPolicy = spec.undatedPolicy ?? "REJECT";

    for (let i = 0; i < spec.events.length; i++) {
      const ev = spec.events[i];
      if (!ev.date || ev.date.trim() === "") {
        if (undatedPolicy === "REJECT") {
          throw new DataVisualizationError({
            code: "INVALID_DATE",
            message: `Evento '${ev.title}' carece de fecha válida bajo política REJECT.`,
          });
        }
      }

      const t = Date.parse(ev.date);
      const timestamp = Number.isNaN(t) ? 0 : t;
      parsedEvents.push({
        ...ev,
        timestamp,
        displayDate: formatDate(ev.date),
        index: i,
      });
    }

    // Ordenar: timestamp ascendente -> título lexicográfico -> índice
    parsedEvents.sort((a, b) => {
      if (a.timestamp !== b.timestamp) return a.timestamp - b.timestamp;
      const titleCmp = a.title.localeCompare(b.title);
      if (titleCmp !== 0) return titleCmp;
      return a.index - b.index;
    });

    const isHorizontal = spec.orientation === "HORIZONTAL";
    const elements: VisualizationElement[] = [];
    const animBuilder = new AnimationPlanBuilder();

    // 1. Fondo
    elements.push({
      id: generateDeterministicId("bg", ["timeline"]),
      type: "RECT",
      x: 0,
      y: 0,
      width: dims.width,
      height: dims.height,
      fill: TIME_COLOR_PALETTE.backgroundDark,
    });

    // 2. Título
    elements.push({
      id: generateDeterministicId("title", ["timeline"]),
      type: "TEXT",
      x: safeZone.left,
      y: safeZone.top + 32,
      text: "CRONOLOGÍA EDITORIAL",
      fontSize: 36,
      fontFamily: "Impact, Arial Black, Anton",
      fontWeight: "bold",
      fill: TIME_COLOR_PALETTE.textPrimary,
      textAnchor: "start",
    });

    // 3. Eje Principal de la Línea de Tiempo
    const lineId = generateDeterministicId("timeline_axis", ["main"]);
    const midY = plot.top + plot.height / 2;
    const midX = plot.left + plot.width / 2;

    if (isHorizontal) {
      elements.push({
        id: lineId,
        type: "LINE",
        x: plot.left,
        y: midY,
        width: plot.width,
        height: 0,
        stroke: TIME_COLOR_PALETTE.accentRed,
        strokeWidth: 3,
      });
    } else {
      elements.push({
        id: lineId,
        type: "LINE",
        x: midX,
        y: plot.top,
        width: 0,
        height: plot.height,
        stroke: TIME_COLOR_PALETTE.accentRed,
        strokeWidth: 3,
      });
    }

    const animDuration = Math.max(0.5, spec.animationDurationSeconds ?? 2.5);
    animBuilder.add({
      targetId: lineId,
      property: isHorizontal ? "WIDTH" : "HEIGHT",
      from: 0,
      to: isHorizontal ? plot.width : plot.height,
      startSeconds: 0.2,
      endSeconds: 0.2 + animDuration * 0.4,
    });

    // 4. Hitos y Carriles Alternados
    const n = parsedEvents.length;
    const step = isHorizontal ? plot.width / (n + 1) : plot.height / (n + 1);

    for (let i = 0; i < n; i++) {
      const ev = parsedEvents[i];
      const isAlt = i % 2 === 1; // Alternar carril arriba/abajo o izq/der

      const nodeId = generateDeterministicId("node", [ev.title, i]);
      const dateId = generateDeterministicId("date", [ev.title, i]);
      const titleId = generateDeterministicId("event_title", [ev.title, i]);
      const connId = generateDeterministicId("conn", [ev.title, i]);

      const nodeX = isHorizontal ? plot.left + (i + 1) * step : midX;
      const nodeY = isHorizontal ? midY : plot.top + (i + 1) * step;

      // Nodo central
      elements.push({
        id: nodeId,
        type: "CIRCLE",
        x: nodeX,
        y: nodeY,
        width: 14,
        height: 14,
        fill: TIME_COLOR_PALETTE.accentRed,
        stroke: TIME_COLOR_PALETTE.textPrimary,
        strokeWidth: 2,
      });

      const startReveal = 0.4 + (i / n) * (animDuration * 0.6);

      animBuilder.add({
        targetId: nodeId,
        property: "SCALE",
        from: 0,
        to: 1,
        startSeconds: startReveal,
        endSeconds: startReveal + 0.2,
        easing: "easeOutBack",
      });

      if (isHorizontal) {
        const offset = isAlt ? 90 : -90;
        const textY = midY + offset;

        // Conector vertical hacia la etiqueta
        elements.push({
          id: connId,
          type: "LINE",
          x: nodeX,
          y: isAlt ? midY : textY + 30,
          width: 0,
          height: Math.abs(offset) - 30,
          stroke: TIME_COLOR_PALETTE.gridLine,
          strokeWidth: 1,
        });

        // Fecha
        elements.push({
          id: dateId,
          type: "TEXT",
          x: nodeX,
          y: isAlt ? textY + 8 : textY,
          text: ev.displayDate,
          fontSize: 14,
          fontFamily: "Impact, Arial Black",
          fontWeight: "bold",
          fill: TIME_COLOR_PALETTE.accentRed,
          textAnchor: "middle",
        });

        // Título del evento
        elements.push({
          id: titleId,
          type: "TEXT",
          x: nodeX,
          y: isAlt ? textY + 28 : textY + 20,
          text: ev.title.toUpperCase(),
          fontSize: 16,
          fontFamily: "Arial, sans-serif",
          fontWeight: "bold",
          fill: TIME_COLOR_PALETTE.textPrimary,
          textAnchor: "middle",
        });
      } else {
        // Vertical
        const offset = isAlt ? 120 : -120;
        const textX = midX + offset;

        elements.push({
          id: connId,
          type: "LINE",
          x: isAlt ? midX : textX,
          y: nodeY,
          width: Math.abs(offset) - 20,
          height: 0,
          stroke: TIME_COLOR_PALETTE.gridLine,
          strokeWidth: 1,
        });

        elements.push({
          id: dateId,
          type: "TEXT",
          x: textX,
          y: nodeY - 6,
          text: ev.displayDate,
          fontSize: 14,
          fontFamily: "Impact, Arial Black",
          fontWeight: "bold",
          fill: TIME_COLOR_PALETTE.accentRed,
          textAnchor: isAlt ? "start" : "end",
        });

        elements.push({
          id: titleId,
          type: "TEXT",
          x: textX,
          y: nodeY + 14,
          text: ev.title.toUpperCase(),
          fontSize: 16,
          fontFamily: "Arial, sans-serif",
          fontWeight: "bold",
          fill: TIME_COLOR_PALETTE.textPrimary,
          textAnchor: isAlt ? "start" : "end",
        });
      }

      animBuilder.add({
        targetId: titleId,
        property: "OPACITY",
        from: 0,
        to: 1,
        startSeconds: startReveal + 0.1,
        endSeconds: startReveal + 0.3,
      });
      animBuilder.add({
        targetId: dateId,
        property: "OPACITY",
        from: 0,
        to: 1,
        startSeconds: startReveal + 0.1,
        endSeconds: startReveal + 0.3,
      });
    }

    const durationSeconds = Math.max(3.0, animDuration + 1.5);
    const visId = generateDeterministicId("timeline", [spec.events.length, spec.orientation]);

    const partialIR: Omit<DataVisualizationIR, "checksumSha256"> = {
      id: visId,
      type: "CHRONOLOGY",
      width: dims.width,
      height: dims.height,
      durationSeconds,
      elements,
      animation: animBuilder.build(),
      metadata: {
        datasetId: "chronology_events",
        generatedBy: "DATA_VISUALIZATION_ENGINE",
        engineVersion: "v4.0.0-editorial-master",
        schemaVersion: "1.0.0",
        editorialProfile: params.editorialProfile ?? "DOCUMENTARY_INVESTIGATIVE",
        complexity: {
          elementCount: elements.length,
          textElementCount: elements.filter((e) => e.type === "TEXT").length,
          dataSeriesCount: 1,
          categoryCount: parsedEvents.length,
        },
        attention: {
          visualNovelty: 0.85,
          dataReveal: 0.9,
        },
      },
    };

    const checksumSha256 = computeVisualizationChecksum(partialIR);

    return {
      ...partialIR,
      checksumSha256,
    };
  }
}
