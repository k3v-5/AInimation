import crypto from "node:crypto";
import { EditorialRemediation } from "./editorial-remediation.js";

/**
 * REQ-030 §3: Modelo de Severidad Canónico
 */
export type EditorialSeverity = "BLOCKING" | "WARNING" | "SUGGESTION";

/**
 * REQ-030 §5: Tipos de Evidencia Estructurada
 */
export type EditorialEvidenceType =
  | "IR_NODE"
  | "TIMECODE"
  | "NUMERIC_VALUE"
  | "RULE"
  | "DEPENDENCY"
  | "METRIC"
  | "SOURCE_ASSET"
  | "NARRATIVE_BEAT"
  | "CLAIM"
  | "CALCULATION";

export interface EditorialEvidence {
  type: EditorialEvidenceType;
  reference: string;
  value?: unknown;
  description: string;
}

/**
 * REQ-030 §4: 14 Categorías de Hallazgos Editoriales
 */
export type EditorialFindingCategory =
  | "STRUCTURAL"
  | "TEMPORAL"
  | "NARRATIVE"
  | "EVIDENCE"
  | "CONTINUITY"
  | "AUDIO"
  | "VISUAL"
  | "COGNITIVE"
  | "COGNITIVE_LOAD"
  | "ATTENTION"
  | "PACING"
  | "CONTRAST"
  | "EXPORT"
  | "SECURITY"
  | "PERFORMANCE";

/**
 * REQ-030 §4: Contrato Principal de Hallazgo Editorial
 */
export interface EditorialQAFinding {
  id: string;
  ruleId: string;
  severity: EditorialSeverity;
  category: EditorialFindingCategory;

  title: string;
  message: string;

  timestampSeconds?: number;
  durationSeconds?: number;

  affectedNodeIds: string[];

  expected?: unknown;
  actual?: unknown;

  confidence: number;

  remediation?: EditorialRemediation;
  evidence: EditorialEvidence[];

  fingerprint: string;

  // Aliases de retrocompatibilidad con tests anteriores
  entityIds?: string[];
  affectedEntityIds?: string[];
  reason?: string;
  description?: string;
  autoFixAvailable?: boolean;
  autoFixable?: boolean;
  proposalId?: string;
  requiresHumanReview?: boolean;
}

/**
 * Genera un fingerprint determinista e inmutable para un hallazgo.
 */
export function computeFindingFingerprint(
  ruleId: string,
  category: string,
  affectedNodeIds: string[],
  timestampSeconds?: number
): string {
  const sortedNodes = [...affectedNodeIds].sort().join(",");
  const ts = timestampSeconds !== undefined ? Number(timestampSeconds.toFixed(3)) : "global";
  const raw = `${ruleId}::${category}::${sortedNodes}::${ts}`;
  return crypto.createHash("sha256").update(raw, "utf8").digest("hex").slice(0, 16);
}

/**
 * Constructor de hallazgos editoriales con cálculo de fingerprint e integridad.
 */
export function createFinding(params: {
  id?: string;
  ruleId: string;
  severity: EditorialSeverity;
  category: EditorialFindingCategory;
  title: string;
  message: string;
  timestampSeconds?: number;
  durationSeconds?: number;
  affectedNodeIds?: string[];
  expected?: unknown;
  actual?: unknown;
  confidence?: number;
  remediation?: EditorialRemediation;
  evidence?: EditorialEvidence[];
}): EditorialQAFinding {
  const affectedNodeIds = params.affectedNodeIds ?? [];
  const confidence = Math.max(0, Math.min(1, params.confidence ?? 1.0));
  const fingerprint = computeFindingFingerprint(
    params.ruleId,
    params.category,
    affectedNodeIds,
    params.timestampSeconds
  );
  const id = params.id || `f_${params.ruleId.toLowerCase().replace(/[^a-z0-9]/g, "_")}_${fingerprint.slice(0, 8)}`;

  return {
    id,
    ruleId: params.ruleId,
    severity: params.severity,
    category: params.category,
    title: params.title,
    message: params.message,
    timestampSeconds: params.timestampSeconds,
    durationSeconds: params.durationSeconds,
    affectedNodeIds,
    expected: params.expected,
    actual: params.actual,
    confidence,
    remediation: params.remediation,
    evidence: params.evidence ?? [],
    fingerprint,

    // Aliases para retrocompatibilidad
    entityIds: affectedNodeIds,
    reason: params.message,
    autoFixAvailable: params.remediation !== undefined,
  };
}
