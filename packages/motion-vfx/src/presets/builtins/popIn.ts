import { parallel } from "../../animation/helpers.js";
import { overshoot } from "../../animation/motion/OvershootMotion.js";
import { fadeIn } from "../../animation/primitives/fade.js";
import { scaleIn } from "../../animation/primitives/scale.js";
import { PresetContext, PresetDefinition } from "../schema/types.js";

/**
 * Preset de referencia PopIn: Entrada simultánea de Fade In + Scale In con sobrepaso (Overshoot) orgánico.
 */
export const popInPreset: PresetDefinition = {
  id: "popIn",
  name: "Pop In",
  category: "entrance",
  version: 1,
  description: "Scales an element into view with a smooth organic overshoot and simultaneous fade.",
  tags: ["smooth", "modern", "pop", "scale", "entrance", "tiktok", "youtube"],
  compatibleWith: ["text", "image", "shape", "video", "group"],
  parameters: [
    {
      name: "duration",
      type: "duration",
      default: 0.5,
      min: 0.05,
      max: 10.0,
      description: "Total duration of the pop-in animation in seconds.",
    },
    {
      name: "intensity",
      type: "number",
      default: 0.7,
      min: 0.0,
      max: 2.0,
      description: "Strength of the initial scale reduction and subsequent overshoot peak.",
    },
  ],
  build(context: PresetContext) {
    const duration = context.parameters.duration as number;
    const intensity = context.parameters.intensity as number;

    const fromScale = Math.max(0.1, 1.0 - 0.3 * intensity);
    const overshootAmount = 1.2 * intensity;

    return parallel(
      fadeIn(context.target as any, { duration }),
      scaleIn(context.target as any, {
        from: fromScale,
        duration,
        motion: overshoot({ amount: overshootAmount }),
      })
    );
  },
};
