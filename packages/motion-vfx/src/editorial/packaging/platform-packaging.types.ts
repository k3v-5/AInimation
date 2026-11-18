import { z } from "zod";
import { AspectRatioTargetSchema } from "../compiler/multi-version.types.js";

/**
 * REQ-029 & REQ-030: Canonical delivery platform standards.
 */
export const PlatformStandardSchema = z.enum([
  "YOUTUBE_LONG",        // 16:9 horizontal, -16 LUFS, 90% action safe
  "TIKTOK_REELS_SHORT",  // 9:16 vertical, -14 LUFS, strict UI exclusion safe zone
  "BROADCAST_EBU_R128",  // 16:9, -23 LUFS (±0.5 LUFS), -1.0 dBTP
  "CINEMA_DCI",          // 21:9 or 16:9, -24 LUFS, 24fps
  "LINKEDIN_CORPORATE",  // 1:1 square or 16:9, -16 LUFS, burned-in subtitles
]);

export type PlatformStandard = z.infer<typeof PlatformStandardSchema>;

/**
 * Safe zone configuration for platform packaging.
 */
export const PlatformSafeZoneSchema = z.object({
  topMarginPercent: z.number().min(0).max(50),
  bottomMarginPercent: z.number().min(0).max(50),
  leftMarginPercent: z.number().min(0).max(50),
  rightMarginPercent: z.number().min(0).max(50),
  socialUIExclusion: z.boolean(),
});

export type PlatformSafeZone = z.infer<typeof PlatformSafeZoneSchema>;

/**
 * Master Delivery Packaging Manifest.
 */
export const PlatformDeliveryManifestSchema = z.object({
  deliveryId: z.string().min(1),
  projectId: z.string().min(1),
  platform: PlatformStandardSchema,
  aspectRatio: AspectRatioTargetSchema,
  width: z.number().int().positive(),
  height: z.number().int().positive(),
  frameRate: z.number().positive(),
  targetDialogueLufs: z.number().min(-30).max(-10),
  truePeakMaxDb: z.number().max(0),
  safeZone: PlatformSafeZoneSchema,
  readyForDelivery: z.boolean(),
  checksum: z.string().length(64),
});

export type PlatformDeliveryManifest = z.infer<typeof PlatformDeliveryManifestSchema>;
