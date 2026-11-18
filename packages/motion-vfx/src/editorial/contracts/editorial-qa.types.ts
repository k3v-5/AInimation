import { EditorialIR } from "../ir/editorial-ir.types.js";
import { HumanReviewSummary } from "./human-review.types.js";

/**
 * REQ-030: Canonical Editorial QA Linter Contracts
 */

export type QASeverity = "BLOCKING" | "WARNING" | "SUGGESTION";

export type EditorialIssueSeverity = QASeverity;

export type EditorialDocument = EditorialIR;

export interface QAIssue {
  id: string;
  ruleId: string;
  severity: QASeverity;

  title: string;
  message: string;

  timestampSeconds?: number;
  durationSeconds?: number;

  entityIds: string[];

  actualValue?: number | string | boolean;
  expectedValue?: number | string | boolean;

  threshold?: number;

  confidence: number;

  remediation?: string;

  autoFixAvailable: boolean;

  fingerprint: string;

  // Compatibility aliases
  category?: string;
  reason?: string;
  affectedEntityIds?: string[];
}

export interface QARuleContext {
  profile?: string;
  config?: Record<string, unknown>;
  assetRegistry?: unknown;
  evidenceEngine?: unknown;
  narrativeArc?: unknown;
}

export interface QARule {
  readonly id: string;
  readonly description: string;
  readonly severity: QASeverity;

  evaluate(
    document: EditorialDocument,
    context: QARuleContext
  ): QAIssue[];
}

export interface ExportReadiness {
  ready: boolean;
  blockers: QAIssue[];
}

export interface QALintOptions {
  strict?: boolean;
  includeSuggestions?: boolean;
  includeDiagnostics?: boolean;
  failOnWarnings?: boolean;
  confidenceThreshold?: number;
}

export interface EditorialQAReport {
  schemaVersion: string;
  engineVersion: string;

  documentId: string;
  projectId: string; // compatibility alias
  inputChecksumSha256: string;
  generatedAtDeterministic: string; // compatibility alias

  status: "BLOCKED" | "REVIEW_REQUIRED" | "PASSED" | "PASSED_WITH_WARNINGS" | "PASS";

  score: number;
  overallScore: number; // compatibility alias

  issues: QAIssue[];

  summary: {
    blocking: number;
    warnings: number;
    suggestions: number;
    total: number;
  };

  categories: Record<
    string,
    {
      score: number;
      issuesCount: number;
    }
  >;

  categorySummary: Record<string, number>; // compatibility alias

  confidenceSummary: {
    average: number;
    minimum: number;
    belowHumanReviewThreshold: number;
  };

  humanReviewRequired: boolean;
  humanReviewCount: number;

  exportReadiness: ExportReadiness;
  humanReview: HumanReviewSummary;

  integrity: {
    deterministic: boolean;
    algorithm: string;
    canonicalizationVersion?: string;
    timestampDeterministic?: boolean;
  };

  checksumSha256: string;

  // Compatibility fields for legacy consumers
  blockingCount: number;
  warningCount: number;
  suggestionCount: number;
  canExport: boolean;
  confidenceScore: number;
  findings: any[];
  reviewQueue: unknown[];
}

export interface QARecommendation {
  id: string;
  issueId: string;
  type:
    | "TRIM"
    | "MOVE"
    | "REPLACE"
    | "DUCK"
    | "SHIFT_GRAPHIC"
    | "INSERT_RELEASE"
    | "REVIEW_EVIDENCE";
  confidence: number;
  rationale: string;
}

export type PatchOperationType = "ADD" | "REMOVE" | "REPLACE" | "MOVE" | "TRIM";

export interface EditorialPatchOperation {
  op: PatchOperationType;
  path: string;
  value?: unknown;
  oldValue?: unknown;
}

export interface EditorialPatch {
  id: string;
  operations: EditorialPatchOperation[];
  sourceChecksumSha256: string;
  resultingChecksumSha256?: string;
}

export interface QAOverride {
  issueId: string;
  reviewerId: string;
  reason: string;
  scope: "SINGLE_ISSUE";
  expiresAt?: string;
}

export interface QAMetrics {
  totalRulesExecuted: number;
  totalRulesPassed: number;
  totalRulesFailed: number;
  executionTimeMs?: number;
  blockingCount: number;
  warningCount: number;
  suggestionCount: number;
  humanReviewCount: number;
  autoFixAvailableCount: number;
}
