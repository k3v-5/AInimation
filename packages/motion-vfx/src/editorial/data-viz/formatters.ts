/**
 * REQ-025 §10: Formateo numérico y temporal determinista e independiente del locale del sistema.
 */

export function formatDeterministicNumber(num: number, decimals = 2): string {
  if (!Number.isFinite(num)) return "0";
  const fixed = num.toFixed(decimals);
  const parts = fixed.split(".");
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  // Si decimals > 0 y los decimales son todos ceros opcionales, mantener fijo
  return parts.join(".");
}

export function formatCompactNumber(num: number, decimals = 2): string {
  if (!Number.isFinite(num)) return "0";
  const abs = Math.abs(num);
  const sign = num < 0 ? "-" : "";

  if (abs >= 1_000_000_000_000) {
    const v = (abs / 1_000_000_000_000).toFixed(decimals);
    return `${sign}${v.replace(/\.0+$/, "")}T`;
  }
  if (abs >= 1_000_000_000) {
    const v = (abs / 1_000_000_000).toFixed(decimals);
    return `${sign}${v.replace(/\.0+$/, "")}B`;
  }
  if (abs >= 1_000_000) {
    const v = (abs / 1_000_000).toFixed(decimals);
    return `${sign}${v.replace(/\.0+$/, "")}M`;
  }
  if (abs >= 1_000) {
    const v = (abs / 1_000).toFixed(decimals);
    return `${sign}${v.replace(/\.0+$/, "")}K`;
  }

  return `${sign}${formatDeterministicNumber(abs, decimals).replace(/\.00$/, "")}`;
}

export function formatPercentage(num: number, decimals = 1): string {
  if (!Number.isFinite(num)) return "0.0%";
  const fixed = num.toFixed(decimals);
  return `${fixed}%`;
}

export function formatCurrency(num: number, symbol = "$", decimals = 2): string {
  if (!Number.isFinite(num)) return `${symbol}0.00`;
  const formatted = formatDeterministicNumber(num, decimals);
  return `${symbol}${formatted}`;
}

export function formatDate(dateVal: string | number): string {
  const t = typeof dateVal === "number" ? dateVal : Date.parse(dateVal);
  if (Number.isNaN(t)) return String(dateVal);

  const d = new Date(t);
  const year = d.getUTCFullYear();
  const month = String(d.getUTCMonth() + 1).padStart(2, "0");
  const day = String(d.getUTCDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function formatDataValue(val: any, unit?: string): string {
  if (val === null || val === undefined) return "—";
  if (typeof val === "boolean") return val ? "True" : "False";
  if (typeof val === "string") return val;

  if (typeof val === "number") {
    if (!Number.isFinite(val)) return "0";
    if (unit === "PERCENT" || unit === "%") {
      return formatPercentage(val);
    }
    if (unit === "CURRENCY" || unit === "$") {
      return formatCurrency(val);
    }
    if (Math.abs(val) >= 10_000) {
      return formatCompactNumber(val);
    }
    return formatDeterministicNumber(val, Number.isInteger(val) ? 0 : 2);
  }

  return String(val);
}
