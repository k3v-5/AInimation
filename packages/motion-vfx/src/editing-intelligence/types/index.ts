import { Time } from "../../core/types.js";

export type PacingProfileType = "fast_social" | "medium_social" | "educational" | "cinematic";

export type HookType = "curiosity" | "statement" | "question" | "promise";

export interface TranscriptWord {
  word: string;
  start: Time;
  end: Time;
}

export interface EnrichedSegment {
  id: string;
  start: Time;
  end: Time;
  text: string;
  speakerId?: string;
  words: TranscriptWord[];
  semanticTags: string[];
  importance: number; // [0, 1]
}

export interface HookCandidate {
  start: Time;
  end: Time;
  score: number; // [0, 1]
  type: HookType;
  text: string;
  explanation: string;
}

export interface ContentModel {
  segments: EnrichedSegment[];
  hooks: HookCandidate[];
  totalDuration: Time;
  primaryTopic: string;
}

export interface PacingProfile {
  name: PacingProfileType;
  averageShotDuration: Time;
  minShotDuration: Time;
  maxShotDuration: Time;
  motionDensity: number;
  sfxDensity: number;
}

export interface DecisionLogEntry {
  time: Time;
  action: string;
  reason: string;
  confidence: number;
}

export interface PlannedScene {
  id: string;
  role: "hook" | "context" | "problem" | "explanation" | "reveal" | "cta";
  start: Time;
  duration: Time;
  shotType: "talking_head" | "b_roll" | "motion_graphic";
  brollKeyword?: string;
}

export interface SemanticEditPlan {
  id: string;
  pacingProfile: PacingProfileType;
  scenes: PlannedScene[];
  decisionLog: DecisionLogEntry[];
  parameters: Record<string, unknown>;
}

export interface PlanPatch {
  operation: "add" | "remove" | "replace" | "modify";
  target: string;
  changes: Record<string, unknown>;
}

export interface PlanValidationResult {
  isValid: boolean;
  issues: string[];
  repairedPlan?: SemanticEditPlan;
}
