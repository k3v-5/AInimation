import { z } from "zod";
import { UnsupportedAspectRatioError } from "./DeliveryErrors.js";

export const AspectRatioSchema = z.enum(["9:16", "16:9", "1:1", "4:5", "21:9"]);

export type AspectRatio = z.infer<typeof AspectRatioSchema>;

export interface AspectRatioDimension {
  width: number;
  height: number;
  ratio: AspectRatio;
  decimal: number;
}

export const ASPECT_RATIO_DIMENSIONS: Record<AspectRatio, AspectRatioDimension> = {
  "9:16": { width: 1080, height: 1920, ratio: "9:16", decimal: 9 / 16 },
  "16:9": { width: 1920, height: 1080, ratio: "16:9", decimal: 16 / 9 },
  "1:1": { width: 1080, height: 1080, ratio: "1:1", decimal: 1.0 },
  "4:5": { width: 1080, height: 1350, ratio: "4:5", decimal: 4 / 5 },
  "21:9": { width: 2560, height: 1080, ratio: "21:9", decimal: 21 / 9 },
};

export function parseAspectRatio(ratio: string): AspectRatioDimension {
  const parsed = AspectRatioSchema.safeParse(ratio);
  if (!parsed.success) {
    throw new UnsupportedAspectRatioError(ratio);
  }
  return ASPECT_RATIO_DIMENSIONS[parsed.data];
}
