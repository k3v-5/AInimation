export * from "../contracts/editorial-diff.types.js";

export interface TemporalImpact {
  durationDeltaSeconds: number;
  startTimeDeltaSeconds: number;
  endTimeDeltaSeconds: number;
  affectedRangeStart: number;
  affectedRangeEnd: number;
  downstreamShiftSeconds: number;
}

export interface EditorialImpactReport {
  attentionDelta?: number;
  cognitiveLoadDelta?: number;
  contrastDelta?: number;
  pacingAlignmentDelta?: number;
  narrativeImpact: "NONE" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  continuityImpact: "NONE" | "LOW" | "MEDIUM" | "HIGH";
  evidenceImpact: "NONE" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
}
