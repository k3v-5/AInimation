/**
 * REQ-025 §15 & §16: Deterministic Number & Unit Formatter
 *
 * Formateador determinista independiente del sistema operativo, timezone o locale del host.
 */

export interface NumberFormatConfig {
  locale?: string;
  minimumFractionDigits?: number;
  maximumFractionDigits?: number;
  useGrouping?: boolean;
  prefix?: string;
  suffix?: string;
}

export const CANONICAL_UNITS: Record<string, { prefix?: string; suffix?: string; isCurrency?: boolean }> = {
  "%": { suffix: "%" },
  "USD": { prefix: "$", suffix: " USD", isCurrency: true },
  "EUR": { prefix: "€", suffix: " EUR", isCurrency: true },
  "MXN": { prefix: "$", suffix: " MXN", isCurrency: true },
  "GBP": { prefix: "£", suffix: " GBP", isCurrency: true },
  "JPY": { prefix: "¥", suffix: " JPY", isCurrency: true },
  "kg": { suffix: " kg" },
  "g": { suffix: " g" },
  "km": { suffix: " km" },
  "m": { suffix: " m" },
  "m²": { suffix: " m²" },
  "hours": { suffix: " hrs" },
  "minutes": { suffix: " min" },
  "seconds": { suffix: " s" },
};

export class DeterministicNumberFormatter {
  /**
   * Formatea un número de manera 100% determinista sin depender de Intl.NumberFormat del entorno.
   */
  public static format(value: number, config: NumberFormatConfig = {}): string {
    if (!Number.isFinite(value) || isNaN(value)) {
      throw new Error(`DeterministicNumberFormatter: Cannot format non-finite number '${value}'.`);
    }

    const minDec = config.minimumFractionDigits ?? 0;
    const maxDec = config.maximumFractionDigits ?? 2;
    const useGrouping = config.useGrouping ?? true;

    const isNegative = value < 0;
    const absVal = Math.abs(value);

    // Redondeo determinista
    const factor = Math.pow(10, maxDec);
    const rounded = Math.round(absVal * factor) / factor;

    const parts = rounded.toFixed(maxDec).split(".");
    let intPart = parts[0];
    let decPart = parts.length > 1 ? parts[1] : "";

    // Truncar ceros innecesarios respetando minimumFractionDigits
    while (decPart.length > minDec && decPart.endsWith("0")) {
      decPart = decPart.slice(0, -1);
    }

    // Agrupación de miles determinista con comas
    if (useGrouping) {
      intPart = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    const formattedNum = decPart.length > 0 ? `${intPart}.${decPart}` : intPart;
    const sign = isNegative ? "-" : "";

    const prefix = config.prefix ?? "";
    const suffix = config.suffix ?? "";

    return `${sign}${prefix}${formattedNum}${suffix}`;
  }

  /**
   * Formatea un valor acompañado de su unidad canónica.
   */
  public static formatWithUnit(value: number, unit?: string, config: NumberFormatConfig = {}): string {
    if (!unit) {
      return this.format(value, config);
    }

    const unitInfo = CANONICAL_UNITS[unit] || { suffix: ` ${unit}` };
    const mergedConfig: NumberFormatConfig = {
      ...config,
      prefix: (config.prefix ?? "") + (unitInfo.prefix ?? ""),
      suffix: (unitInfo.suffix ?? "") + (config.suffix ?? ""),
    };

    return this.format(value, mergedConfig);
  }
}
