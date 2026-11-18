/**
 * REQ-082: Editorial Diff & Version Impact Governance Contracts
 */

export type EditorialDiffType =
  | "ADDED"
  | "REMOVED"
  | "MODIFIED"
  | "MOVED"
  | "RESIZED"
  | "REORDERED";

export type ImpactLevel = "NONE" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export type EditorialChangeOrigin = "DIRECT" | "DERIVED";

export interface EditorialRegression {
  id?: string;
  ruleId?: string;
  type?: string;
  description: string;
  severity: "BLOCKING" | "WARNING" | "SUGGESTION";
  category?: string;
  impactLevel?: string;
  entityId?: string;
  sourceDiffId?: string;
  beforeState?: any;
  afterState?: any;
}

export interface EditorialImpact {
  durationDeltaSeconds: number;

  pacingDelta: number;
  pacingScoreBefore?: number;
  pacingScoreAfter?: number;

  attentionDelta: number;
  cognitiveLoadDelta: number;

  contrastDelta: number;

  narrativeImpactScore?: number;
  evidenceImpactScore?: number;
  continuityImpactScore?: number;
  overallImpactScore: number;

  // Compatibility delta metrics
  cutCountDelta?: number;
  pacingAlignmentDelta?: number;

  narrativeImpact?: {
    causalRelationsChanged: number;
    beatsAffected: string[];
    spoilersIntroduced: number;
  };

  continuityImpact?: {
    visualIssuesDelta: number;
    audioIssuesDelta: number;
  };

  evidenceImpact?: {
    claimsAffected: number;
    unsupportedClaimsDelta: number;
  };

  exportImpact?: {
    blockersAdded: number;
    blockersRemoved: number;
  };

  // Structured impact breakdown (§29)
  duration?: {
    beforeSeconds: number;
    afterSeconds: number;
    deltaSeconds: number;
  };
  pacing?: {
    beforeAlignmentScore: number;
    afterAlignmentScore: number;
    delta: number;
  };
  attention?: {
    beforeAverage: number;
    afterAverage: number;
    delta: number;
  };
  cognitiveLoad?: {
    beforeAverage: number;
    afterAverage: number;
    delta: number;
    overloadCountBefore: number;
    overloadCountAfter: number;
  };
  contrast?: {
    beforeScore: number;
    afterScore: number;
    delta: number;
  };
  narrative?: {
    causalChangesCount: number;
    beatChangesCount: number;
    spoilerRiskChanged: boolean;
  };
  continuity?: {
    newViolations: number;
    resolvedViolations: number;
  };
}

export interface EditorialDiff {
  id: string;
  type: EditorialDiffType;
  entityType?: string;
  category?: any;
  origin?: EditorialChangeOrigin;
  entityId: string;
  path?: string;

  before?: unknown;
  after?: unknown;

  delta?: number;
  timestampBefore?: number;
  timestampAfter?: number;

  operation?: string; // compatibility alias
  fingerprint?: string; // compatibility alias

  impact: EditorialImpact;
}

export interface EditorialDiffReport {
  beforeChecksumSha256: string;
  afterChecksumSha256: string;

  diffs: EditorialDiff[];
  changes: EditorialDiff[]; // compatibility alias

  totalChanges: number;

  impactLevel: ImpactLevel;
  impact: EditorialImpact; // compatibility alias

  baseChecksum?: string; // compatibility alias
  candidateChecksum?: string; // compatibility alias
  fromChecksum?: string;
  toChecksum?: string;


  summary: {
    added: number;
    removed: number;
    modified: number;
    moved: number;
    durationDeltaSeconds?: number;
    overallImpactScore?: number;
  };

  requiresRevalidation: boolean;

  checksumSha256: string;

  // Compatibility fields for legacy consumers
  changedEntitiesCount?: number;
  addedCount?: number;
  removedCount?: number;
  modifiedCount?: number;
  riskLevel?: string;
}
