import { z } from "zod";

/** Modo de tasa de fotogramas detectado */
export type FrameRateMode = "CFR" | "VFR" | "UNKNOWN";

export const FrameRateModeSchema = z.enum(["CFR", "VFR", "UNKNOWN"]);

/** Orientación visual del medio */
export type MediaOrientation = "LANDSCAPE" | "PORTRAIT" | "SQUARE";

export const MediaOrientationSchema = z.enum(["LANDSCAPE", "PORTRAIT", "SQUARE"]);

/** Metadatos de stream de video */
export interface VideoStreamMetadata {
  codec: string;
  width: number;
  height: number;
  aspectRatio: string; // ej. "16:9", "9:16"
  fps: number;
  frameRateMode: FrameRateMode;
  durationSeconds: number;
  bitrateBps?: number;
  orientation: MediaOrientation;
}

export const VideoStreamMetadataSchema = z.object({
  codec: z.string().min(1),
  width: z.number().int().positive(),
  height: z.number().int().positive(),
  aspectRatio: z.string().min(1),
  fps: z.number().positive(),
  frameRateMode: FrameRateModeSchema,
  durationSeconds: z.number().positive(),
  bitrateBps: z.number().positive().optional(),
  orientation: MediaOrientationSchema,
});

/** Metadatos de stream de audio */
export interface AudioStreamMetadata {
  codec: string;
  sampleRateHz: number;
  channels: number;
  bitrateBps?: number;
  durationSeconds: number;
}

export const AudioStreamMetadataSchema = z.object({
  codec: z.string().min(1),
  sampleRateHz: z.number().int().positive(),
  channels: z.number().int().positive(),
  bitrateBps: z.number().positive().optional(),
  durationSeconds: z.number().positive(),
});

/** Huella criptográfica y dimensional de un archivo */
export interface MediaFingerprint {
  checksumSha256: string;
  sizeBytes: number;
  lastModifiedTimestamp: number;
  durationSeconds?: number;
  width?: number;
  height?: number;
  fps?: number;
}

export const MediaFingerprintSchema = z.object({
  checksumSha256: z.string().min(64).max(64),
  sizeBytes: z.number().int().nonnegative(),
  lastModifiedTimestamp: z.number().positive(),
  durationSeconds: z.number().positive().optional(),
  width: z.number().int().positive().optional(),
  height: z.number().int().positive().optional(),
  fps: z.number().positive().optional(),
});

/** Archivo multimedia probado e indexado durante la ingesta */
export interface IngestedMediaFile {
  id: string;
  absolutePath: string;
  filename: string;
  extension: string;
  mimeType: string;
  fingerprint: MediaFingerprint;
  videoStream?: VideoStreamMetadata;
  audioStream?: AudioStreamMetadata;
  isReadOnly: boolean;
  ingestedAtTimestamp: number;
}

export const IngestedMediaFileSchema = z.object({
  id: z.string().min(1),
  absolutePath: z.string().min(1),
  filename: z.string().min(1),
  extension: z.string().min(1),
  mimeType: z.string().min(1),
  fingerprint: MediaFingerprintSchema,
  videoStream: VideoStreamMetadataSchema.optional(),
  audioStream: AudioStreamMetadataSchema.optional(),
  isReadOnly: z.boolean().default(true),
  ingestedAtTimestamp: z.number().positive(),
});

/** Reporte de ingesta del directorio fuente */
export interface IngestionReport {
  inputDirectory: string;
  totalFilesScanned: number;
  validMediaFiles: IngestedMediaFile[];
  corruptedOrUnsupportedFiles: Array<{
    path: string;
    reason: string;
  }>;
  totalDurationSeconds: number;
  ingestionDurationMs: number;
}
