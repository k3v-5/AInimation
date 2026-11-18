import { Time } from "../../core/types.js";

export type AssetSourceType = "user" | "stock" | "generated" | "screen_capture";

export type OrientationType = "portrait" | "landscape" | "square";

export type SafeRegionSide = "left" | "center" | "right" | "top" | "bottom";

export interface LicenseInfo {
  source: AssetSourceType;
  attributionRequired: boolean;
  commercialUse: boolean;
}

export interface ShotMetadata {
  id: string;
  start: Time;
  end: Time;
  objects: string[];
  hasFace: boolean;
  textSafeSide: SafeRegionSide;
  quality: number; // [0, 1]
  energy: number; // [0, 1]
}

export interface IndexedAsset {
  id: string;
  uri: string;
  fingerprint: string;
  duration: Time;
  orientation: OrientationType;
  tags: string[];
  shots: ShotMetadata[];
  license: LicenseInfo;
  usageCount: number;
}

export interface BRollQuery {
  intent: string;
  targetDuration: Time;
  preferredOrientation?: OrientationType;
  textSafeSide?: SafeRegionSide;
  minQuality?: number;
  minEnergy?: number;
  avoidAssetIds?: string[];
}

export interface ScoreBreakdown {
  semanticRelevance: number;
  quality: number;
  durationFit: number;
  textSafeMatch: number;
  reusePenalty: number;
  total: number;
}

export interface RankedCandidate {
  assetId: string;
  subclipStart: Time;
  subclipEnd: Time;
  score: ScoreBreakdown;
  rationale: string;
}

export interface BRollResolution {
  primary: RankedCandidate;
  alternatives: RankedCandidate[];
}
