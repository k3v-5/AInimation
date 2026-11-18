import { DataUnit } from "./types.js";

export interface NumberFormatOptions {
  abbreviate?: boolean;
  decimals?: number;
  separator?: string;
  unit?: DataUnit | string;
  currencySymbol?: string;
  customUnitLabel?: string;
  prefix?: string;
  suffix?: string;
}

/**
 * REQ-025 §24, §25, §92, §93, §94: Deterministic Editorial Number Formatter.
 * Pure formatting without OS locale dependency.
 */
export class NumberFormatter {
  public static format(value: number, options: NumberFormatOptions = {}): string {
    if (!Number.isFinite(value)) {
      return String(value);
    }

    const abbreviate = options.abbreviate ?? true;
    const isNegative = value < 0;
    const absVal = Math.abs(value);

    let formattedValue = "";
    let metricSuffix = "";

    if (abbreviate && absVal >= 1000) {
      if (absVal >= 1e12) {
        metricSuffix = "T";
        formattedValue = this.roundToDecimals(absVal / 1e12, options.decimals ?? 2);
      } else if (absVal >= 1e9) {
        metricSuffix = "B";
        formattedValue = this.roundToDecimals(absVal / 1e9, options.decimals ?? 2);
      } else if (absVal >= 1e6) {
        metricSuffix = "M";
        formattedValue = this.roundToDecimals(absVal / 1e6, options.decimals ?? 2);
      } else {
        metricSuffix = "K";
        formattedValue = this.roundToDecimals(absVal / 1e3, options.decimals ?? 2);
      }
    } else {
      const decimals = options.decimals !== undefined ? options.decimals : Number.isInteger(value) ? 0 : 2;
      formattedValue = this.roundToDecimals(absVal, decimals);
    }

    // Apply thousands separator if no metric suffix was appended
    if (metricSuffix === "" && options.separator) {
      const parts = formattedValue.split(".");
      parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, options.separator);
      formattedValue = parts.join(".");
    }

    let result = (isNegative ? "-" : "") + formattedValue + metricSuffix;

    // Currency Prefix (§92: only if currency symbol explicitly specified)
    if (options.currencySymbol) {
      result = isNegative ? `-${options.currencySymbol}${formattedValue}${metricSuffix}` : `${options.currencySymbol}${result}`;
    }

    // Explicit Prefix
    if (options.prefix) {
      result = options.prefix + result;
    }

    // Unit Handling (§93, §94)
    if (options.unit === "PERCENT" || options.unit === "%") {
      result += "%";
    } else if (options.unit === "CUSTOM" && options.customUnitLabel) {
      result += ` ${options.customUnitLabel}`;
    } else if (options.suffix) {
      result += options.suffix;
    } else if (typeof options.unit === "string" && options.unit !== "NONE" && options.unit !== "COUNT" && options.unit !== "CURRENCY") {
      result += ` ${options.unit}`;
    }

    return result;
  }

  private static roundToDecimals(num: number, decimals: number): string {
    if (decimals === 0) {
      return String(Math.round(num));
    }
    const fixed = num.toFixed(decimals);
    // Remove trailing zero if not requested, but maintain consistent precision if formatted
    return fixed;
  }
}
