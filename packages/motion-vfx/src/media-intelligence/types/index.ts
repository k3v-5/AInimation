import { Time } from "../../core/types.js";
import { SpeechData } from "../../audio-intelligence/types/index.js";

export type AssetType =
  | "video"
  | "audio"
  | "image"
  | "font"
  | "subtitle"
  | "graphic"
  | "sequence";

export type AssetStatus = "available" | "missing" | "offline";

export interface Rect {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface AssetSource {
  uri: string;
  size?: number;
  checksum?: string; // SHA-256
}

export interface AssetMetadata {
  filename: string;
  mimeType: string;
  duration?: Time;
  width?: number;
  height?: number;
  frameRate?: number;
  sampleRate?: number;
  channels?: number;
  codec?: string;
  bitrate?: number;
}

export interface MediaQuality {
  sharpness: number; // [0, 1]
  exposure: number; // [0, 1]
  stability: number; // [0, 1]
  resolutionScore: number; // [0, 1]
  overall: number; // [0, 1]
}

export interface FaceDetection {
  bbox: Rect;
  confidence: number;
}

export interface ObjectDetection {
  label: string;
  bbox: Rect;
  confidence: number;
}

export interface VisualEmbedding {
  vector: number[];
  model: string;
}

export interface TextEmbedding {
  vector: number[];
  model: string;
}

export interface ShotAnalysis {
  description?: string;
  tags?: string[];
  objects?: ObjectDetection[];
  faces?: FaceDetection[];
  quality?: MediaQuality;
  embedding?: VisualEmbedding;
}

export interface MediaShot {
  id: string;
  start: Time;
  end: Time;
  keyframes: Time[];
  analysis?: ShotAnalysis;
}

export interface ClipRange {
  assetId: string;
  start: Time;
  end: Time;
}

export interface BrollCandidate {
  assetId: string;
  shotId?: string;
  range: ClipRange;
  relevance: number;
  visualScore?: number;
  semanticScore?: number;
  qualityScore?: number;
  finalScore: number;
}

export interface Asset {
  id: string;
  type: AssetType;
  source: AssetSource;
  metadata: AssetMetadata;
  status: AssetStatus;
  shots?: MediaShot[];
  transcript?: SpeechData;
  embedding?: TextEmbedding;
  tags?: string[];
}

export interface AssetQuery {
  type?: AssetType;
  tags?: string[];
  text?: string;
  semanticQuery?: string;
  minDuration?: number;
  maxDuration?: number;
  minWidth?: number;
  minHeight?: number;
}

export interface SmartCollection {
  id: string;
  name: string;
  query: AssetQuery;
}

export interface AssetContext {
  asset: Asset;
  relevantShots: BrollCandidate[];
  transcript?: SpeechData;
  summary: string;
}
