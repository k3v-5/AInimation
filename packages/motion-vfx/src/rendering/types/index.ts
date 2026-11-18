import { Color, Time } from "../../core/types.js";
import { TimeRange } from "../../timeline/core/TimeRange.js";

export type RenderState =
  | "queued"
  | "preparing"
  | "rendering"
  | "encoding"
  | "completed"
  | "failed"
  | "cancelled"
  | "paused";

export type RenderStage =
  | "preparing"
  | "loading-assets"
  | "evaluating"
  | "compositing"
  | "encoding"
  | "finalizing";

export type RenderPriority = "low" | "normal" | "high" | "critical";

export type RenderQuality = "draft" | "preview" | "final" | "master";

export type VideoCodec = "H.264" | "H.265" | "AV1" | "ProRes" | "Raw";
export type AudioCodec = "AAC" | "MP3" | "PCM" | "Opus";
export type ContainerFormat = "mp4" | "mov" | "webm" | "mkv";

export interface OutputProfile {
  id: string;
  name: string;
  width: number;
  height: number;
  fps: number;
  codec: VideoCodec;
  audioCodec: AudioCodec;
  container: ContainerFormat;
  bitrateKbps?: number;
}

export interface RenderSettings {
  quality: RenderQuality;
  resolutionScale: number; // e.g. 0.5 para preview, 1.0 para final
  fps?: number;
  enableMotionBlur: boolean;
  enableEffects: boolean;
  useProxies: boolean;
  colorManagement: boolean;
}

export interface FrameContext {
  frame: number;
  time: Time;
  fps: number;
  width: number;
  height: number;
  quality: RenderQuality;
}

export interface RenderFrame {
  frameNumber: number;
  time: Time;
  width: number;
  height: number;
  channels: number; // e.g. 4 para RGBA
  data?: Uint8ClampedArray;
  metadata?: Record<string, unknown>;
}

export interface RenderProgress {
  frame: number;
  totalFrames: number;
  timeRendered: Time;
  percentage: number;
  fps: number;
  etaSeconds?: number;
  stage: RenderStage;
}

export interface RenderJob {
  id: string;
  projectId: string;
  outputProfile: OutputProfile;
  range?: TimeRange;
  priority: RenderPriority;
  settings: RenderSettings;
  state: RenderState;
  rendererVersion: string;
}

export interface RenderManifest {
  jobId: string;
  projectId: string;
  rendererVersion: string;
  framesCompleted: number;
  totalFrames: number;
  outputProfile: OutputProfile;
  outputPath: string;
  duration: Time;
  completedAt: string;
}

export interface RenderValidationResult {
  valid: boolean;
  issues: string[];
}
