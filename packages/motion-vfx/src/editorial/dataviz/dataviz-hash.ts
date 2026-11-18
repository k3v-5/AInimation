import crypto from "node:crypto";
import { normalizeNumber } from "./data-normalizer.js";
import { DataVizIR } from "./types.js";

/**
 * REQ-025 §53, §54: Canonical JSON Serializer & Deterministic SHA-256 Hasher.
 */
export class DataVizHash {
  /**
   * Recursively canonicalizes an object or array:
   * - Lexicographically sorted object keys
   * - Excludes 'checksumSha256'
   * - Normalizes numbers to 4 decimals, eliminating -0
   * - Strips undefined values
   */
  public static canonicalize(obj: unknown): unknown {
    if (obj === null || obj === undefined) {
      return null;
    }

    if (typeof obj === "number") {
      return normalizeNumber(obj);
    }

    if (typeof obj === "string" || typeof obj === "boolean") {
      return obj;
    }

    if (Array.isArray(obj)) {
      return obj.map((item) => this.canonicalize(item));
    }

    if (typeof obj === "object") {
      const keys = Object.keys(obj as Record<string, unknown>)
        .filter((k) => k !== "checksumSha256" && (obj as Record<string, unknown>)[k] !== undefined)
        .sort((a, b) => a.localeCompare(b, "en", { numeric: true }));

      const sortedObj: Record<string, unknown> = {};
      for (const key of keys) {
        sortedObj[key] = this.canonicalize((obj as Record<string, unknown>)[key]);
      }
      return sortedObj;
    }

    return String(obj);
  }

  public static canonicalStringify(obj: unknown): string {
    const canonical = this.canonicalize(obj);
    return JSON.stringify(canonical);
  }

  public static computeSha256(ir: Omit<DataVizIR, "checksumSha256"> | DataVizIR): string {
    const canonical = this.canonicalStringify(ir);
    return crypto.createHash("sha256").update(canonical, "utf8").digest("hex");
  }
}
