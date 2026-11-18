import {
  DataVisualizationDataset,
  BigStatSpec,
  DataVisualizationIR,
  VisualizationElement,
} from "./types.js";
import { resolveCanvasDimensions, computeSafeZone } from "./layout.js";
import { AnimationPlanBuilder } from "./animation.js";
import { formatCompactNumber, formatDeterministicNumber } from "./formatters.js";
import { TIME_COLOR_PALETTE } from "./color-mapping.js";
import { generateDeterministicId, computeVisualizationChecksum } from "./dataset-hash.js";
import { DataVisualizationError } from "./errors.js";

/**
 * REQ-025 §16 & §17: Generador editorial de tarjetas estadísticas de alto impacto (Big Stat Card).
 */

export class BigStatCardGenerator {
  public static compile(params: {
    dataset?: DataVisualizationDataset | null;
    spec: BigStatSpec;
    editorialProfile?: string;
    width?: number;
    height?: number;
  }): DataVisualizationIR {
    const { dataset, spec } = params;
    const dims = resolveCanvasDimensions(params.width ?? 1920, params.height ?? 1080);
    const safeZone = computeSafeZone(dims);

    // Resolver valor
    let numericValue: number = 0;
    let displayStr: string = "";

    if (spec.staticValue !== undefined) {
      if (typeof spec.staticValue === "number") {
        numericValue = spec.staticValue;
        displayStr = formatCompactNumber(numericValue);
      } else {
        displayStr = String(spec.staticValue);
      }
    } else if (dataset && spec.valueColumn) {
      const col = dataset.columns.find((c) => c.key === spec.valueColumn);
      if (!col) {
        throw new DataVisualizationError({
          code: "COLUMN_NOT_FOUND",
          message: `Columna de valor '${spec.valueColumn}' no encontrada.`,
          column: spec.valueColumn,
        });
      }
      const firstRowVal = dataset.rows[0]?.[spec.valueColumn];
      if (typeof firstRowVal === "number") {
        numericValue = firstRowVal;
        displayStr = formatCompactNumber(numericValue);
      } else {
        displayStr = String(firstRowVal ?? "0");
      }
    } else {
      displayStr = "0";
    }

    const prefix = spec.prefix ?? "";
    const suffix = spec.suffix ?? (spec.unit === "PERCENT" || spec.unit === "%" ? "%" : "");
    const fullValueText = `${prefix}${displayStr}${suffix}`;

    const centerX = safeZone.left + safeZone.width / 2;
    const centerY = safeZone.top + safeZone.height / 2;

    const elements: VisualizationElement[] = [];
    const animBuilder = new AnimationPlanBuilder();

    // 1. Fondo
    const bgId = generateDeterministicId("bg", [spec.label, "bigstat"]);
    elements.push({
      id: bgId,
      type: "RECT",
      x: 0,
      y: 0,
      width: dims.width,
      height: dims.height,
      fill: TIME_COLOR_PALETTE.backgroundDark,
    });

    // 2. Valor Gigante
    const valId = generateDeterministicId("stat_val", [spec.label]);
    elements.push({
      id: valId,
      type: "TEXT",
      x: centerX,
      y: centerY - 40,
      text: fullValueText,
      fontSize: 120,
      fontFamily: "Impact, Arial Black, Anton",
      fontWeight: "bold",
      fill: TIME_COLOR_PALETTE.textPrimary,
      textAnchor: "middle",
    });

    const animDuration = Math.max(0.5, spec.animationDurationSeconds ?? 2.0);

    animBuilder.add({
      targetId: valId,
      property: "OPACITY",
      from: 0,
      to: 1,
      startSeconds: 0.2,
      endSeconds: 0.2 + animDuration * 0.4,
    });

    animBuilder.add({
      targetId: valId,
      property: "SCALE",
      from: 0.94,
      to: 1.0,
      startSeconds: 0.2,
      endSeconds: 0.2 + animDuration * 0.6,
      easing: "easeOutBack",
    });

    // 3. Línea de Acento Editorial Roja
    const ruleWidth = Math.min(safeZone.width * 0.5, 400);
    const ruleId = generateDeterministicId("stat_rule", [spec.label]);
    elements.push({
      id: ruleId,
      type: "RULE",
      x: centerX - ruleWidth / 2,
      y: centerY + 20,
      width: ruleWidth,
      height: 4,
      fill: TIME_COLOR_PALETTE.accentRed,
    });

    animBuilder.add({
      targetId: ruleId,
      property: "WIDTH",
      from: 0,
      to: ruleWidth,
      startSeconds: 0.4,
      endSeconds: 0.4 + animDuration * 0.4,
    });

    // 4. Etiqueta Descriptiva
    const labelId = generateDeterministicId("stat_label", [spec.label]);
    elements.push({
      id: labelId,
      type: "TEXT",
      x: centerX,
      y: centerY + 65,
      text: spec.label.toUpperCase(),
      fontSize: 28,
      fontFamily: "Arial, sans-serif",
      fontWeight: "bold",
      fill: TIME_COLOR_PALETTE.textSecondary,
      textAnchor: "middle",
    });

    animBuilder.add({
      targetId: labelId,
      property: "OPACITY",
      from: 0,
      to: 1,
      startSeconds: 0.6,
      endSeconds: 0.6 + animDuration * 0.4,
    });

    // 5. Subtítulo / Fuente
    const sourceText = spec.sourceLabel ?? dataset?.source?.title;
    if (sourceText) {
      const srcId = generateDeterministicId("stat_src", [spec.label]);
      elements.push({
        id: srcId,
        type: "TEXT",
        x: centerX,
        y: centerY + 110,
        text: sourceText.toUpperCase(),
        fontSize: 16,
        fontFamily: "Arial, sans-serif",
        fill: TIME_COLOR_PALETTE.textMuted,
        textAnchor: "middle",
      });

      animBuilder.add({
        targetId: srcId,
        property: "OPACITY",
        from: 0,
        to: 1,
        startSeconds: 0.8,
        endSeconds: 0.8 + animDuration * 0.3,
      });
    }

    const durationSeconds = Math.max(3.0, animDuration + 1.5);
    const visId = generateDeterministicId("bigstat", [spec.label]);

    const partialIR: Omit<DataVisualizationIR, "checksumSha256"> = {
      id: visId,
      type: "BIG_STAT",
      width: dims.width,
      height: dims.height,
      durationSeconds,
      elements,
      animation: animBuilder.build(),
      metadata: {
        datasetId: dataset?.id ?? "stat_isolated",
        sourceId: dataset?.source?.id,
        evidenceIds: dataset?.source?.id ? [dataset.source.id] : [],
        generatedBy: "DATA_VISUALIZATION_ENGINE",
        engineVersion: "v4.0.0-editorial-master",
        schemaVersion: "1.0.0",
        editorialProfile: params.editorialProfile ?? "DOCUMENTARY_INVESTIGATIVE",
        complexity: {
          elementCount: elements.length,
          textElementCount: elements.filter((e) => e.type === "TEXT").length,
          dataSeriesCount: 1,
          categoryCount: 1,
        },
        attention: {
          visualNovelty: 0.9,
          dataReveal: 0.95,
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
