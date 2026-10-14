import { z } from 'zod';

export const Vector3DSchema = z.object({
  x: z.number(),
  y: z.number(),
  z: z.number(),
});
export type Vector3D = z.infer<typeof Vector3DSchema>;

export const Rotator3DSchema = z.object({
  pitch: z.number(),
  yaw: z.number(),
  roll: z.number(),
});
export type Rotator3D = z.infer<typeof Rotator3DSchema>;

export const CameraKeyframeSchema = z.object({
  time: z.number().min(0),
  x: z.number(),
  y: z.number(),
  z: z.number(),
  pitch: z.number(),
  yaw: z.number(),
  roll: z.number().default(0),
  fov: z.number().min(10).max(120).default(45),
});
export type CameraKeyframe = z.infer<typeof CameraKeyframeSchema>;

export const AudioAnalysisSchema = z.object({
  bpm: z.number().min(0),
  duration_seconds: z.number().min(0),
  beat_timestamps: z.array(z.number()),
  onset_envelope: z.array(z.number()).default([]),
  stems: z.record(z.string()).nullable().optional(),
  time_signature: z.string().default('4/4'),
  danceability: z.number().min(0).max(1).default(0.5),
});
export type AudioAnalysis = z.infer<typeof AudioAnalysisSchema>;

export const PlanStepSchema = z.object({
  step_id: z.string().min(1),
  index: z.number().min(0),
  tool_name: z.string().min(1),
  title: z.string().nullable().optional(),
  description: z.string(),
  parameters: z.record(z.union([z.string(), z.number(), z.boolean(), z.array(z.string())])),
  risk_level: z.enum(['low', 'medium', 'high', 'critical']),
  requires_confirmation: z.boolean(),
  status: z.enum(['proposed', 'approved', 'rejected', 'in_progress', 'completed', 'failed']),
  output_preview: z.string().nullable().optional(),
  error_message: z.string().nullable().optional(),
});
export type PlanStep = z.infer<typeof PlanStepSchema>;

export const ProductionPlanSchema = z.object({
  plan_id: z.string().min(1),
  title: z.string(),
  description: z.string(),
  steps: z.array(PlanStepSchema),
  status: z.enum(['proposed', 'approved', 'rejected', 'in_progress', 'completed', 'failed']),
  created_at: z.string(),
  updated_at: z.string(),
  total_estimated_duration_seconds: z.number().min(0),
});
export type ProductionPlan = z.infer<typeof ProductionPlanSchema>;

export const TelemetryEventSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('progress'),
    stage: z.string(),
    percentage: z.number().min(0).max(100),
    message: z.string(),
    plan_id: z.string().nullable().optional(),
    step_id: z.string().nullable().optional(),
    tool_name: z.string().nullable().optional(),
    timestamp: z.string(),
  }),
  z.object({
    type: z.literal('plan_proposal'),
    plan_id: z.string(),
    steps: z.array(PlanStepSchema),
    status: z.enum(['proposed', 'approved', 'rejected', 'in_progress', 'completed', 'failed']),
    timestamp: z.string(),
  }),
  z.object({
    type: z.literal('asset_ready'),
    asset_id: z.string(),
    asset_type: z.string(),
    file_path: z.string(),
    metadata: z.record(z.string()).nullable().optional(),
    timestamp: z.string(),
  }),
  z.object({
    type: z.literal('log'),
    level: z.enum(['debug', 'info', 'warning', 'error', 'critical']),
    message: z.string(),
    source: z.string().nullable().optional(),
    timestamp: z.string(),
  }),
]);
export type TelemetryEvent = z.infer<typeof TelemetryEventSchema>;

export const LightingPresetSchema = z.enum([
  'studio_3point',
  'cyberpunk_neon',
  'dramatic',
  'outdoor_sunlight',
  'night_moonlight',
]);
export type LightingPreset = z.infer<typeof LightingPresetSchema>;

export const CameraPresetSchema = z.enum([
  'smooth_orbit',
  'dramatic_orbit',
  'aerial_pan',
  'front_close',
  'spiral_ascent',
]);
export type CameraPreset = z.infer<typeof CameraPresetSchema>;

export const PixelStreamingStatusSchema = z.enum([
  'disconnected',
  'connecting',
  'connected',
  'error',
]);
export type PixelStreamingStatus = z.infer<typeof PixelStreamingStatusSchema>;
