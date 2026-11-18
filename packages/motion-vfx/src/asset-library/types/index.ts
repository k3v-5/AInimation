import { Time } from "../../core/types.js";
import { AssetType } from "../../media-intelligence/types/index.js";

export type LicenseType = "unknown" | "personal" | "royalty-free" | "licensed" | "restricted";

export type CameraShotType = "wide" | "medium" | "close-up" | "macro" | "overhead";
export type CameraMovement = "static" | "pan" | "tilt" | "zoom" | "handheld" | "tracking";

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface CompositionAnalysis {
  subjectBox?: BoundingBox;
  faceBox?: BoundingBox;
  negativeSpaceArea: number; // [0, 1]
  dominantColors: string[];
  safeCaptionZone: "top" | "center" | "bottom";
}

export interface ShotAnalysis {
  objects: string[];
  environment: string[];
  action: string[];
  camera: {
    shot: CameraShotType;
    movement: CameraMovement;
  };
  qualityScore: number; // [0, 1]
  composition?: CompositionAnalysis;
}

export interface Shot {
  id: string;
  assetId: string;
  start: Time;
  end: Time;
  duration: Time;
  description: string;
  analysis: ShotAnalysis;
  embedding?: number[];
}

export interface AssetProvenance {
  source: string;
  license: LicenseType;
  creator?: string;
  importDate: string;
  originalPath: string;
}

export interface IntelligentAsset {
  id: string;
  type: AssetType;
  filename: string;
  duration?: Time;
  provenance: AssetProvenance;
  shots: Shot[];
  tags: string[];
  userCorrections: Record<string, string>; // originalTag -> userCorrectedTag
  metadata: {
    width?: number;
    height?: number;
    fps?: number;
    codec?: string;
    fileSizeBytes?: number;
    sha256?: string;
  };
}

export interface BestVisualQuery {
  concept: string;
  duration: Time;
  orientation?: "vertical" | "landscape" | "square";
  allowRestricted?: boolean;
}

export interface BestVisualResult {
  shot: Shot;
  asset: IntelligentAsset;
  confidence: number;
  reasoning: string;
}

export interface SemanticSearchOptions {
  minDuration?: Time;
  maxDuration?: Time;
  orientation?: "vertical" | "landscape" | "square";
  license?: LicenseType;
  tags?: string[];
  limit?: number;
}
