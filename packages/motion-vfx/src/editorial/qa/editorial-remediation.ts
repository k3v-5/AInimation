/**
 * REQ-030 §6: Declarative Remediation Contracts
 *
 * Las remediaciones describen propuestas declarativas para resolver hallazgos editoriales.
 * Está estrictamente prohibido que se ejecuten automáticamente durante la fase de análisis.
 */

export type EditorialRemediationAction =
  | "SHIFT"
  | "TRIM"
  | "EXTEND"
  | "REMOVE"
  | "REPLACE"
  | "ADD"
  | "DUCK"
  | "SPLIT"
  | "REORDER"
  | "REVIEW";

export interface EditorialRemediationImpact {
  pacingDelta?: number;
  attentionDelta?: number;
  cognitiveLoadDelta?: number;
  durationDeltaSeconds?: number;
}

export interface EditorialRemediation {
  action: EditorialRemediationAction;
  parameters: Record<string, unknown>;
  estimatedImpact?: EditorialRemediationImpact;
  confidence: number;
  requiresHumanApproval: boolean;
}

export function createRemediation(
  action: EditorialRemediationAction,
  parameters: Record<string, unknown> = {},
  options: {
    confidence?: number;
    requiresHumanApproval?: boolean;
    estimatedImpact?: EditorialRemediationImpact;
  } = {}
): EditorialRemediation {
  const confidence = options.confidence ?? 0.85;
  const requiresHumanApproval =
    options.requiresHumanApproval ?? (confidence < 0.7 || action === "REMOVE" || action === "REVIEW");

  return {
    action,
    parameters,
    confidence,
    requiresHumanApproval,
    estimatedImpact: options.estimatedImpact,
  };
}
