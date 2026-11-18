import { QACertificationStatus } from "./editorial-qa-severity.js";
import { EditorialIssueSeverity } from "../contracts/editorial-qa.types.js";
import { EditorialIR } from "../ir/editorial-ir.types.js";
import { StyleProfile } from "../../styles/StyleProfileManager.js";

export { QACertificationStatus };

/**
 * REQ-QA-005: 17 Categorías canónicas de issues editoriales.
 */
export type EditorialIssueCategory =
  | "STRUCTURE"
  | "TIMING"
  | "MEDIA"
  | "AUDIO"
  | "VISUAL_CONTINUITY"
  | "SAFE_ZONE"
  | "NARRATIVE"
  | "EVIDENCE"
  | "ATTENTION"
  | "COGNITIVE_LOAD"
  | "CONTRAST"
  | "PACING"
  | "STYLE"
  | "EXPORT"
  | "CONFIDENCE"
  | "INTEGRITY";

export interface EditorialIssueEvidence {
  claimId?: string;
  evidenceId?: string;
  sourceUri?: string;
  description?: string;
  confidence?: number;
}

/**
 * REQ-QA-004: Contrato formal de issue editorial.
 */
export interface EditorialIssue {
  id: string;
  ruleId: string;
  severity: EditorialIssueSeverity;
  category: EditorialIssueCategory;

  timestampSeconds?: number;
  durationSeconds?: number;

  entityIds: string[];

  title: string;
  message: string;

  expected?: unknown;
  actual?: unknown;

  confidence: number;

  autoFixAvailable: boolean;

  recommendation?: string;

  evidence?: EditorialIssueEvidence[];

  fingerprint: string;
}

/**
 * REQ-QA-022: Integridad criptográfica del proceso de auditoría.
 */
export interface EditorialIntegrityReport {
  inputChecksumSha256: string;
  outputChecksumSha256: string;
  canonicalizationVersion: string;
  algorithm: "SHA-256";
  deterministic: true;
}

export type { EditorialQAReport } from "../contracts/editorial-qa.types.js";

/**
 * Contexto de evaluación para las reglas del linter.
 */
export interface EditorialQAContext {
  ir: EditorialIR;
  profile?: StyleProfile;
  config: EditorialQAConfig;
  assetRegistry?: Record<string, { exists: boolean; codec?: string; resolution?: [number, number]; framerate?: number }>;
  evidenceIndex?: Record<string, { verified: boolean; confidence: number; source?: string }>;
}

/**
 * REQ-QA-049: Configuración del Linter Editorial.
 */
export interface EditorialQAConfig {
  enabledRules: string[];
  thresholds: {
    humanReviewConfidence: number;
    maxCognitiveLoad: number;
    minAttention: number;
    minPacingAlignment: number;
    maxLowTensionDuration: number;
    maxHighTensionRun: number;
  };
  failOnWarnings: boolean;
  requireEvidence: boolean;
  requireSafeZones: boolean;
  deterministic: true;
}

/**
 * REQ-QA-066: Identidad canónica de ejecución para auditoría.
 */
export interface QARunIdentity {
  inputChecksumSha256: string;
  profileChecksumSha256: string;
  configChecksumSha256: string;
  ruleSetVersion: string;
  canonicalizationVersion: string;
  runChecksumSha256: string;
}

/**
 * REQ-QA-046: Propuesta de auto-reparación no destructiva.
 */
export interface EditorialFixProposal {
  id: string;
  issueId: string;
  operation: "MOVE" | "TRIM" | "SHIFT" | "DUCK" | "REPLACE" | "REMOVE" | "ADD";
  parameters: Record<string, unknown>;
  confidence: number;
}

/**
 * REQ-QA-072: Estado de ejecución interna del linter.
 */
export type QAExecutionStatus = "SUCCESS" | "PARTIAL" | "FAILED";
