import {
  CreativeBrief,
  EditingPlan,
  EditorialSection,
  Framing,
  ScenePlan,
  ShotPlan,
  StyleProfile,
} from "../../ai-planner/types/index.js";

export {
  CreativeBrief,
  EditingPlan,
  EditorialSection,
  Framing,
  ScenePlan,
  ShotPlan,
  StyleProfile,
};
import { SpeechData } from "../../audio-intelligence/types/index.js";
import { Time } from "../../core/types.js";
import { Asset, BrollCandidate } from "../../media-intelligence/types/index.js";

export type AgentRole = "story" | "visual" | "audio" | "caption" | "motion" | "director";

export type PlanningState =
  | "idle"
  | "planning"
  | "reviewing"
  | "resolving"
  | "validating"
  | "revising"
  | "approved"
  | "failed";

export interface Recommendation {
  type: string;
  target?: string;
  priority: number;
  reasoning: string;
  parameters: Record<string, unknown>;
}

export interface AgentProposal {
  agentId: string;
  role: AgentRole;
  confidence: number;
  recommendations: Recommendation[];
}

export interface StoryBeat {
  id: string;
  start: Time;
  end: Time;
  purpose: string;
  energy: number;
  importance: number;
}

export interface AgentContext {
  brief: CreativeBrief;
  style: StyleProfile;
  transcript?: SpeechData;
  availableAssets?: Asset[];
  existingPlan?: Partial<EditingPlan>;
}

export interface AgentConflict {
  agents: string[];
  conflictType: "timing" | "asset" | "style" | "budget";
  proposals: Recommendation[];
}

export interface ConflictResolution {
  selectedProposalIndex: number;
  reasoning: string;
  resolvedParameters: Record<string, unknown>;
}

export interface DirectorPolicy {
  priorities: Array<"narrative" | "audio_beat" | "visual" | "platform">;
  maxIterations: number;
  qualityThreshold: number;
}

export interface DecisionLogEntry {
  agentId: string;
  action: string;
  reasoning: string;
  timestamp: string;
}

export interface PlanningSession {
  id: string;
  traceId: string;
  state: PlanningState;
  brief: CreativeBrief;
  style: StyleProfile;
  plan?: EditingPlan;
  decisions: DecisionLogEntry[];
  conflicts: AgentConflict[];
}

export interface UserFeedback {
  category: "style" | "story" | "audio" | "visual" | "caption" | "motion";
  instruction: string;
}

export interface EditingAgent {
  readonly id: string;
  readonly role: AgentRole;
  analyze(context: AgentContext): Promise<AgentProposal>;
}
