import { Time } from "../../core/types.js";
import { Color } from "../../core/types.js";
import { AssetSource } from "../../media-intelligence/types/index.js";

export type Platform =
  | "youtube"
  | "youtube-shorts"
  | "tiktok"
  | "instagram-reels"
  | "instagram";

export type AspectRatio = "16:9" | "9:16" | "1:1" | "4:5";

export type SectionType =
  | "hook"
  | "setup"
  | "context"
  | "main-point"
  | "example"
  | "escalation"
  | "payoff"
  | "cta"
  | "outro";

export type Framing = "wide" | "medium" | "close" | "extreme-close" | "overhead" | "POV";

export type GraphicSemanticType =
  | "callout"
  | "arrow"
  | "highlight"
  | "statistic"
  | "label"
  | "comparison"
  | "progress"
  | "diagram"
  | "badge";

export type TransitionType =
  | "cut"
  | "fade"
  | "wipe"
  | "zoom"
  | "whip"
  | "match-cut"
  | "flash"
  | "morph";

export interface CreativeConstraint {
  type: string;
  value: unknown;
  priority: number;
}

export interface CreativeBrief {
  objective: string;
  platform: Platform;
  targetDuration: number;
  minDuration?: number;
  maxDuration?: number;
  audience?: string;
  tone?: string[];
  styleId?: string;
  constraints?: CreativeConstraint[];
}

export interface StyleProfile {
  id: string;
  name: string;
  palette: {
    primary: Color;
    secondary: Color;
    accent: Color;
    background: Color;
  };
  captionStyle: "minimal" | "bold" | "karaoke" | "word-pop" | "highlight" | "creator-style";
  defaultTransition: TransitionType;
  motionIntensity: "low" | "medium" | "high";
}

export interface EditorialSection {
  id: string;
  type: SectionType;
  start: Time;
  end: Time;
  objective: string;
  energy: number; // [0, 1]
}

export interface TransitionPlan {
  type: TransitionType;
  duration: number;
}

export interface ShotPlan {
  id: string;
  assetId?: string;
  purpose: string;
  start: Time;
  duration: number;
  framing?: Framing;
  transition?: TransitionPlan;
}

export interface CaptionSegmentPlan {
  text: string;
  start: Time;
  end: Time;
  isEmphasized?: boolean;
}

export interface CaptionPlan {
  style: string;
  segments: CaptionSegmentPlan[];
}

export interface GraphicPlanItem {
  id: string;
  type: GraphicSemanticType;
  purpose: string;
  start: Time;
  duration: number;
  parameters: Record<string, unknown>;
}

export interface GraphicsPlan {
  elements: GraphicPlanItem[];
}

export interface SFXPlan {
  id: string;
  type: "whoosh" | "impact" | "click" | "pop";
  time: Time;
  volume?: number;
}

export interface AudioPlan {
  musicAssetId?: string;
  musicVolume?: number;
  enableDucking?: boolean;
  soundEffects?: SFXPlan[];
}

export interface ScenePlan {
  id: string;
  sectionId: string;
  purpose: string;
  start: Time;
  end: Time;
  shots: ShotPlan[];
}

export interface EditingPlan {
  id: string;
  version: number;
  brief: CreativeBrief;
  style: StyleProfile;
  sections: EditorialSection[];
  scenes: ScenePlan[];
  captions?: CaptionPlan;
  graphics?: GraphicsPlan;
  audio?: AudioPlan;
}

export interface EngineCapability {
  id: string;
  category: "graphics" | "camera" | "caption" | "audio" | "tracking" | "transition";
  description: string;
  parameters: Record<string, string>;
}

export interface EditingIssue {
  severity: "error" | "warning" | "info";
  sectionId?: string;
  message: string;
}

export interface EditingSuggestion {
  message: string;
  targetSectionId?: string;
  action: string;
}

export interface EditingCritique {
  pacingScore: number; // [0, 10]
  varietyScore: number; // [0, 10]
  overallScore: number; // [0, 10]
  issues: EditingIssue[];
  suggestions: EditingSuggestion[];
}
