/**
 * Tipos y esquemas de metadatos para el Media / Asset System (Fase 5A).
 */

export type AssetType =
  | "image"
  | "video"
  | "audio"
  | "font"
  | "svg"
  | "unknown";

export type AssetLifecycleState =
  | "unloaded"
  | "loading"
  | "ready"
  | "missing"
  | "error";

export interface AssetSource {
  path: string;
  proxyPath?: string;
  hash?: string; // SHA-256
  uriScheme?: "file" | "asset" | "https" | "http" | "mcp" | "custom";
  [key: string]: unknown;
}

export interface BaseAssetMetadata {
  mimeType?: string;
  sizeBytes?: number;
  [key: string]: unknown;
}

export interface ImageMetadata extends BaseAssetMetadata {
  width: number;
  height: number;
  aspectRatio?: number;
  colorSpace?: string;
  format?: string;
  hasAlpha?: boolean;
}

export interface VideoMetadata extends BaseAssetMetadata {
  width: number;
  height: number;
  duration: number; // en segundos (> 0)
  fps: number; // framerate (> 0)
  codec?: string;
  bitrate?: number;
  hasAudio?: boolean;
  hasAlpha?: boolean;
  aspectRatio?: number;
}

export interface AudioMetadata extends BaseAssetMetadata {
  duration: number; // en segundos (> 0)
  sampleRate?: number; // ej. 44100, 48000 (> 0)
  channels?: number; // 1 = mono, 2 = stereo
  codec?: string;
  bitrate?: number;
}

export interface FontMetadata extends BaseAssetMetadata {
  family: string;
  style?: string; // "regular", "italic"
  weight?: number; // 400, 700, 900
  format?: string; // "ttf", "otf", "woff2"
}

export interface SVGMetadata extends BaseAssetMetadata {
  width?: number;
  height?: number;
  viewBox?: string;
}

export type AssetMetadata =
  | ImageMetadata
  | VideoMetadata
  | AudioMetadata
  | FontMetadata
  | SVGMetadata
  | BaseAssetMetadata;
