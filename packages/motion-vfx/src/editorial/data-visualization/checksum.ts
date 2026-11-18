import { createHash } from "node:crypto";
import { VisualizationIR } from "./types.js";

/**
 * REQ-025 §33: Serialización canónica JSON lexicográfica y normalizada.
 */
export function canonicalJsonStringify(obj: any): string {
  if (obj === null || typeof obj !== "object") {
    if (typeof obj === "number") {
      if (!Number.isFinite(obj)) {
        throw new Error(`Valor numérico no serializable en canonical JSON: ${obj}`);
      }
      return Number(obj.toFixed(4)).toString();
    }
    return JSON.stringify(obj);
  }

  if (Array.isArray(obj)) {
    const items = obj.map((item) => canonicalJsonStringify(item));
    return `[${items.join(",")}]`;
  }

  const sortedKeys = Object.keys(obj).sort();
  const entries: string[] = [];

  for (const key of sortedKeys) {
    if (key === "checksumSha256" || key === "generatedAt") {
      continue; // Excluido explícitamente del cómputo de checksum (§33, §51)
    }
    const val = obj[key];
    if (val === undefined) {
      continue; // Omitir undefined
    }
    entries.push(`${JSON.stringify(key)}:${canonicalJsonStringify(val)}`);
  }

  return `{${entries.join(",")}}`;
}

/**
 * REQ-025 §34: Cálculo determinista de checksum SHA-256 para VisualizationIR.
 */
export function computeVisualizationChecksum(visualization: VisualizationIR): string {
  const canonical = canonicalJsonStringify(visualization);
  return createHash("sha256").update(canonical, "utf-8").digest("hex");
}

/**
 * Verifica la integridad criptográfica de un VisualizationIR.
 */
export function verifyVisualizationChecksum(visualization: VisualizationIR): boolean {
  if (!visualization.checksumSha256) return false;
  const expected = computeVisualizationChecksum(visualization);
  return visualization.checksumSha256 === expected;
}

export const canonicalStringify = canonicalJsonStringify;
