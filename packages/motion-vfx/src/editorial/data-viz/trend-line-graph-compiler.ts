import {
  DataVisualizationDataset,
  TrendLineSpec,
  DataVisualizationIR,
  VisualizationElement,
} from "./types.js";
import { assertValidDataset } from "./validation.js";
import { LinearScale } from "./scales.js";
import { resolveCanvasDimensions, computeSafeZone, computePlotArea } from "./layout.js";
import { AnimationPlanBuilder } from "./animation.js";
import { formatDataValue, formatDate } from "./formatters.js";
import { TIME_COLOR_PALETTE } from "./color-mapping.js";
import { generateDeterministicId, computeVisualizationChecksum } from "./dataset-hash.js";
import { DataVisualizationError } from "./errors.js";

/**
 * REQ-025 §15: Compilador determinista de gráficos de líneas de tendencia.
 */

export class TrendLineGraphCompiler {
  public static compile(params: {
    dataset: DataVisualizationDataset;
    spec: TrendLineSpec;
    editorialProfile?: string;
    width?: number;
    height?: number;
  }): DataVisualizationIR {
    const { dataset, spec } = params;
    assertValidDataset(dataset);

    const dims = resolveCanvasDimensions(params.width ?? 1920, params.height ?? 1080);
    const safeZone = computeSafeZone(dims);
    const plot = computePlotArea(safeZone, Boolean(dataset.title), Boolean(dataset.source));

    // Validar columnas
    const xCol = dataset.columns.find((c) => c.key === spec.xColumn);
    if (!xCol) {
      throw new DataVisualizationError({
        code: "COLUMN_NOT_FOUND",
        message: `Columna X '${spec.xColumn}' no encontrada.`,
        column: spec.xColumn,
      });
    }

    const yCol = dataset.columns.find((c) => c.key === spec.yColumn);
    if (!yCol || yCol.type !== "NUMBER") {
      throw new DataVisualizationError({
        code: "COLUMN_TYPE_MISMATCH",
        message: `Columna Y '${spec.yColumn}' no es numérica o no existe.`,
        column: spec.yColumn,
      });
    }

    // Extraer puntos
    interface PointItem {
      rawX: any;
      numericX: number;
      numericY: number;
      displayX: string;
      index: number;
    }

    const points: PointItem[] = [];

    for (let i = 0; i < dataset.rows.length; i++) {
      const row = dataset.rows[i];
      const rawX = row[spec.xColumn];
      const rawY = row[spec.yColumn];

      if (rawY === null || rawY === undefined || typeof rawY !== "number" || !Number.isFinite(rawY)) {
        continue;
      }

      let numX = i;
      let dispX = String(rawX);
      if (xCol.type === "DATE") {
        const t = typeof rawX === "number" ? rawX : Date.parse(String(rawX));
        if (!Number.isNaN(t)) {
          numX = t;
          dispX = formatDate(t);
        }
      } else if (xCol.type === "NUMBER" && typeof rawX === "number") {
        numX = rawX;
        dispX = String(rawX);
      }

      points.push({
        rawX,
        numericX: numX,
        numericY: rawY,
        displayX: dispX,
        index: i,
      });
    }

    if (points.length === 0) {
      throw new DataVisualizationError({
        code: "DATASET_EMPTY",
        message: "No hay puntos válidos para compilar la línea de tendencia.",
      });
    }

    // Ordenar puntos por X ascendente
    points.sort((a, b) => a.numericX - b.numericX);

    // Escalas X e Y
    const minX = points[0].numericX;
    const maxX = points[points.length - 1].numericX;
    const minY = Math.min(...points.map((p) => p.numericY));
    const maxY = Math.max(...points.map((p) => p.numericY));

    const scaleX = new LinearScale(minX, maxX === minX ? minX + 1 : maxX);
    const scaleY = new LinearScale(minY, maxY === minY ? minY + 1 : maxY);

    const elements: VisualizationElement[] = [];
    const animBuilder = new AnimationPlanBuilder();

    // 1. Fondo
    elements.push({
      id: generateDeterministicId("bg", [dataset.id, "trend"]),
      type: "RECT",
      x: 0,
      y: 0,
      width: dims.width,
      height: dims.height,
      fill: TIME_COLOR_PALETTE.backgroundDark,
    });

    // 2. Título
    if (dataset.title) {
      elements.push({
        id: generateDeterministicId("title", [dataset.id]),
        type: "TEXT",
        x: safeZone.left,
        y: safeZone.top + 32,
        text: dataset.title.toUpperCase(),
        fontSize: 36,
        fontFamily: "Impact, Arial Black, Anton",
        fontWeight: "bold",
        fill: TIME_COLOR_PALETTE.textPrimary,
        textAnchor: "start",
      });
    }

    // 3. Grid Lines
    if (spec.showGrid) {
      const gridSteps = 4;
      for (let g = 0; g <= gridSteps; g++) {
        const normY = g / gridSteps;
        const gridY = plot.bottom - normY * plot.height;
        elements.push({
          id: generateDeterministicId("grid", [dataset.id, g]),
          type: "LINE",
          x: plot.left,
          y: gridY,
          width: plot.width,
          height: 0,
          stroke: TIME_COLOR_PALETTE.gridLine,
          strokeWidth: 1,
          opacity: 0.6,
        });
      }
    }

    // 4. Eje horizontal y vertical
    if (spec.showAxis) {
      elements.push({
        id: generateDeterministicId("axis_x", [dataset.id]),
        type: "LINE",
        x: plot.left,
        y: plot.bottom,
        width: plot.width,
        height: 0,
        stroke: TIME_COLOR_PALETTE.axisLine,
        strokeWidth: 2,
      });
    }

    // 5. Coordenadas de pantalla de los puntos
    const screenPoints = points.map((p) => {
      const normX = scaleX.scale(p.numericX);
      const normY = scaleY.scale(p.numericY);
      const screenX = plot.left + normX * plot.width;
      const screenY = plot.bottom - normY * plot.height;
      return { ...p, screenX, screenY };
    });

    // 6. Elemento PATH para la línea
    const pathId = generateDeterministicId("trend_path", [dataset.id]);
    elements.push({
      id: pathId,
      type: "PATH",
      x: plot.left,
      y: plot.top,
      width: plot.width,
      height: plot.height,
      stroke: TIME_COLOR_PALETTE.accentRed,
      strokeWidth: 4,
      fill: "none",
      metadata: {
        points: screenPoints.map((sp) => [sp.screenX, sp.screenY]),
      },
    });

    const animDuration = Math.max(0.5, spec.animationDurationSeconds ?? 2.0);
    animBuilder.add({
      targetId: pathId,
      property: "PATH_PROGRESS",
      from: 0,
      to: 1,
      startSeconds: 0.3,
      endSeconds: 0.3 + animDuration,
    });

    // 7. Puntos circulares y extremos
    let extremaIndices = new Set<number>();
    if (spec.highlightExtrema) {
      let minIdx = 0;
      let maxIdx = 0;
      for (let i = 0; i < points.length; i++) {
        if (points[i].numericY < points[minIdx].numericY) minIdx = i;
        if (points[i].numericY > points[maxIdx].numericY) maxIdx = i;
      }
      extremaIndices.add(minIdx);
      extremaIndices.add(maxIdx);
    }

    if (spec.showPoints) {
      for (let i = 0; i < screenPoints.length; i++) {
        const sp = screenPoints[i];
        const isExtrema = extremaIndices.has(i);
        const pointId = generateDeterministicId("point", [dataset.id, i]);
        const pointColor = isExtrema ? TIME_COLOR_PALETTE.textPrimary : TIME_COLOR_PALETTE.accentRed;

        elements.push({
          id: pointId,
          type: "CIRCLE",
          x: sp.screenX,
          y: sp.screenY,
          width: isExtrema ? 12 : 8,
          height: isExtrema ? 12 : 8,
          fill: pointColor,
          stroke: TIME_COLOR_PALETTE.backgroundDark,
          strokeWidth: 2,
        });

        const revealTime = 0.3 + (i / screenPoints.length) * animDuration;
        animBuilder.add({
          targetId: pointId,
          property: "OPACITY",
          from: 0,
          to: 1,
          startSeconds: revealTime,
          endSeconds: revealTime + 0.15,
        });

        // Etiqueta en extremos o si showLabels
        if (isExtrema || spec.showLabels) {
          const valLabelId = generateDeterministicId("val_lbl", [dataset.id, i]);
          elements.push({
            id: valLabelId,
            type: "TEXT",
            x: sp.screenX,
            y: sp.screenY - 14,
            text: formatDataValue(sp.numericY, dataset.unit),
            fontSize: 16,
            fontFamily: "Impact, Arial Black",
            fontWeight: "bold",
            fill: pointColor,
            textAnchor: "middle",
          });
          animBuilder.add({
            targetId: valLabelId,
            property: "OPACITY",
            from: 0,
            to: 1,
            startSeconds: revealTime + 0.1,
            endSeconds: revealTime + 0.25,
          });
        }
      }
    }

    // 8. Fuente
    if (dataset.source) {
      elements.push({
        id: generateDeterministicId("source", [dataset.id]),
        type: "TEXT",
        x: safeZone.left,
        y: safeZone.bottom + 22,
        text: `FUENTE: ${dataset.source.title.toUpperCase()}`,
        fontSize: 14,
        fontFamily: "Arial, sans-serif",
        fill: TIME_COLOR_PALETTE.textMuted,
        textAnchor: "start",
      });
    }

    const visId = generateDeterministicId("trendline", [dataset.id, spec.xColumn, spec.yColumn]);
    const durationSeconds = Math.max(3.0, animDuration + 1.5);

    const partialIR: Omit<DataVisualizationIR, "checksumSha256"> = {
      id: visId,
      type: "TREND_LINE",
      width: dims.width,
      height: dims.height,
      durationSeconds,
      elements,
      animation: animBuilder.build(),
      metadata: {
        datasetId: dataset.id,
        sourceId: dataset.source?.id,
        evidenceIds: dataset.source?.id ? [dataset.source.id] : [],
        generatedBy: "DATA_VISUALIZATION_ENGINE",
        engineVersion: "v4.0.0-editorial-master",
        schemaVersion: "1.0.0",
        editorialProfile: params.editorialProfile ?? "DOCUMENTARY_INVESTIGATIVE",
        complexity: {
          elementCount: elements.length,
          textElementCount: elements.filter((e) => e.type === "TEXT").length,
          dataSeriesCount: 1,
          categoryCount: points.length,
        },
        attention: {
          visualNovelty: 0.8,
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
