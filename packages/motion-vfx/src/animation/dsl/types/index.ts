import { EasingName, Time, Vector2 } from "../../../core/types.js";
import { SlideDirection } from "../../primitives/types.js";
import { StaggerMode } from "../../composition/types.js";
import { AnimationNode } from "../../AnimationNode.js";

export type DSLPrimitiveType =
  | "fadeIn"
  | "fadeOut"
  | "slideIn"
  | "slideOut"
  | "scaleIn"
  | "scaleOut"
  | "rotateIn"
  | "rotateOut";

export type DSLCompositionType =
  | "parallel"
  | "sequence"
  | "delay"
  | "hold"
  | "repeat"
  | "offset"
  | "stagger";

export type DSLNodeType = DSLPrimitiveType | DSLCompositionType | "preset" | "textAnimation";

export interface DSLMotionConfig {
  type: string;
  amount?: number;
  mass?: number;
  stiffness?: number;
  damping?: number;
  velocity?: number;
  preset?: string;
  amplitude?: number;
  period?: number;
  frequency?: number;
  decay?: boolean | number;
  bounces?: number;
  seed?: number;
}

export interface DSLBaseNode {
  id?: string;
  type: DSLNodeType;
  delay?: number | string;
  priority?: number;
}

export interface DSLBasicAnimationNode extends DSLBaseNode {
  type: DSLPrimitiveType;
  target: string;
  duration?: number | string;
  easing?: EasingName;
  motion?: string | DSLMotionConfig;
  direction?: SlideDirection;
  distance?: number | string;
  from?: number | Vector2 | string;
  to?: number | Vector2 | string;
}

export interface DSLCompositionNode extends DSLBaseNode {
  type: DSLCompositionType;
  duration?: number | string; // para delay / hold
  count?: number; // para repeat
  offsetTime?: number | string; // para offset
  staggerDelay?: number | string; // para stagger
  staggerMode?: StaggerMode; // para stagger
  targets?: string[]; // para stagger con múltiples targets
  children?: DSLNode[];
}

export interface DSLPresetNode extends DSLBaseNode {
  type: "preset";
  name: string;
  target: string;
  overrides?: Record<string, unknown>;
}

export interface DSLTextAnimationNode extends DSLBaseNode {
  type: "textAnimation";
  target: string;
  text?: string;
  scope?: "element" | "line" | "word" | "character";
  order?: "forward" | "reverse" | "random" | "center" | "edges";
  stagger?: { delay?: number | string; wordDelay?: number | string; characterDelay?: number | string } | number | string;
  animation: DSLBasicAnimationNode;
  seed?: number;
}

export type DSLNode = DSLBasicAnimationNode | DSLCompositionNode | DSLPresetNode | DSLTextAnimationNode;

export interface DSLDocument {
  version: 1;
  variables?: Record<string, number | string>;
  animations: DSLNode[];
}

export interface DiagnosticError {
  path: string;
  code: string;
  message: string;
  received?: unknown;
}

export interface AnimationIR {
  version: 1;
  rootNodes: AnimationNode[];
  metadata: {
    nodeCount: number;
    totalDuration: Time;
    targets: string[];
  };
}
