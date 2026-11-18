import crypto from "node:crypto";

/**
 * REQ-030 §38, §60: Canonical JSON and SHA-256 Serializer for Editorial QA
 */
export class QANormalizer {
  private static EXCLUDED_FIELDS = new Set([
    "checksumSha256",
    "executionTimeMs",
    "wallClockTime",
    "machineId",
    "processId",
  ]);

  public static canonicalize(obj: unknown): unknown {
    if (obj === null || obj === undefined) return null;

    if (typeof obj === "number") {
      if (!Number.isFinite(obj)) {
        throw new Error(`QANormalizer: Non-finite number (${obj}) detected during canonicalization`);
      }
      const rounded = Number(obj.toFixed(4));
      return rounded === 0 ? 0 : rounded;
    }

    if (typeof obj === "string" || typeof obj === "boolean") {
      return obj;
    }

    if (Array.isArray(obj)) {
      return obj.map((item) => this.canonicalize(item));
    }

    if (typeof obj === "object") {
      const rec = obj as Record<string, unknown>;
      const keys = Object.keys(rec)
        .filter((k) => !this.EXCLUDED_FIELDS.has(k) && rec[k] !== undefined)
        .sort((a, b) => a.localeCompare(b, "en", { numeric: true }));

      const sorted: Record<string, unknown> = {};
      for (const k of keys) {
        sorted[k] = this.canonicalize(rec[k]);
      }
      return sorted;
    }

    return String(obj);
  }

  public static canonicalStringify(obj: unknown): string {
    return JSON.stringify(this.canonicalize(obj));
  }

  public static computeCanonicalSha256(obj: unknown): string {
    const canonical = this.canonicalStringify(obj);
    return crypto.createHash("sha256").update(canonical, "utf8").digest("hex");
  }
}
