import { z } from "zod";

/**
 * REQ-021: Canonical track classifications in the Editorial IR.
 */
export const EditorialTrackTypeSchema = z.enum([
  "VIDEO_PRIMARY",   // Main narrative / A-Roll / Host / Interviewee
  "VIDEO_BROLL",     // Cutaways / B-Roll / Illustrative archive
  "VIDEO_GRAPHICS",  // Overlays, lower thirds, titles, UI graphics
  "AUDIO_DIALOGUE",  // Voiceover / Interview / Dialogue tracks
  "AUDIO_MUSIC",     // Background score / Soundtrack bed
  "AUDIO_SFX",       // Foley, UI sounds, shutter, whooshes
  "AUDIO_AMBIENCE",  // Room tone / Environmental beds
  "SUBTITLE",        // Timed text / Karaoke / Closed captions
]);

export type EditorialTrackType = z.infer<typeof EditorialTrackTypeSchema>;

/**
 * Canonical time range representation in seconds.
 */
export const EditorialTimeRangeSchema = z.object({
  startSeconds: z.number().min(0.0),
  durationSeconds: z.number().min(0.0),
});

export type EditorialTimeRange = z.infer<typeof EditorialTimeRangeSchema>;

/**
 * REQ-022: Individual media clip placed in the timeline.
 */
export const EditorialClipSchema = z.object({
  id: z.string().min(1),
  assetId: z.string().min(1),
  label: z.string().default("Clip"),
  sourceRange: EditorialTimeRangeSchema,
  timelineRange: EditorialTimeRangeSchema,
  speed: z.number().positive().default(1.0),
  volumeDb: z.number().min(-90).max(12).default(0.0),
  pan: z.number().min(-1.0).max(1.0).default(0.0),
  scale: z.number().positive().default(1.0),
  positionOffset: z
    .object({
      x: z.number(),
      y: z.number(),
    })
    .optional(),
  colorLabel: z.string().optional(),
});

export type EditorialClip = z.infer<typeof EditorialClipSchema>;
export type EditorialClipInput = z.input<typeof EditorialClipSchema>;

/**
 * REQ-021: Single track containing an ordered sequence of clips.
 */
export const EditorialTrackSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  type: EditorialTrackTypeSchema,
  index: z.number().int().min(0),
  isMuted: z.boolean().default(false),
  isLocked: z.boolean().default(false),
  clips: z.array(EditorialClipSchema).default([]),
});

export type EditorialTrack = z.infer<typeof EditorialTrackSchema>;

/**
 * Permissible editorial transition types in IR.
 */
export const EditorialTransitionTypeSchema = z.enum([
  "CROSS_DISSOLVE",
  "J_CUT",
  "L_CUT",
  "DIP_TO_BLACK",
  "WIPE",
  "HARD_CUT",
]);

export type EditorialTransitionType = z.infer<typeof EditorialTransitionTypeSchema>;

/**
 * Transition linking two clips.
 */
export const EditorialTransitionSchema = z.object({
  id: z.string().min(1),
  type: EditorialTransitionTypeSchema,
  fromClipId: z.string().min(1),
  toClipId: z.string().min(1),
  timestampSeconds: z.number().min(0),
  durationSeconds: z.number().min(0),
});

export type EditorialTransition = z.infer<typeof EditorialTransitionSchema>;

/**
 * Timeline marker / chapter cue.
 */
export const EditorialMarkerSchema = z.object({
  id: z.string().min(1),
  timestampSeconds: z.number().min(0),
  name: z.string().min(1),
  color: z.string().default("#00FF00"),
  comment: z.string().optional(),
});

export type EditorialMarker = z.infer<typeof EditorialMarkerSchema>;

/**
 * Overall technical metadata for the timeline composition.
 */
export const EditorialMetadataSchema = z.object({
  title: z.string().min(1),
  profile: z.string().min(1),
  frameRate: z.number().positive().default(30),
  width: z.number().int().positive().default(1920),
  height: z.number().int().positive().default(1080),
  sampleRate: z.number().int().positive().default(44100),
  targetDialogueLufs: z.number().min(-30).max(-10).default(-16),
});

export type EditorialMetadata = z.infer<typeof EditorialMetadataSchema>;

/**
 * REQ-021 & REQ-022: Master Editorial Intermediate Representation (IR) Schema.
 * The absolute Single Source of Truth for the entire postproduction workflow.
 */
export const EditorialIRSchema = z.object({
  schemaVersion: z.literal("4.0.0"),
  projectId: z.string().min(1),
  metadata: EditorialMetadataSchema,
  tracks: z.array(EditorialTrackSchema).default([]),
  transitions: z.array(EditorialTransitionSchema).default([]),
  markers: z.array(EditorialMarkerSchema).default([]),
  checksum: z.string().length(64), // SHA-256 seal
  createdAt: z.string().datetime(),
});

export type EditorialIR = z.infer<typeof EditorialIRSchema>;
