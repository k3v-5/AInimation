import { Color, Time, Vector2 } from "../../core/types.js";

export type StaggerDirection = "forward" | "reverse" | "center";

export type MotionIntensity = "subtle" | "medium" | "strong" | "extreme";

export type MotionBudgetType = "low" | "medium" | "high";

export interface KineticTextSegment {
  text: string;
  index: number;
  startDelay: Time;
  duration: Time;
  isEmphasized: boolean;
  scale: number;
  color?: string;
  glow?: boolean;
}

export interface CameraDynamicsConfig {
  mode: "static" | "snapZoom" | "subtlePush" | "dramaticPush" | "shake";
  intensity: number; // [0, 1]
  seed?: number;
  duration: Time;
}

export interface Particle {
  id: number;
  position: Vector2;
  velocity: Vector2;
  size: number;
  color: string;
  opacity: number;
  lifetime: Time;
  age: Time;
}

export interface ParticleEmitterConfig {
  preset: "confetti" | "spark" | "dust" | "celebration";
  count: number;
  seed: number;
  duration: Time;
}

export interface MotionMacro {
  id: string;
  name: string;
  description: string;
  parameters: Record<string, unknown>;
  elements: {
    type: "text" | "camera" | "shape" | "sfx" | "particles";
    timing: { start: Time; duration: Time };
    params: Record<string, unknown>;
  }[];
}

export interface MotionComplexityResult {
  score: number; // [0, 1]
  budget: MotionBudgetType;
  isWithinBudget: boolean;
  activeElementsCount: number;
}
