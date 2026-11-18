import { z } from "zod";
import { AspectRatio } from "./AspectRatio.js";

export const TargetPlatformSchema = z.enum([
  "tiktok",
  "instagram_reels",
  "youtube_shorts",
  "youtube_horizontal",
  "instagram_feed",
  "linkedin",
  "broadcast",
]);

export type TargetPlatform = z.infer<typeof TargetPlatformSchema>;

export interface SocialPlatformProfile {
  platform: TargetPlatform;
  defaultAspectRatio: AspectRatio;
  targetLufs: number;
  maxTruePeakDb: number;
  safeZoneMargins: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  };
}

export const SOCIAL_PLATFORM_PROFILES: Record<TargetPlatform, SocialPlatformProfile> = {
  tiktok: {
    platform: "tiktok",
    defaultAspectRatio: "9:16",
    targetLufs: -16.0,
    maxTruePeakDb: -1.0,
    safeZoneMargins: { top: 120, bottom: 280, left: 60, right: 140 },
  },
  instagram_reels: {
    platform: "instagram_reels",
    defaultAspectRatio: "9:16",
    targetLufs: -16.0,
    maxTruePeakDb: -1.0,
    safeZoneMargins: { top: 100, bottom: 260, left: 60, right: 120 },
  },
  youtube_shorts: {
    platform: "youtube_shorts",
    defaultAspectRatio: "9:16",
    targetLufs: -14.0,
    maxTruePeakDb: -1.0,
    safeZoneMargins: { top: 100, bottom: 220, left: 60, right: 100 },
  },
  youtube_horizontal: {
    platform: "youtube_horizontal",
    defaultAspectRatio: "16:9",
    targetLufs: -14.0,
    maxTruePeakDb: -1.0,
    safeZoneMargins: { top: 60, bottom: 60, left: 90, right: 90 },
  },
  instagram_feed: {
    platform: "instagram_feed",
    defaultAspectRatio: "4:5",
    targetLufs: -16.0,
    maxTruePeakDb: -1.0,
    safeZoneMargins: { top: 60, bottom: 60, left: 60, right: 60 },
  },
  linkedin: {
    platform: "linkedin",
    defaultAspectRatio: "1:1",
    targetLufs: -14.0,
    maxTruePeakDb: -1.0,
    safeZoneMargins: { top: 60, bottom: 60, left: 60, right: 60 },
  },
  broadcast: {
    platform: "broadcast",
    defaultAspectRatio: "16:9",
    targetLufs: -23.0,
    maxTruePeakDb: -1.0,
    safeZoneMargins: { top: 108, bottom: 108, left: 192, right: 192 }, // 10% SMPTE
  },
};
