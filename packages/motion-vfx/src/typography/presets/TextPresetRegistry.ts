import { ValidationError } from "../../errors/index.js";
import { TextPreset } from "../types/index.js";

/**
 * Registro y catálogo de presets tipográficos para Kinetic Motion Graphics (Fase 5F).
 */
export class TextPresetRegistry {
  private static presets = new Map<string, TextPreset>();

  public static register(preset: TextPreset): void {
    if (!preset || !preset.id) {
      throw new ValidationError("Text preset requires a valid 'id'.");
    }
    if (this.presets.has(preset.id)) {
      throw new ValidationError(`DUPLICATE_TEXT_PRESET: Preset '${preset.id}' already exists.`);
    }
    this.presets.set(preset.id, preset);
  }

  public static get(id: string): TextPreset {
    const p = this.presets.get(id);
    if (!p) {
      throw new ValidationError(`TEXT_PRESET_NOT_FOUND: Text preset '${id}' is not registered.`);
    }
    return p;
  }

  public static has(id: string): boolean {
    return this.presets.has(id);
  }

  public static list(): TextPreset[] {
    return Array.from(this.presets.values());
  }

  public static clear(): void {
    this.presets.clear();
  }
}

export const BuiltinTextPresets: TextPreset[] = [
  {
    id: "title-impact",
    name: "Title Impact",
    description: "Heavy impact typography with thick stroke and drop shadow.",
    style: {
      fontFamily: "Montserrat",
      fontSize: 84,
      fontWeight: 900,
      letterSpacing: 2,
      lineHeight: 1.1,
      alignment: "center",
    },
    paint: {
      fill: { r: 1, g: 1, b: 1 },
      strokes: [{ width: 8, color: { r: 0, g: 0, b: 0 } }],
      shadow: { offsetX: 0, offsetY: 6, blur: 12, color: { r: 0, g: 0, b: 0 }, opacity: 0.8 },
    },
    stagger: {
      duration: 0.5,
      mode: "forward",
    },
  },
  {
    id: "neon-glow",
    name: "Neon Glow",
    description: "Cyberpunk neon typography with vivid cyan stroke and shadow.",
    style: {
      fontFamily: "Inter",
      fontSize: 72,
      fontWeight: 700,
      letterSpacing: 4,
      lineHeight: 1.2,
      alignment: "center",
    },
    paint: {
      fill: { r: 0.9, g: 1, b: 1 },
      strokes: [{ width: 4, color: { r: 0, g: 0.9, b: 1 } }],
      shadow: { offsetX: 0, offsetY: 0, blur: 24, color: { r: 0, g: 0.8, b: 1 }, opacity: 1.0 },
    },
    stagger: {
      duration: 0.4,
      mode: "center",
    },
  },
  {
    id: "gradient-punch",
    name: "Gradient Punch",
    description: "Dynamic linear gradient yellow-to-orange headline.",
    style: {
      fontFamily: "Montserrat",
      fontSize: 90,
      fontWeight: 900,
      letterSpacing: 1,
      lineHeight: 1.05,
      alignment: "center",
    },
    paint: {
      fill: {
        type: "linear",
        angle: 90,
        stops: [
          { offset: 0.0, color: { r: 1, g: 0.9, b: 0 } },
          { offset: 1.0, color: { r: 1, g: 0.3, b: 0 } },
        ],
      },
      strokes: [{ width: 6, color: { r: 0, g: 0, b: 0 } }],
    },
    stagger: {
      duration: 0.35,
      mode: "random",
      seed: 12345,
    },
  },
];

for (const p of BuiltinTextPresets) {
  if (!TextPresetRegistry.has(p.id)) {
    TextPresetRegistry.register(p);
  }
}
