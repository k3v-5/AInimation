import { QASeverity } from "../contracts/editorial-qa.types.js";

/**
 * REQ-030: QA Severity Weights and Certification Status Logic
 */

export const QA_SEVERITY_WEIGHTS: Record<QASeverity, number> = {
  BLOCKING: 1.0,
  WARNING: 0.65,
  SUGGESTION: 0.3,
};

export class QASeverityCalculator {
  public static calculateScore(
    blockingCount: number,
    warningCount: number,
    suggestionCount: number
  ): number {
    const penalty = blockingCount * 50.0 + warningCount * 10.0 + suggestionCount * 2.0;
    return Number(Math.max(0.0, Math.min(100.0, 100.0 - penalty)).toFixed(4));
  }

  public static determineStatus(
    blockingCount: number,
    warningCount: number,
    humanReviewCount: number
  ): "BLOCKED" | "REVIEW_REQUIRED" | "PASSED_WITH_WARNINGS" | "PASSED" {
    if (blockingCount > 0) return "BLOCKED";
    if (humanReviewCount > 0) return "REVIEW_REQUIRED";
    if (warningCount > 0) return "PASSED_WITH_WARNINGS";
    return "PASSED";
  }
}
