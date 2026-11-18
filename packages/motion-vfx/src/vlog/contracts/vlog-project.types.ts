import { z } from "zod";
import { SupportedLocaleSchema } from "./language.types.js";
import { VlogAspectRatio, SupportedLocale } from "./vlog.constants.js";

/** Beat narrativo dramático del vlog o documental */
export type VlogNarrativeBeat =
  | "HOOK"
  | "SETUP"
  | "CONTEXT"
  | "DEVELOPMENT"
  | "CLIMAX"
  | "REFLECTION"
  | "CTA"
  | "OUTRO";

export const VlogNarrativeBeatSchema = z.enum([
  "HOOK",
  "SETUP",
  "CONTEXT",
  "DEVELOPMENT",
  "CLIMAX",
  "REFLECTION",
  "CTA",
  "OUTRO",
]);

/** Modos de bloqueo manual humano sobre clips */
export type ClipLockType = "FORCE" | "FORBIDDEN" | "PREFERRED" | "NONE";

export const ClipLockTypeSchema = z.enum(["FORCE", "FORBIDDEN", "PREFERRED", "NONE"]);

/** Bloqueo editorial manual */
export interface VlogClipLock {
  mediaId: string;
  lockType: ClipLockType;
  targetSegmentId?: string;
  reason?: string;
}

export const VlogClipLockSchema = z.object({
  mediaId: z.string().min(1),
  lockType: ClipLockTypeSchema,
  targetSegmentId: z.string().optional(),
  reason: z.string().optional(),
});

/** Configuración global de producción para un proyecto Vlog */
export interface VlogProjectConfig {
  sourceLocale: SupportedLocale;
  targetLocales: SupportedLocale[];
  aspectRatio: VlogAspectRatio;
  stylePreset: string; // ej. "time_editorial_poster", "cinematic_travel"
  offlineMode: boolean; // default: true
  enableTTS: boolean; // default: true
  enableSubtitles: boolean; // default: true
  enableTravelOverlays: boolean; // default: true
  enableBrollMatching: boolean; // default: true
  enableJumpCuts: boolean; // default: true
  silenceThresholdSeconds: number; // default: 0.25 s
  microCrossfadeMilliseconds: number; // default: 10 ms
  punchInScale: number; // default: 1.15
  automaticStretchMin: number; // default: 0.95
  automaticStretchMax: number; // default: 1.05
  seed: number; // Semilla determinista para rotaciones Polaroid y variaciones
}

export const VlogProjectConfigSchema = z.object({
  sourceLocale: SupportedLocaleSchema,
  targetLocales: z.array(SupportedLocaleSchema).min(1),
  aspectRatio: z.enum(["16:9", "9:16", "1:1", "4:5", "21:9"]).default("9:16"),
  stylePreset: z.string().default("time_editorial_poster"),
  offlineMode: z.boolean().default(true),
  enableTTS: z.boolean().default(true),
  enableSubtitles: z.boolean().default(true),
  enableTravelOverlays: z.boolean().default(true),
  enableBrollMatching: z.boolean().default(true),
  enableJumpCuts: z.boolean().default(true),
  silenceThresholdSeconds: z.number().positive().default(0.25),
  microCrossfadeMilliseconds: z.number().positive().default(10),
  punchInScale: z.number().min(1.0).max(1.30).default(1.15),
  automaticStretchMin: z.number().min(0.85).max(1.0).default(0.95),
  automaticStretchMax: z.number().min(1.0).max(1.15).default(1.05),
  seed: z.number().int().default(42),
});

/** Activo de medio enlazado al proyecto */
export interface VlogMediaAsset {
  id: string;
  sourceFilePath: string;
  filename: string;
  mediaType: "VIDEO" | "AUDIO" | "IMAGE";
  durationSeconds: number;
  checksumSha256: string;
  assignedRole: "A_ROLL" | "B_ROLL" | "MUSIC" | "SFX" | "UNKNOWN";
  lock: VlogClipLock;
}

export const VlogMediaAssetSchema = z.object({
  id: z.string().min(1),
  sourceFilePath: z.string().min(1),
  filename: z.string().min(1),
  mediaType: z.enum(["VIDEO", "AUDIO", "IMAGE"]),
  durationSeconds: z.number().min(0),
  checksumSha256: z.string().min(64).max(64),
  assignedRole: z.enum(["A_ROLL", "B_ROLL", "MUSIC", "SFX", "UNKNOWN"]),
  lock: VlogClipLockSchema,
});

/** Segmento narrativo individual de la historia */
export interface VlogSegment {
  id: string;
  sceneId: string;
  startSeconds: number;
  endSeconds: number;
  durationSeconds: number;
  beat: VlogNarrativeBeat;
  speechText: string;
  topic?: string;
  primaryMediaId?: string;
  bRollMediaId?: string;
  hasPunchIn: boolean;
}

export const VlogSegmentSchema = z.object({
  id: z.string().min(1),
  sceneId: z.string().min(1),
  startSeconds: z.number().min(0),
  endSeconds: z.number().min(0),
  durationSeconds: z.number().min(0),
  beat: VlogNarrativeBeatSchema,
  speechText: z.string(),
  topic: z.string().optional(),
  primaryMediaId: z.string().optional(),
  bRollMediaId: z.string().optional(),
  hasPunchIn: z.boolean().default(false),
});

/** Escena temática del Vlog que agrupa segmentos */
export interface VlogScene {
  id: string;
  title: string;
  order: number;
  durationSeconds: number;
  locationName?: string;
  segments: VlogSegment[];
}

export const VlogSceneSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1),
  order: z.number().int().min(0),
  durationSeconds: z.number().min(0),
  locationName: z.string().optional(),
  segments: z.array(VlogSegmentSchema),
});

/** Evento o decisión de edición atómica en la timeline */
export interface VlogEditDecision {
  id: string;
  timeSeconds: number;
  type: "CUT" | "TRANSITION" | "PUNCH_IN" | "OVERLAY_IN" | "SFX_TRIGGER";
  sourceAssetId?: string;
  parameters: Record<string, unknown>;
}

export const VlogEditDecisionSchema = z.object({
  id: z.string().min(1),
  timeSeconds: z.number().min(0),
  type: z.enum(["CUT", "TRANSITION", "PUNCH_IN", "OVERLAY_IN", "SFX_TRIGGER"]),
  sourceAssetId: z.string().optional(),
  parameters: z.record(z.unknown()),
});

/** Línea temporal unificada para un idioma específico */
export interface VlogTimeline {
  id: string;
  locale: SupportedLocale;
  totalDurationSeconds: number;
  scenes: VlogScene[];
  editDecisions: VlogEditDecision[];
  checksumSha256: string;
}

export const VlogTimelineSchema = z.object({
  id: z.string().min(1),
  locale: SupportedLocaleSchema,
  totalDurationSeconds: z.number().min(0),
  scenes: z.array(VlogSceneSchema),
  editDecisions: z.array(VlogEditDecisionSchema),
  checksumSha256: z.string().min(64).max(64),
});

/** Proyecto Vlog Maestro — Fuente Única de Verdad (SSOT) */
export interface VlogProject {
  schemaVersion: "1.0.0";
  id: string;
  title: string;
  createdAtTimestamp: number;
  updatedAtTimestamp: number;
  config: VlogProjectConfig;
  mediaAssets: VlogMediaAsset[];
  scenes: VlogScene[];
  sourceTimeline: VlogTimeline;
  localizedTimelines: Partial<Record<SupportedLocale, VlogTimeline>>;
}

export const VlogProjectSchema = z.object({
  schemaVersion: z.literal("1.0.0"),
  id: z.string().min(1),
  title: z.string().min(1),
  createdAtTimestamp: z.number().positive(),
  updatedAtTimestamp: z.number().positive(),
  config: VlogProjectConfigSchema,
  mediaAssets: z.array(VlogMediaAssetSchema),
  scenes: z.array(VlogSceneSchema),
  sourceTimeline: VlogTimelineSchema,
  localizedTimelines: z.record(VlogTimelineSchema).optional(),
});
