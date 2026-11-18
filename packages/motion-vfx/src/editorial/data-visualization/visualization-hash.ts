import { createHash } from "node:crypto";
import { VisualizationIR } from "./types.js";

/**
 * REQ-025 §50, §51, §52: Serialización canónica y Sello SHA-256 de VisualizationIR.
 */

export function canonicalStringify(obj: any): string {
  if (obj === null || obj === undefined) {
    return "null";
  }

  if (typeof obj === "number") {
    if (!Number.isFinite(obj)) {
      throw new Error(`Número no finito encontrado durante canonical stringify: ${obj}`);
    }
    return Number(obj.toFixed(4)).toString();
  }

  if (typeof obj === "boolean") {
    return obj ? "true" : "false";
  }

  if (typeof obj === "string") {
    return JSON.stringify(obj);
  }

  if (Array.isArray(obj)) {
    const elements = obj.map((item) => canonicalStringify(item));
    return `[${elements.join(",")}]`;
  }

  if (typeof obj === "object") {
    const keys = Object.keys(obj)
      .filter((k) => k !== "checksumSha256" && obj[k] !== undefined)
      .sort();

    const entries = keys.map((k) => {
      const val = canonicalStringify(obj[k]);
      return `${JSON.stringify(k)}:${val}`;
    });

    return `{${entries.join(",")}}`;
  }

  return JSON.stringify(obj);
}

export function computeVisualizationChecksum(ir: VisualizationIR): string {
  const canonical = canonicalStringify(ir);
  return createHash("sha256").update(canonical, "utf-8").digest("hex");
}

export function verifyVisualizationChecksum(ir: VisualizationIR): boolean {
  if (!ir.checksumSha256 || ir.checksumSha256.length !== 64) {
    return false;
  }
  const recalculated = computeVisualizationChecksum(ir);
  return recalculated === ir.checksumSha256;
}
