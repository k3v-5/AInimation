/**
 * RF-056: Intelligent Performance & Semantic Trimming Engine — Type Definitions
 */

export type PerformanceMarker =
  | "BREATH"
  | "LAUGH"
  | "HESITATION"
  | "REFLECTIVE_PAUSE"
  | "FILLER"
  | "STUTTER"
  | "FALSE_START"
  | "WORD_REPETITION"
  | "TECHNICAL_ERROR"
  | "EMPHATIC_PAUSE"
  | "EMOTIONAL_REACTION"
  | "UNCERTAINTY";

export interface PerformanceSegment {
  id: string;
  sourceClipId: string;
  startSeconds: number;
  endSeconds: number;
  transcript: string;
  confidence: number;
  markers: PerformanceMarker[];
  evidenceProtection?: boolean;
  beatId?: string;
  narrativeRole?: string;
}

export type RedundancyRecommendation = "KEEP_BOTH" | "KEEP_A" | "KEEP_B" | "REVIEW";

export interface RedundancyCandidate {
  id: string;
  segmentAId: string;
  segmentBId: string;
  semanticSimilarity: number;
  informationOverlap: number;
  temporalDistanceSeconds: number;
  narrativeRoleA?: string;
  narrativeRoleB?: string;
  redundancyScore: number;
  recommendation: RedundancyRecommendation;
  reason: string;
  confidence: number;
}

export type PreservationAction = "PRESERVE" | "TRIM" | "REVIEW";

export interface PreservationDecision {
  marker: PerformanceMarker;
  action: PreservationAction;
  preservationScore: number;
  authenticityScore: number;
  technicalDefectScore: number;
  reason: string;
  confidence: number;
}

export interface TakeCandidate {
  id: string;
  transcript: string;
  sourceClipId: string;
  startSeconds: number;
  endSeconds: number;
  semanticIntegrity: number;
  phoneticClarity: number;
  vocalEnergy: number;
  visualStability: number;
  eyeContact: number;
  naturalPerformance: number;
  continuity: number;
  audioQuality: number;
}

export interface BestTakeSelection {
  takeGroupId: string;
  selectedTakeId: string;
  winnerScore: number;
  runnerUpScore?: number;
  scoreDifference?: number;
  isAutoSelected: boolean;
  desempateApplied?: string;
  recommendation: "SELECT" | "REVIEW";
}

export type TrimAction = "KEEP" | "TRIM" | "REPLACE_TAKE" | "MERGE" | "REVIEW";

export interface AudioTransitionProposal {
  startSeconds: number;
  durationSeconds: number;
  type: "MICRO_CROSSFADE";
}

export interface TrimProposal {
  id: string;
  sourceClipId: string;
  startSeconds: number;
  endSeconds: number;
  action: TrimAction;
  reason: string;
  confidence: number;
  audioTransition?: AudioTransitionProposal;
}

export interface PerformanceReviewItem {
  id: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  reason: string;
  candidateIds: string[];
  confidence: number;
  affectedRange: {
    startSeconds: number;
    endSeconds: number;
  };
}

export interface TrimmingMetrics {
  originalDurationSeconds: number;
  finalDurationSeconds: number;
  removedDurationSeconds: number;
  reductionRatio: number;
  preservedSemanticCoverage: number;
  preservedPerformanceCoverage: number;
}

export type IntelligentTrimStatus =
  | "WITHIN_SAFE_BOUNDS"
  | "PROPOSALS_READY"
  | "REVIEW_REQUIRED";

export interface IntelligentTrimReport {
  engineVersion: string;
  processedSegments: number;
  redundancyCandidates: number;
  trimsProposed: number;
  trimsAccepted: number;
  trimsRejected: number;
  takesEvaluated: number;
  automaticTakeSelections: number;
  reviewItems: number;

  metrics: TrimmingMetrics;

  proposals: TrimProposal[];
  takeSelections: BestTakeSelection[];
  redundancy: RedundancyCandidate[];
  preservation: PreservationDecision[];
  reviewQueue: PerformanceReviewItem[];

  status: IntelligentTrimStatus;
  checksumSha256: string;
}
