import { z } from "zod";

/**
 * REQ-012: Person / Speaker entity.
 */
export const SpeakerRoleSchema = z.enum([
  "INTERVIEWER",
  "GUEST",
  "NARRATOR",
  "EXPERT",
  "WITNESS",
  "SUBJECT",
  "SECONDARY",
]);

export type SpeakerRole = z.infer<typeof SpeakerRoleSchema>;

export const PersonEntitySchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  role: SpeakerRoleSchema,
  speakerIdentifier: z.string().optional(),
  title: z.string().optional(), // Lower third title
  affiliation: z.string().optional(),
});

export type PersonEntity = z.infer<typeof PersonEntitySchema>;

/**
 * REQ-074: Location entity.
 */
export const LocationEntitySchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  country: z.string().optional(),
  city: z.string().optional(),
  coordinates: z
    .object({
      latitude: z.number().min(-90).max(90),
      longitude: z.number().min(-180).max(180),
    })
    .optional(),
  description: z.string().optional(),
});

export type LocationEntity = z.infer<typeof LocationEntitySchema>;

/**
 * REQ-009 & REQ-010: Claim and Fact Checking entity.
 */
export const ClaimStatusSchema = z.enum([
  "VERIFIED",
  "UNVERIFIED",
  "CONTRADICTED",
  "MISSING_SOURCE",
  "EDITOR_REVIEW",
]);

export type ClaimStatus = z.infer<typeof ClaimStatusSchema>;

export const ClaimEntitySchema = z.object({
  id: z.string().min(1),
  text: z.string().min(1),
  speakerId: z.string().optional(),
  sourceCitation: z.string().optional(),
  evidenceAssetIds: z.array(z.string()).default([]),
  confidence: z.number().min(0.0).max(1.0).default(1.0),
  status: ClaimStatusSchema.default("UNVERIFIED"),
  requiresOnScreenCitation: z.boolean().default(false),
});

export type ClaimEntity = z.infer<typeof ClaimEntitySchema>;
export type ClaimEntityInput = z.input<typeof ClaimEntitySchema>;

/**
 * REQ-042: Scene entity.
 */
export const SceneEntitySchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  locationId: z.string().optional(),
  participantIds: z.array(z.string()).default([]),
  estimatedStartSeconds: z.number().min(0).optional(),
  estimatedDurationSeconds: z.number().min(0).optional(),
  narrativeImportance: z.number().min(0.0).max(1.0).default(0.5),
  description: z.string().optional(),
});

export type SceneEntity = z.infer<typeof SceneEntitySchema>;
export type SceneEntityInput = z.input<typeof SceneEntitySchema>;

/**
 * REQ-004: Shot entity within knowledge graph.
 */
export const ShotClassificationScaleSchema = z.enum([
  "EXTREME_WIDE",
  "WIDE",
  "MEDIUM_WIDE",
  "MEDIUM",
  "MEDIUM_CLOSE",
  "CLOSE_UP",
  "EXTREME_CLOSE",
  "DETAIL",
  "OVER_SHOULDER",
  "POV",
  "ESTABLISHING",
  "CUTAWAY",
  "ARCHIVAL",
  "DRONE",
  "TALKING_HEAD",
]);

export type ShotClassificationScale = z.infer<typeof ShotClassificationScaleSchema>;

export const ShotEntitySchema = z.object({
  id: z.string().min(1),
  assetId: z.string().min(1),
  sceneId: z.string().optional(),
  scale: ShotClassificationScaleSchema.default("MEDIUM"),
  startSeconds: z.number().min(0),
  endSeconds: z.number().min(0),
  durationSeconds: z.number().min(0),
  technicalQuality: z.number().min(0.0).max(1.0).default(0.9),
  subjectId: z.string().optional(),
  description: z.string().optional(),
});

export type ShotEntity = z.infer<typeof ShotEntitySchema>;
export type ShotEntityInput = z.input<typeof ShotEntitySchema>;

/**
 * REQ-041: Project Knowledge Graph Schema.
 */
export const ProjectKnowledgeGraphSchema = z.object({
  projectId: z.string().min(1),
  people: z.array(PersonEntitySchema).default([]),
  locations: z.array(LocationEntitySchema).default([]),
  claims: z.array(ClaimEntitySchema).default([]),
  scenes: z.array(SceneEntitySchema).default([]),
  shots: z.array(ShotEntitySchema).default([]),
  checksum: z.string().length(64), // SHA-256
});

export type ProjectKnowledgeGraph = z.infer<typeof ProjectKnowledgeGraphSchema>;
