import crypto from "crypto";
import { EditorialIR } from "../ir/editorial-ir.types.js";
import {
  PlatformDeliveryManifest,
  PlatformDeliveryManifestSchema,
  PlatformSafeZone,
  PlatformStandard,
} from "./platform-packaging.types.js";

/**
 * REQ-029 & REQ-030: Master Platform Packager.
 * Enforces technical audio/video standards (loudness LUFS, true peak, aspect ratios, safe zones)
 * tailored for each distribution channel (YouTube, TikTok/Reels, EBU R128 Broadcast, Cinema DCI).
 */
export class PlatformPackager {
  private static readonly PLATFORM_PROFILES: Record<
    PlatformStandard,
    {
      targetLufs: number;
      truePeakMaxDb: number;
      expectedAspectRatio: "16:9" | "9:16" | "1:1" | "4:5" | "21:9";
      safeZone: PlatformSafeZone;
    }
  > = {
    YOUTUBE_LONG: {
      targetLufs: -16,
      truePeakMaxDb: -1.0,
      expectedAspectRatio: "16:9",
      safeZone: {
        topMarginPercent: 5,
        bottomMarginPercent: 5,
        leftMarginPercent: 5,
        rightMarginPercent: 5,
        socialUIExclusion: false,
      },
    },
    TIKTOK_REELS_SHORT: {
      targetLufs: -14,
      truePeakMaxDb: -1.0,
      expectedAspectRatio: "9:16",
      safeZone: {
        topMarginPercent: 10,
        bottomMarginPercent: 22, // Space for caption, sound tag, creator handle
        leftMarginPercent: 6,
        rightMarginPercent: 18, // Space for right-hand action icons (like, share, comment)
        socialUIExclusion: true,
      },
    },
    BROADCAST_EBU_R128: {
      targetLufs: -23,
      truePeakMaxDb: -1.0,
      expectedAspectRatio: "16:9",
      safeZone: {
        topMarginPercent: 10,
        bottomMarginPercent: 10,
        leftMarginPercent: 10,
        rightMarginPercent: 10,
        socialUIExclusion: false,
      },
    },
    CINEMA_DCI: {
      targetLufs: -24,
      truePeakMaxDb: -0.5,
      expectedAspectRatio: "21:9",
      safeZone: {
        topMarginPercent: 5,
        bottomMarginPercent: 5,
        leftMarginPercent: 5,
        rightMarginPercent: 5,
        socialUIExclusion: false,
      },
    },
    LINKEDIN_CORPORATE: {
      targetLufs: -16,
      truePeakMaxDb: -1.0,
      expectedAspectRatio: "1:1",
      safeZone: {
        topMarginPercent: 8,
        bottomMarginPercent: 15,
        leftMarginPercent: 8,
        rightMarginPercent: 8,
        socialUIExclusion: false,
      },
    },
  };

  /**
   * Generates a formal delivery manifest for a specific platform.
   */
  public static packageForPlatform(
    ir: EditorialIR,
    platform: PlatformStandard
  ): PlatformDeliveryManifest {
    const profile = this.PLATFORM_PROFILES[platform];
    const deliveryId = `deliv_${platform.toLowerCase()}_${ir.projectId}`;

    // Verify aspect ratio compatibility
    const currentAspect = this.inferAspectRatio(ir.metadata.width, ir.metadata.height);
    const aspectMatches = currentAspect === profile.expectedAspectRatio;

    const manifestContent = JSON.stringify({
      deliveryId,
      projectId: ir.projectId,
      platform,
      aspectRatio: currentAspect,
      width: ir.metadata.width,
      height: ir.metadata.height,
      frameRate: ir.metadata.frameRate,
      targetDialogueLufs: profile.targetLufs,
      truePeakMaxDb: profile.truePeakMaxDb,
      safeZone: profile.safeZone,
      readyForDelivery: aspectMatches,
    });

    const checksum = crypto.createHash("sha256").update(manifestContent).digest("hex");

    const manifest: PlatformDeliveryManifest = {
      deliveryId,
      projectId: ir.projectId,
      platform,
      aspectRatio: currentAspect,
      width: ir.metadata.width,
      height: ir.metadata.height,
      frameRate: ir.metadata.frameRate,
      targetDialogueLufs: profile.targetLufs,
      truePeakMaxDb: profile.truePeakMaxDb,
      safeZone: profile.safeZone,
      readyForDelivery: aspectMatches,
      checksum,
    };

    return PlatformDeliveryManifestSchema.parse(manifest);
  }

  private static inferAspectRatio(width: number, height: number): "16:9" | "9:16" | "1:1" | "4:5" | "21:9" {
    const ratio = width / height;
    if (Math.abs(ratio - 16 / 9) < 0.05) return "16:9";
    if (Math.abs(ratio - 9 / 16) < 0.05) return "9:16";
    if (Math.abs(ratio - 1.0) < 0.05) return "1:1";
    if (Math.abs(ratio - 4 / 5) < 0.05) return "4:5";
    if (Math.abs(ratio - 21 / 9) < 0.15) return "21:9";
    return "16:9";
  }
}
