import { Time } from "../../core/types.js";

export type MaskType = "rectangle" | "ellipse" | "bezier";
export type MaskMode = "add" | "subtract" | "intersect" | "difference";
export type TrackMatteType = "alpha" | "alpha-inverted" | "luma" | "luma-inverted";

export interface Vec2 {
  x: number;
  y: number;
}

export interface MaskPoint {
  position: Vec2;
  inTangent?: Vec2;
  outTangent?: Vec2;
}

export interface MaskPath {
  closed: boolean;
  points: MaskPoint[];
}

export interface Mask {
  id: string;
  type: MaskType;
  path: MaskPath;
  mode: MaskMode;
  feather: number; // Radio de desenfoque en px
  expansion: number; // Expansión / contracción en px
  opacity: number; // [0, 1]
  inverted?: boolean;
}

export interface Matte {
  width: number;
  height: number;
  alpha: Float32Array; // Array 1D de tamaño width * height con valores alfa [0, 1]
}

export interface RotoFrame {
  time: Time;
  path: MaskPath;
}

export interface RotoMask {
  id: string;
  type: MaskType;
  mode: MaskMode;
  feather: number;
  expansion: number;
  opacity: number;
  frames: RotoFrame[];
}

export interface SegmentationOptions {
  threshold?: number;
  refineEdges?: boolean;
}

export interface SegmentationResult {
  matte: Matte;
  confidence?: number;
}

export interface SegmentationBackend {
  segment(frameData: unknown, options?: SegmentationOptions): Promise<SegmentationResult>;
}
