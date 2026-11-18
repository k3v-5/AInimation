import { z } from "zod";
import { ShotClassificationScaleSchema } from "../contracts/knowledge-graph.types.js";

/**
 * REQ-011: Camera role in a multi-camera production.
 */
export const CameraRoleSchema = z.enum([
  "WIDE",
  "SPEAKER_PRIMARY",
  "SPEAKER_SECONDARY",
  "DETAIL",
  "REACTION",
]);

export type CameraRole = z.infer<typeof CameraRoleSchema>;

/**
 * REQ-011 §6.3: Estados de Protección Emocional Inviolables
 */
export const EmotionalProtectionStateSchema = z.enum([
  "NONE",
  "CONFESSION",
  "BREAKDOWN",
  "CRYING",
  "HIGH_VULNERABILITY",
  "MAJOR_REVELATION",
]);

export type EmotionalProtectionState = z.infer<typeof EmotionalProtectionStateSchema>;

/**
 * REQ-012 §6.1: Abstracción de Hablante y Tracking
 */
export interface SpeakerIdentity {
  speakerId: string;
  name: string;
  role: "INTERVIEWER" | "INTERVIEWEE" | "HOST" | "GUEST" | "EXPERT" | "WITNESS";
}

export interface SpeakerPresence {
  timestampSeconds: number;
  isActive: boolean;
  confidence: number;
}

export interface SpeakerEnergy {
  timestampSeconds: number;
  energyLevel: number; // 0.0 a 1.0 (RMS normalizado)
  isPeak: boolean;
}

export interface SpeakerTrack {
  speakerId: string;
  identity: SpeakerIdentity;
  turns: Array<{
    startSeconds: number;
    endSeconds: number;
    emotionalState: EmotionalProtectionState;
    meanEnergy: number;
  }>;
}

/**
 * Configuración de ángulo de cámara con posición espacial y azimut de eje 180°
 */
export const CameraAngleDefinitionSchema = z.object({
  angleId: z.string().min(1),
  name: z.string().min(1),
  role: CameraRoleSchema,
  assignedSpeakerId: z.string().optional(),
  scale: ShotClassificationScaleSchema.default("MEDIUM"),
  cameraAzimuthDeg: z.number().min(0).max(360).default(0),
  spatialSide: z.enum(["LEFT_OF_AXIS", "RIGHT_OF_AXIS", "NEUTRAL_CENTER"]).default("NEUTRAL_CENTER").optional(),
});

export type CameraAngleDefinition = z.infer<typeof CameraAngleDefinitionSchema>;

/**
 * Decisión de corte multicámara explicable
 */
export const MultiCamSwitchDecisionSchema = z.object({
  id: z.string().min(1),
  timestampSeconds: z.number().min(0),
  activeAngleId: z.string().min(1),
  previousAngleId: z.string().optional(),
  reason: z.string().min(1),
  isEmotionalProtection: z.boolean().default(false),
  emotionalState: EmotionalProtectionStateSchema.default("NONE"),
  confidence: z.number().min(0.0).max(1.0).default(0.95),
  axisValidated: z.boolean().default(true),
});

export type MultiCamSwitchDecision = z.infer<typeof MultiCamSwitchDecisionSchema>;
