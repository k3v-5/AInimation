import crypto from "node:crypto";
import { QASeverity } from "../contracts/editorial-qa.types.js";
import { QANormalizer } from "./qa-normalizer.js";

/**
 * REQ-030 §7: Deterministic QA Issue ID Generator
 */
export class QAId {
  public static createIssueId(params: {
    ruleId: string;
    entityIds: string[];
    timestampSeconds?: number;
    severity: QASeverity;
    fingerprint: string;
  }): string {
    const payload = {
      ruleId: params.ruleId,
      entityIds: [...params.entityIds].sort(),
      timestampSeconds:
        params.timestampSeconds !== undefined ? Number(params.timestampSeconds.toFixed(4)) : null,
      severity: params.severity,
      fingerprint: params.fingerprint,
    };

    const canonical = QANormalizer.canonicalStringify(payload);
    const hash = crypto.createHash("sha256").update(canonical, "utf8").digest("hex");
    return `qa_${params.ruleId.toLowerCase().replace(/[^a-z0-9]/g, "_")}_${hash.slice(0, 16)}`;
  }
}
