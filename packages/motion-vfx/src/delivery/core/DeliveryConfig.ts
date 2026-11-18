import { z } from "zod";
import { AspectRatioSchema } from "./AspectRatio.js";
import { TargetPlatformSchema } from "./TargetPlatform.js";

export const DeliveryConfigSchema = z.object({
  targetAspectRatios: z.array(AspectRatioSchema).min(1).default(["9:16", "16:9", "1:1"]),
  targetPlatforms: z.array(TargetPlatformSchema).min(1).default(["tiktok", "youtube_horizontal", "instagram_feed"]),
  reframeStrategy: z.enum(["fit", "fill", "smart_recenter", "letterbox"]).default("smart_recenter"),
  normalizeAudio: z.boolean().default(true),
  extractThumbnails: z.boolean().default(true),
  thumbnailCount: z.number().int().min(1).max(10).default(3),
  outputDirectory: z.string().default("./dist/social_delivery"),
});

export type DeliveryConfig = z.infer<typeof DeliveryConfigSchema>;

export function createDeliveryConfig(overrides?: Partial<DeliveryConfig>): DeliveryConfig {
  return DeliveryConfigSchema.parse(overrides ?? {});
}
