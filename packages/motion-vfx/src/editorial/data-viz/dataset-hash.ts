import { createHash } from "node:crypto";
import { DataVisualizationIR } from "./types.js";

/**
 * REQ-025 §28 & §29: Serialización canónica y sellado criptográfico SHA-256.
 */

export function deterministicCanonicalStringify(obj: any): string {
  if (obj === null || obj === undefined) return "null";

  if (typeof obj === "number") {
    if (!Number.isFinite(obj)) {
      throw new Error(`[CANONICAL_JSON] Valor no finito detectado: ${obj}`);
    }
    // Redondeo determinista a 4 decimales
    return (Math.round(obj * 10000) / 10000).toString();
  }

  if (typeof obj === "boolean" || typeof obj === "string") {
    return JSON.stringify(obj);
  }

  if (Array.isArray(obj)) {
    const items = obj.map((item) => deterministicCanonicalStringify(item));
    return `[${items.join(",")}]`;
  }

  if (typeof obj === "object") {
    const keys = Object.keys(obj).sort();
    const pairs: string[] = [];
    for (const key of keys) {
      if (key === "checksumSha256") continue; // Excluido del hashing
      const val = obj[key];
      if (val === undefined) continue;
      pairs.push(`${JSON.stringify(key)}:${deterministicCanonicalStringify(val)}`);
    }
    return `{${pairs.join(",")}}`;
  }

  return JSON.stringify(obj);
}

export function computeVisualizationChecksum(
  ir: Omit<DataVisualizationIR, "checksumSha256"> | DataVisualizationIR
): string {
  const canonical = deterministicCanonicalStringify(ir);
  return createHash("sha256").update(canonical, "utf8").digest("hex");
}

export function verifyVisualizationChecksum(ir: DataVisualizationIR): boolean {
  if (!ir.checksumSha256 || typeof ir.checksumSha256 !== "string") {
    return false;
  }
  const expected = computeVisualizationChecksum(ir);
  return ir.checksumSha256 === expected;
}

export function generateDeterministicId(prefix: string, components: any[]): string {
  const payload = components
    .map((c) => (typeof c === "object" ? deterministicCanonicalStringify(c) : String(c)))
    .join("::");
  const hash = createHash("sha256").update(payload, "utf8").digest("hex").slice(0, 12);
  return `${prefix}_${hash}`;
}
