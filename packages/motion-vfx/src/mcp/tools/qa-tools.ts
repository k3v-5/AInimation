import {
  EditorialDocument,
  QALintOptions,
  HumanDecision,
} from "../../editorial/contracts/index.js";
import { EditorialQALinter } from "../../editorial/qa/editorial-qa-linter.js";
import { EditorialAuditEngine } from "../../editorial/qa/editorial-audit-engine.js";
import { EditorialDiffEngine } from "../../editorial/qa/editorial-diff-engine.js";
import { HumanReviewQueue } from "../../editorial/qa/human-review-queue.js";

/**
 * REQ-030 / REQ-081 / REQ-082 / REQ-083 (§42):
 * Canonical MCP Tools for Editorial QA Linter, Audit & Human-in-the-Loop Diff Engine
 */

export async function editorial_run_qa(params: {
  document: EditorialDocument;
  options?: QALintOptions;
}) {
  const report = EditorialQALinter.lint(params.document, params.options);
  return { report };
}
export const editorial_qa_lint = editorial_run_qa;

export async function editorial_get_audit(params: {
  document: EditorialDocument;
  options?: QALintOptions;
}) {
  const report = EditorialAuditEngine.audit(params.document, params.options);
  return { report };
}
export const editorial_qa_get_report = editorial_get_audit;

export async function editorial_get_review_queue(params: {
  document: EditorialDocument;
}) {
  const report = EditorialQALinter.lint(params.document);
  return { queue: report.humanReview };
}
export const editorial_review_queue = editorial_get_review_queue;

export async function editorial_compare_revisions(params: {
  before: EditorialDocument;
  after: EditorialDocument;
}) {
  const report = EditorialDiffEngine.diff(params.before, params.after);
  return { report };
}
export const editorial_diff = editorial_compare_revisions;

export async function editorial_get_change_impact(params: {
  before: EditorialDocument;
  after: EditorialDocument;
}) {
  const report = EditorialDiffEngine.diff(params.before, params.after);
  return { impact: report.summary, impactLevel: report.impactLevel, impactReport: report.impact };
}
export const editorial_diff_impact = editorial_get_change_impact;

export async function editorial_approve_review(params: {
  itemId: string;
  reviewerId?: string;
  reason?: string;
  queueInstance?: HumanReviewQueue;
}) {
  const queue = params.queueInstance ?? new HumanReviewQueue();
  queue.approve(params.itemId, params.reason || "Approved by human editor");
  return { status: "APPROVED", itemId: params.itemId, auditEvents: queue.getAuditEvents() };
}

export async function editorial_reject_review(params: {
  itemId: string;
  reviewerId?: string;
  reason?: string;
  queueInstance?: HumanReviewQueue;
}) {
  const queue = params.queueInstance ?? new HumanReviewQueue();
  queue.reject(params.itemId, params.reason || "Rejected by human editor");
  return { status: "REJECTED", itemId: params.itemId, auditEvents: queue.getAuditEvents() };
}

export async function editorial_review_decide(params: {
  itemId: string;
  decision: HumanDecision;
  queueInstance?: HumanReviewQueue;
}) {
  const queue = params.queueInstance ?? new HumanReviewQueue();
  const updatedItem = queue.decide(params.itemId, params.decision);
  return { updatedItem, auditEvents: queue.getAuditEvents() };
}
