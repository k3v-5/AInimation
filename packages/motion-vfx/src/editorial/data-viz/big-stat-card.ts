import {
  Dataset,
  ValidationResult,
  NormalizedVisualizationData,
  VisualizationCompileContext,
  DataVisualizationCompiler,
} from "./contracts.js";
import { BigStatNode } from "./visualization-base.js";
import { validateCanonicalDataset } from "./validation.js";
import { DeterministicNumberFormatter } from "./number-formatter.js";
import { ProvenanceTracker } from "./provenance.js";
import { BigStatCardGenerator as InternalGenerator } from "./big-stat-card-generator.js";

export interface BigStatConfig {
  value?: number;
  label?: string;
  subtitle?: string;
  unit?: string;
  isCurrency?: boolean;
  currencyCode?: string;
  animationDurationSeconds?: number;
}

/**
 * REQ-025 §14, §15 & §16: BigStatCardGenerator
 * Generador de tarjetas estadísticas TIME Editorial de alto impacto.
 */
export class BigStatCardGenerator implements DataVisualizationCompiler<Dataset | any, BigStatNode> {
  public readonly type = "BIG_STAT" as const;

  public validate(input: Dataset | any): ValidationResult {
    if (input && input.values) {
      return validateCanonicalDataset(input);
    }
    return { valid: true, errors: [] };
  }

  public normalize(input: Dataset | any): NormalizedVisualizationData {
    const val = input && input.values && input.values[0] ? input.values[0].value : (input?.value ?? 0);
    return {
      minValue: val,
      maxValue: val,
      range: 0,
      isConstant: true,
      normalizedPoints: [{
        original: { label: input?.title ?? "Stat", value: val },
        normalizedValue: 1.0,
      }],
    };
  }

  public compile(
    input: Dataset | any,
    context: VisualizationCompileContext | any = {}
  ): any {
    // Si se pasa con spec legacy
    if (input && (input.spec || (input.dataset && input.spec))) {
      return InternalGenerator.compile(input);
    }

    const config: BigStatConfig = context.config ?? context ?? {};
    let numericValue = 0;
    let label = config.label || "STAT";
    let unit = config.unit;
    let datasetId = "stat_direct";

    if (input && input.values && input.values.length > 0) {
      numericValue = input.values[0].value;
      label = input.values[0].label || input.title || label;
      unit = input.unit || unit;
      datasetId = input.id;
    } else if (typeof input === "number") {
      numericValue = input;
    } else if (config.value !== undefined) {
      numericValue = config.value;
    }

    // Formatear valor deterministamente (§15, §16)
    let formattedValue: string;
    if (unit === "%" || label.includes("%")) {
      formattedValue = `${DeterministicNumberFormatter.format(numericValue, { maximumFractionDigits: 1 })}%`;
    } else if (config.isCurrency || config.currencyCode || unit === "USD" || unit === "EUR" || unit === "MXN") {
      formattedValue = DeterministicNumberFormatter.formatWithUnit(numericValue, config.currencyCode ?? unit ?? "USD");
    } else {
      formattedValue = DeterministicNumberFormatter.formatWithUnit(numericValue, unit);
    }

    const width = context.width ?? 1920;
    const height = context.height ?? 1080;
    const bounds = { x: 100, y: 100, width: width - 200, height: height - 200 };

    const node: BigStatNode = {
      id: `stat_${datasetId}`,
      type: "BIG_STAT",
      startTimeSeconds: context.startTimeSeconds ?? 0,
      durationSeconds: config.animationDurationSeconds ?? 4.0,
      bounds,
      numericValue,
      formattedValue,
      unit,
      primaryLabel: label.toUpperCase(),
      subtitle: config.subtitle,
      sourceText: input?.source?.citationId || input?.source?.description,
      style: {
        primaryColor: "#000000",
        accentColor: "#FF1424",
        backgroundColor: "#FFFFFF",
        fontFamily: "Impact",
        fontWeight: 900,
        labelSize: 36,
        valueSize: 120,
      },
      provenance: ProvenanceTracker.createProvenance(datasetId),
    };

    return node;
  }

  // Compatibilidad estática
  public static compile(params: any): any {
    const inst = new BigStatCardGenerator();
    if (params.spec || (params.dataset && params.spec)) {
      return InternalGenerator.compile(params);
    }
    return inst.compile(params.dataset ?? params, params);
  }
}
