import {
  VisualizationElement,
  CollisionReport,
} from "./types.js";

export interface NumberFormatOptions {
  decimals?: number;
  prefix?: string;
  suffix?: string;
  unit?: string;
  isCurrency?: boolean;
  currencySymbol?: string;
  isPercentage?: boolean;
  useGrouping?: boolean;
}

/**
 * REQ-025 §21: Formateador numérico determinista e independiente del locale del OS.
 */
export function formatVisualizationNumber(
  value: number,
  options: NumberFormatOptions = {}
): string {
  if (!Number.isFinite(value)) return "—";

  const decimals = options.decimals ?? 0;
  const isNegative = value < 0;
  const abs = Math.abs(value);

  // Redondear a los decimales solicitados
  const fixed = abs.toFixed(decimals);
  const parts = fixed.split(".");
  let integerPart = parts[0];
  const decimalPart = parts[1];

  // Separador de miles determinista (coma ',')
  if (options.useGrouping !== false) {
    integerPart = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }

  let formatted = decimalPart !== undefined ? `${integerPart}.${decimalPart}` : integerPart;

  // Prefijo / Moneda
  if (options.isCurrency || options.currencySymbol) {
    const sym = options.currencySymbol ?? "$";
    formatted = `${sym}${formatted}`;
  } else if (options.prefix) {
    formatted = `${options.prefix}${formatted}`;
  }

  // Porcentaje / Sufijo / Unidad
  if (options.isPercentage) {
    formatted = `${formatted}%`;
  } else if (options.unit) {
    formatted = `${formatted} ${options.unit}`;
  } else if (options.suffix) {
    formatted = `${formatted}${options.suffix}`;
  }

  return isNegative ? `-${formatted}` : formatted;
}

/**
 * REQ-025 §24: Detección determinista de colisiones entre elementos visuales rectangulares o de texto.
 */
export function detectVisualizationCollisions(
  elements: VisualizationElement[]
): CollisionReport {
  const collisions: CollisionReport["collisions"] = [];

  for (let i = 0; i < elements.length; i++) {
    for (let j = i + 1; j < elements.length; j++) {
      const a = elements[i];
      const b = elements[j];

      // Omitir fondos
      if (a.id.includes("bg") || b.id.includes("bg")) continue;

      const aW = a.width ?? 50;
      const aH = a.height ?? 20;
      const bW = b.width ?? 50;
      const bH = b.height ?? 20;

      // Intersección AABB
      const overlapX = Math.max(0, Math.min(a.x + aW, b.x + bW) - Math.max(a.x, b.x));
      const overlapY = Math.max(0, Math.min(a.y + aH, b.y + bH) - Math.max(a.y, b.y));

      if (overlapX > 0 && overlapY > 0) {
        collisions.push({
          elementIdA: a.id,
          elementIdB: b.id,
          distance: Math.hypot(b.x - a.x, b.y - a.y),
          recommendedOffset: {
            x: Number((overlapX / 2).toFixed(2)),
            y: Number((overlapY / 2).toFixed(2)),
          },
        });
      }
    }
  }

  return {
    hasCollisions: collisions.length > 0,
    collisions,
  };
}
