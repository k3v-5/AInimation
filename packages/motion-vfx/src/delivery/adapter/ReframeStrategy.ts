import { z } from "zod";

export const ReframeStrategySchema = z.enum([
  "fit",
  "fill",
  "smart_recenter",
  "letterbox",
]);

export type ReframeStrategy = z.infer<typeof ReframeStrategySchema>;
