import { TargetPlatform, SOCIAL_PLATFORM_PROFILES, SocialPlatformProfile } from "../core/TargetPlatform.js";

export interface AudioComplianceReport {
  platform: TargetPlatform;
  targetLufs: number;
  initialLufs: number;
  gainAdjustmentDb: number;
  finalLufs: number;
  initialTruePeakDb: number;
  finalTruePeakDb: number;
  compliant: boolean;
}

export function getAudioProfileForPlatform(platform: TargetPlatform): SocialPlatformProfile {
  return SOCIAL_PLATFORM_PROFILES[platform];
}
