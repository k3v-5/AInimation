import {
  DataVisualizationDataset,
  BarChartSpec,
  DataVisualizationIR,
  VisualizationElement,
} from "./types.js";
import { assertValidDataset } from "./validation.js";
import { normalizeDataset } from "./normalization.js";
import { LinearScale, BandScale } from "./scales.js";
import { resolveCanvasDimensions, computeSafeZone, computePlotArea } from "./layout.js";
import { AnimationPlanBuilder } from "./animation.js";
import { formatDataValue } from "./formatters.js";
import { TIME_COLOR_PALETTE, getColorForSeries } from "./color-mapping.js";
import { generateDeterministicId, computeVisualizationChecksum } from "./dataset-hash.js";
import { DataVisualizationError } from "./errors.js";

/**
 * REQ-025 §14: Compilador determinista de gráficos de barras animados.
 * Soporta orientación vertical y horizontal, ordenamientos y valores negativos con zero-baseline.
 */

export class AnimatedBarChartCompiler {
  public static compile(params: {
    dataset: DataVisualizationDataset;
    spec: BarChartSpec;
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
    const categoryCol = dataset.columns.find((c) => c.key === spec.categoryColumn);
    if (!categoryCol) {
      throw new DataVisualizationError({
        code: "COLUMN_NOT_FOUND",
        message: `Columna de categoría '${spec.categoryColumn}' no encontrada.`,
        column: spec.categoryColumn,
      });
    }

    const valueColKey = spec.valueColumns[0];
    const valueCol = dataset.columns.find((c) => c.key === valueColKey);
    if (!valueCol || valueCol.type !== "NUMBER") {
      throw new DataVisualizationError({
        code: "COLUMN_TYPE_MISMATCH",
        message: `Columna de valor '${valueColKey}' no es numérica o no existe.`,
        column: valueColKey,
      });
    }

    // Extraer y ordenar filas de datos
    interface BarItem {
      category: string;
      value: number;
      index: number;
    }

    let items: BarItem[] = dataset.rows
      .map((row, idx) => {
        const cat = String(row[spec.categoryColumn] ?? "");
        const rawVal = row[valueColKey];
        const val = typeof rawVal === "number" && Number.isFinite(rawVal) ? rawVal : 0;
        return { category: cat, value: val, index: idx };
      })
      .filter((item) => item.category.length > 0);

    if (spec.sort === "ASCENDING") {
      items.sort((a, b) => {
        if (a.value !== b.value) return a.value - b.value;
        return a.category.localeCompare(b.category);
      });
    } else if (spec.sort === "DESCENDING") {
      items.sort((a, b) => {
        if (a.value !== b.value) return b.value - a.value;
        return a.category.localeCompare(b.category);
      });
    }

    if (items.length === 0) {
      throw new DataVisualizationError({
        code: "DATASET_EMPTY",
        message: "No hay datos válidos para compilar las barras.",
      });
    }

    // Calcular rango numérico
    let minVal = Math.min(...items.map((it) => it.value));
    let maxVal = Math.max(...items.map((it) => it.value));
    if (minVal > 0) minVal = 0; // Baseline cero para barras positivas
    if (maxVal < 0) maxVal = 0; // Baseline cero para barras negativas
    if (minVal === maxVal) maxVal = minVal + 1;

    const valueScale = new LinearScale(minVal, maxVal);
    const bandScale = new BandScale(items.map((it) => it.category), 0.25, 0.1);

    const elements: VisualizationElement[] = [];
    const animBuilder = new AnimationPlanBuilder();
    const isVertical = spec.orientation === "VERTICAL";

    // 1. Fondo
    const bgId = generateDeterministicId("bg", [dataset.id, "bars"]);
    elements.push({
      id: bgId,
      type: "RECT",
      x: 0,
      y: 0,
      width: dims.width,
      height: dims.height,
      fill: TIME_COLOR_PALETTE.backgroundDark,
    });

    // 2. Título editorial
    if (dataset.title) {
      const titleId = generateDeterministicId("title", [dataset.id]);
      elements.push({
        id: titleId,
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

    // 3. Eje Cero (Baseline)
    let zeroCoord = 0;
    if (isVertical) {
      const zeroNorm = valueScale.scale(0);
      zeroCoord = plot.bottom - zeroNorm * plot.height;
      elements.push({
        id: generateDeterministicId("axis_zero", [dataset.id]),
        type: "LINE",
        x: plot.left,
        y: zeroCoord,
        width: plot.width,
        height: 0,
        stroke: TIME_COLOR_PALETTE.axisLine,
        strokeWidth: 2,
      });
    } else {
      const zeroNorm = valueScale.scale(0);
      zeroCoord = plot.left + zeroNorm * plot.width;
      elements.push({
        id: generateDeterministicId("axis_zero", [dataset.id]),
        type: "LINE",
        x: zeroCoord,
        y: plot.top,
        width: 0,
        height: plot.height,
        stroke: TIME_COLOR_PALETTE.axisLine,
        strokeWidth: 2,
      });
    }

    // 4. Generación de Barras y Etiquetas
    const bandwidth = isVertical
      ? bandScale.getBandwidth(plot.width)
      : bandScale.getBandwidth(plot.height);

    const animDuration = Math.max(0.5, spec.animationDurationSeconds ?? 2.0);
    const staggerSec = Math.min(0.12, 1.2 / items.length);

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      const barId = generateDeterministicId("bar", [dataset.id, item.category, i]);
      const labelId = generateDeterministicId("label", [dataset.id, item.category, i]);
      const valTextId = generateDeterministicId("val", [dataset.id, item.category, i]);
      const isNegative = item.value < 0;
      const barColor = isNegative
        ? TIME_COLOR_PALETTE.negativeBar
        : getColorForSeries(i, params.editorialProfile);

      const startAnim = 0.3 + i * staggerSec;
      const endAnim = startAnim + animDuration * 0.7;

      if (isVertical) {
        const bandPos = bandScale.getPosition(item.category, plot.width, plot.left);
        const valNorm = valueScale.scale(item.value);
        const zeroNorm = valueScale.scale(0);
        const targetHeight = Math.abs(valNorm - zeroNorm) * plot.height;
        const targetY = isNegative ? zeroCoord : zeroCoord - targetHeight;

        elements.push({
          id: barId,
          type: "RECT",
          x: bandPos,
          y: targetY,
          width: bandwidth,
          height: targetHeight,
          fill: barColor,
          opacity: 1,
        });

        animBuilder.add({
          targetId: barId,
          property: "HEIGHT",
          from: 0,
          to: targetHeight,
          startSeconds: startAnim,
          endSeconds: endAnim,
        });

        if (!isNegative) {
          animBuilder.add({
            targetId: barId,
            property: "Y",
            from: zeroCoord,
            to: targetY,
            startSeconds: startAnim,
            endSeconds: endAnim,
          });
        }

        // Etiqueta de Categoría debajo de baseline o del gráfico
        if (spec.showLabels) {
          elements.push({
            id: labelId,
            type: "TEXT",
            x: bandPos + bandwidth / 2,
            y: plot.bottom + 26,
            text: item.category,
            fontSize: 18,
            fontFamily: "Arial, sans-serif",
            fill: TIME_COLOR_PALETTE.textSecondary,
            textAnchor: "middle",
          });
          animBuilder.add({
            targetId: labelId,
            property: "OPACITY",
            from: 0,
            to: 1,
            startSeconds: startAnim + 0.1,
            endSeconds: endAnim + 0.2,
          });
        }

        // Etiqueta de Valor
        if (spec.showValues) {
          const valY = isNegative ? targetY + targetHeight + 20 : targetY - 12;
          elements.push({
            id: valTextId,
            type: "TEXT",
            x: bandPos + bandwidth / 2,
            y: valY,
            text: formatDataValue(item.value, dataset.unit),
            fontSize: 20,
            fontFamily: "Impact, Arial Black",
            fontWeight: "bold",
            fill: TIME_COLOR_PALETTE.textPrimary,
            textAnchor: "middle",
          });
          animBuilder.add({
            targetId: valTextId,
            property: "OPACITY",
            from: 0,
            to: 1,
            startSeconds: endAnim - 0.2,
            endSeconds: endAnim + 0.2,
          });
        }
      } else {
        // Horizontal
        const bandPos = bandScale.getPosition(item.category, plot.height, plot.top);
        const valNorm = valueScale.scale(item.value);
        const zeroNorm = valueScale.scale(0);
        const targetWidth = Math.abs(valNorm - zeroNorm) * plot.width;
        const targetX = isNegative ? zeroCoord - targetWidth : zeroCoord;

        elements.push({
          id: barId,
          type: "RECT",
          x: targetX,
          y: bandPos,
          width: targetWidth,
          height: bandwidth,
          fill: barColor,
          opacity: 1,
        });

        animBuilder.add({
          targetId: barId,
          property: "WIDTH",
          from: 0,
          to: targetWidth,
          startSeconds: startAnim,
          endSeconds: endAnim,
        });

        if (isNegative) {
          animBuilder.add({
            targetId: barId,
            property: "X",
            from: zeroCoord,
            to: targetX,
            startSeconds: startAnim,
            endSeconds: endAnim,
          });
        }

        if (spec.showLabels) {
          elements.push({
            id: labelId,
            type: "TEXT",
            x: plot.left - 16,
            y: bandPos + bandwidth / 2 + 6,
            text: item.category,
            fontSize: 18,
            fontFamily: "Arial, sans-serif",
            fill: TIME_COLOR_PALETTE.textSecondary,
            textAnchor: "end",
          });
        }

        if (spec.showValues) {
          const valX = isNegative ? targetX - 12 : targetX + targetWidth + 12;
          elements.push({
            id: valTextId,
            type: "TEXT",
            x: valX,
            y: bandPos + bandwidth / 2 + 6,
            text: formatDataValue(item.value, dataset.unit),
            fontSize: 20,
            fontFamily: "Impact, Arial Black",
            fontWeight: "bold",
            fill: TIME_COLOR_PALETTE.textPrimary,
            textAnchor: isNegative ? "end" : "start",
          });
        }
      }
    }

    // 5. Pie de fuente / evidencia
    if (dataset.source) {
      const srcId = generateDeterministicId("source", [dataset.id]);
      elements.push({
        id: srcId,
        type: "TEXT",
        x: safeZone.left,
        y: safeZone.bottom + 22,
        text: `FUENTE: ${dataset.source.title.toUpperCase()}${
          dataset.source.publisher ? ` | ${dataset.source.publisher.toUpperCase()}` : ""
        }`,
        fontSize: 14,
        fontFamily: "Arial, sans-serif",
        fill: TIME_COLOR_PALETTE.textMuted,
        textAnchor: "start",
      });
    }

    const durationSeconds = Math.max(3.0, animDuration + 1.5);
    const visId = generateDeterministicId("barchart", [dataset.id, spec.categoryColumn]);

    const partialIR: Omit<DataVisualizationIR, "checksumSha256"> = {
      id: visId,
      type: "BAR_CHART",
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
          categoryCount: items.length,
        },
        attention: {
          visualNovelty: 0.75,
          dataReveal: 0.85,
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
