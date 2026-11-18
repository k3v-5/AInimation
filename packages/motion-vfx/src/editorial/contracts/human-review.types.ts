/**
 * REQ-081: Human-in-the-Loop Governance Contracts
 */

export type HumanReviewStatus = "PENDING" | "APPROVED" | "REJECTED" | "DEFERRED";

export type HumanDecisionAction = "ACCEPT" | "REJECT" | "MODIFY" | "DEFER";

export interface HumanDecision {
  decision: HumanDecisionAction;
  reviewerId: string;
  reason: string;
  modifiedValue?: unknown;
  timestamp?: string;
}

export interface HumanReviewItem {
  id: string;
  issueId: string;
  priority: number;
  status: HumanReviewStatus;
  confidence: number;
  createdAtDeterministic?: string;
  timestampSeconds?: number;
  context?: {
    title: string;
    explanation: string;
    evidence: string[];
  };
  proposedAction?: string;
  decision?: HumanDecision;

  // Compatibility fields
  severity?: any;
  reason?: string;
  affectedEntityIds?: string[];
  createdDeterministically?: boolean;
}

export interface HumanReviewSummary {
  pendingCount: number;
  approvedCount: number;
  rejectedCount: number;
  deferredCount: number;
  items: HumanReviewItem[];
}

export interface ReviewAuditEvent {
  sequence: number;
  itemId: string;
  action: string;
  payload: unknown;
}
