import crypto from "node:crypto";

/**
 * REQ-QA-002, REQ-QA-022, REQ-QA-035: Canonical JSON serializer & Deterministic SHA-256 Hasher.
 */
export class QAHash {
  public static canonicalize(obj: unknown): unknown {
    if (obj === null || obj === undefined) {
      return null;
    }

    if (typeof obj === "number") {
      if (!Number.isFinite(obj)) {
        throw new Error(`QAHash: Cannot serialize non-finite number (${obj})`);
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
        .filter((k) => k !== "checksumSha256" && rec[k] !== undefined)
        .sort((a, b) => a.localeCompare(b, "en", { numeric: true }));

      const sortedObj: Record<string, unknown> = {};
      for (const key of keys) {
        sortedObj[key] = this.canonicalize(rec[key]);
      }
      return sortedObj;
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

  /**
   * REQ-QA-006: Identidad determinista de issues.
   * SHA-256 de una estructura canónica de { ruleId, entityIds, timestampSeconds, fingerprint }.
   */
  public static createIssueId(params: {
    ruleId: string;
    entityIds: string[];
    timestampSeconds?: number;
    fingerprint: string;
  }): string {
    const canonicalPayload = {
      ruleId: params.ruleId,
      entityIds: [...params.entityIds].sort(),
      timestampSeconds: params.timestampSeconds !== undefined ? Number(params.timestampSeconds.toFixed(4)) : null,
      fingerprint: params.fingerprint,
    };
    const hash = this.computeCanonicalSha256(canonicalPayload);
    return `issue_${params.ruleId.toLowerCase()}_${hash.slice(0, 16)}`;
  }
}
