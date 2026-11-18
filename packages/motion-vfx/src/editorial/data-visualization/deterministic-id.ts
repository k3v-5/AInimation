import { createHash } from "node:crypto";

/**
 * REQ-025 §15: Generación determinista de identificadores estables.
 * Prohibido el uso de UUIDs aleatorios o Math.random().
 */

export function generateDeterministicId(prefix: string, components: Record<string, any>): string {
  // Serializar de forma canónica las claves ordenadas
  const sortedKeys = Object.keys(components).sort();
  const canonicalObj: Record<string, any> = {};
  for (const k of sortedKeys) {
    canonicalObj[k] = components[k];
  }
  const serialized = JSON.stringify(canonicalObj);
  const hash = createHash("sha256").update(serialized).digest("hex").slice(0, 12);
  return `${prefix}_${hash}`;
}

export function createBarId(
  visId: string,
  category: string,
  rowIndex: number,
  value: number
): string {
  return generateDeterministicId("bar", { visId, category, rowIndex, value });
}

export function createTrendPointId(
  visId: string,
  index: number,
  x: any,
  y: any
): string {
  return generateDeterministicId("point", { visId, index, x, y });
}

export function createTimelineEventId(
  visId: string,
  index: number,
  date: string,
  title: string
): string {
  return generateDeterministicId("evt", { visId, index, date, title });
}
