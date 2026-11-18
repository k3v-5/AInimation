import { z } from "zod";

/**
 * REQ-016: Ken Burns 2D Pan and Zoom Parameters.
 * Coordinates are normalized: 0.0 (left/top) to 1.0 (right/bottom), default center is (0.5, 0.5).
 */
export const KenBurnsParamsSchema = z.object({
  scaleStart: z.number().min(0.5).max(3.0).default(1.0),
  scaleEnd: z.number().min(0.5).max(3.0).default(1.15),
  panStartX: z.number().min(0.0).max(1.0).default(0.5),
  panStartY: z.number().min(0.0).max(1.0).default(0.5),
  panEndX: z.number().min(0.0).max(1.0).default(0.5),
  panEndY: z.number().min(0.0).max(1.0).default(0.5),
  easing: z.enum(["LINEAR", "EASE_IN_OUT", "EASE_OUT"]).default("EASE_IN_OUT"),
});

export type KenBurnsParams = z.infer<typeof KenBurnsParamsSchema>;

/**
 * REQ-087: Archival License and Copyright Status.
 */
export const LicenseComplianceStatusSchema = z.enum([
  "PUBLIC_DOMAIN",
  "LICENSED_VALID",
  "EDITORIAL_USE_ONLY",
  "EXPIRED",
  "RESTRICTED",
]);

export type LicenseComplianceStatus = z.infer<typeof LicenseComplianceStatusSchema>;

/**
 * REQ-016: Archival Media Asset with Historical Metadata.
 */
export const ArchivalAssetSchema = z.object({
  id: z.string().min(1),
  sourcePath: z.string().min(1),
  title: z.string().min(1),
  year: z.number().int().min(1800).max(2100).optional(),
  dateExact: z.string().optional(),
  sourceArchive: z.string().min(1), // e.g. "National Archives", "BBC News", "AP"
  creator: z.string().optional(),
  licenseStatus: LicenseComplianceStatusSchema.default("EDITORIAL_USE_ONLY"),
  licenseExpiryDate: z.string().optional(),
  licenseNotes: z.string().optional(),
  isStillPhoto: z.boolean().default(false),
  aspectRatio: z.string().default("4:3"), // Historical archival is frequently 4:3
});

export type ArchivalAsset = z.infer<typeof ArchivalAssetSchema>;

/**
 * REQ-016: Archival Treatment on Timeline.
 */
export const ArchivalTreatmentSchema = z.object({
  clipId: z.string().min(1),
  assetId: z.string().min(1),
  kenBurns: KenBurnsParamsSchema.optional(),
  dateStampText: z.string().optional(), // e.g., "FILE FOOTAGE // OCT 1983"
  sourceAttributionText: z.string().min(1), // e.g., "Courtesy of BBC Archive"
  grainOverlay: z.boolean().default(false),
  monochromeFilter: z.boolean().default(false),
  timelineStartSeconds: z.number().nonnegative(),
  timelineEndSeconds: z.number().nonnegative(),
});

export type ArchivalTreatment = z.infer<typeof ArchivalTreatmentSchema>;

/**
 * Master Archival Media Report & Plan.
 */
export const ArchivalMediaPlanSchema = z.object({
  projectId: z.string().min(1),
  treatments: z.array(ArchivalTreatmentSchema),
  licenseCompliant: z.boolean(),
  issues: z.array(z.string()).default([]),
  checksumSha256: z.string().length(64),
});

export type ArchivalMediaPlan = z.infer<typeof ArchivalMediaPlanSchema>;
