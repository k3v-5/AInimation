import { GaussianBlur } from "../blur/GaussianBlur.js";
import { Brightness } from "../color/Brightness.js";
import { Contrast } from "../color/Contrast.js";
import { DropShadow } from "../glow/DropShadow.js";
import { Glow } from "../glow/Glow.js";
import { Outline } from "../stylize/Outline.js";
import { EffectRegistry } from "../core/EffectRegistry.js";

/**
 * Registra todos los efectos nativos built-in en el EffectRegistry.
 */
export function registerBuiltinEffects(): void {
  if (!EffectRegistry.has("blur")) {
    EffectRegistry.register({
      type: "blur",
      name: "Gaussian Blur",
      category: "blur",
      description: "Applies smooth isotropic Gaussian blur to the visual representation.",
      parameters: [
        { name: "amount", type: "number", default: 0, min: 0, max: 500, description: "Blur radius in pixels." },
        { name: "quality", type: "enum", default: "medium", values: ["low", "medium", "high"], description: "Sampling quality." },
      ],
      factory: (opts) => new GaussianBlur(opts),
    });
  }

  if (!EffectRegistry.has("brightness")) {
    EffectRegistry.register({
      type: "brightness",
      name: "Brightness",
      category: "color",
      description: "Adjusts the brightness multiplier of the element.",
      parameters: [
        { name: "amount", type: "number", default: 1.0, min: 0.0, max: 5.0, description: "Brightness factor (1.0 = normal)." },
      ],
      factory: (opts) => new Brightness(opts),
    });
  }

  if (!EffectRegistry.has("contrast")) {
    EffectRegistry.register({
      type: "contrast",
      name: "Contrast",
      category: "color",
      description: "Adjusts the contrast level of the element.",
      parameters: [
        { name: "amount", type: "number", default: 1.0, min: 0.0, max: 5.0, description: "Contrast factor (1.0 = normal)." },
      ],
      factory: (opts) => new Contrast(opts),
    });
  }

  if (!EffectRegistry.has("glow")) {
    EffectRegistry.register({
      type: "glow",
      name: "Glow",
      category: "light",
      description: "Creates an illuminated halo surrounding the alpha edges.",
      parameters: [
        { name: "radius", type: "number", default: 20, min: 0, max: 200, description: "Diffusion radius." },
        { name: "intensity", type: "number", default: 1.0, min: 0, max: 10.0, description: "Glow intensity multiplier." },
        { name: "threshold", type: "number", default: 0.5, min: 0, max: 1.0, description: "Luma threshold." },
        { name: "color", type: "color", default: { r: 1, g: 1, b: 1, a: 1 }, description: "Glow color." },
      ],
      factory: (opts) => new Glow(opts),
    });
  }

  if (!EffectRegistry.has("dropShadow")) {
    EffectRegistry.register({
      type: "dropShadow",
      name: "Drop Shadow",
      category: "shadow",
      description: "Projects a soft drop shadow offset from the element.",
      parameters: [
        { name: "offsetX", type: "number", default: 5, description: "Horizontal pixel offset." },
        { name: "offsetY", type: "number", default: 5, description: "Vertical pixel offset." },
        { name: "blur", type: "number", default: 10, min: 0, description: "Shadow blur radius." },
        { name: "spread", type: "number", default: 0, description: "Shadow expansion." },
        { name: "opacity", type: "number", default: 0.5, min: 0, max: 1.0, description: "Shadow opacity." },
        { name: "color", type: "color", default: { r: 0, g: 0, b: 0, a: 1 }, description: "Shadow color." },
      ],
      factory: (opts) => new DropShadow(opts),
    });
  }

  if (!EffectRegistry.has("outline")) {
    EffectRegistry.register({
      type: "outline",
      name: "Outline",
      category: "stylization",
      description: "Renders a stroke outline around text or shape boundaries.",
      parameters: [
        { name: "width", type: "number", default: 2, min: 0, max: 100, description: "Stroke width in pixels." },
        { name: "opacity", type: "number", default: 1.0, min: 0, max: 1.0, description: "Outline opacity." },
        { name: "color", type: "color", default: { r: 0, g: 0, b: 0, a: 1 }, description: "Outline color." },
      ],
      factory: (opts) => new Outline(opts),
    });
  }
}

// Auto-registro en tiempo de carga
registerBuiltinEffects();

export * from "../blur/GaussianBlur.js";
export * from "../color/Brightness.js";
export * from "../color/Contrast.js";
export * from "../glow/DropShadow.js";
export * from "../glow/Glow.js";
export * from "../stylize/Outline.js";
