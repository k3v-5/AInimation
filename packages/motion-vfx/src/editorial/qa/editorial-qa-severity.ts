/**
 * REQ-QA-003: Severidad de issues editoriales y ponderación para priorización.
 */
export type EditorialIssueSeverity = "BLOCKING" | "WARNING" | "SUGGESTION";

export const SEVERITY_WEIGHTS: Record<EditorialIssueSeverity, number> = {
  BLOCKING: 1.0,
  WARNING: 0.65,
  SUGGESTION: 0.3,
};

export type QACertificationStatus = "PASS" | "PASS_WITH_WARNINGS" | "BLOCKED";

/**
 * REQ-QA-024: Regla de certificación determinista.
 * - BLOCKED: si blocking > 0
 * - PASS_WITH_WARNINGS: si blocking === 0 && warnings > 0
 * - PASS: si blocking === 0 && warnings === 0
 * Las SUGGESTION no bloquean.
 */
export function determineCertificationStatus(
  blockingCount: number,
  warningCount: number
): QACertificationStatus {
  if (blockingCount > 0) {
    return "BLOCKED";
  }
  if (warningCount > 0) {
    return "PASS_WITH_WARNINGS";
  }
  return "PASS";
}
