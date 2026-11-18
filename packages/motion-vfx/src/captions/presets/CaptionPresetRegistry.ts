import { ValidationError } from "../../errors/index.js";
import { CaptionLayoutMode, CaptionStyle, SemanticPosition, WordStyleOverride } from "../types/index.js";

export interface CaptionPreset {
  id: string;
  name: string;
  description: string;
  style: CaptionStyle;
  layoutMode: CaptionLayoutMode;
  position: SemanticPosition;
  activeWordOverride?: WordStyleOverride;
}

/**
 * Registro y catálogo de presets de subtítulos dinámicos (Fase 5E).
 */
export class CaptionPresetRegistry {
  private static presets = new Map<string, CaptionPreset>();

  public static register(preset: CaptionPreset): void {
    if (!preset || !preset.id) {
      throw new ValidationError("Caption preset requires a valid non-empty 'id'.");
    }
    if (this.presets.has(preset.id)) {
      throw new ValidationError(`DUPLICATE_CAPTION_PRESET: Preset '${preset.id}' already exists.`);
    }
    this.presets.set(preset.id, preset);
  }

  public static get(id: string): CaptionPreset {
    const p = this.presets.get(id);
    if (!p) {
      throw new ValidationError(`CAPTION_PRESET_NOT_FOUND: Preset '${id}' is not registered.`);
    }
    return p;
  }

  public static has(id: string): boolean {
    return this.presets.has(id);
  }

  public static list(): CaptionPreset[] {
    return Array.from(this.presets.values());
  }

  public static clear(): void {
    this.presets.clear();
  }
}

// Registro de presets estándar de la industria (TikTok, Reels, Shorts)
export const BuiltinCaptionPresets: CaptionPreset[] = [
  {
    id: "clean",
    name: "Clean Minimal",
    description: "Simple clean subtitles with soft shadow.",
    style: {
      fontFamily: "Inter",
      fontSize: 54,
      fontWeight: 600,
      color: { r: 1, g: 1, b: 1 },
      shadow: { offsetX: 0, offsetY: 4, blur: 8, color: { r: 0, g: 0, b: 0 }, opacity: 0.6 },
      alignment: "center",
    },
    layoutMode: "static",
    position: "bottom-center",
  },
  {
    id: "viral-tiktok",
    name: "Viral TikTok / Shorts",
    description: "High-impact bold text with black stroke and bright yellow active word highlight.",
    style: {
      fontFamily: "Montserrat",
      fontSize: 72,
      fontWeight: 900,
      color: { r: 1, g: 1, b: 1 },
      stroke: { width: 8, color: { r: 0, g: 0, b: 0 } },
      alignment: "center",
    },
    layoutMode: "highlight",
    position: "center",
    activeWordOverride: {
      color: { r: 1, g: 0.9, b: 0 }, // Amarillo intenso
      scale: 1.15,
      stroke: { width: 10, color: { r: 0, g: 0, b: 0 } },
    },
  },
  {
    id: "karaoke",
    name: "Karaoke Dynamic",
    description: "Continuous word-by-word karaoke flow.",
    style: {
      fontFamily: "Poppins",
      fontSize: 64,
      fontWeight: 800,
      color: { r: 0.7, g: 0.7, b: 0.7 }, // Grisáceo inactivo
      stroke: { width: 6, color: { r: 0, g: 0, b: 0 } },
      alignment: "center",
    },
    layoutMode: "karaoke",
    position: "bottom-center",
    activeWordOverride: {
      color: { r: 0, g: 1, b: 0.8 }, // Cian brillante activo
      scale: 1.2,
    },
  },
  {
    id: "cinematic",
    name: "Cinematic Box",
    description: "Subtitles enclosed in a clean translucent background box.",
    style: {
      fontFamily: "Roboto",
      fontSize: 48,
      fontWeight: 500,
      color: { r: 1, g: 1, b: 1 },
      background: {
        color: { r: 0, g: 0, b: 0 },
        opacity: 0.75,
        padding: { top: 12, bottom: 12, left: 24, right: 24 },
        cornerRadius: 8,
      },
      alignment: "center",
    },
    layoutMode: "static",
    position: "bottom-center",
  },
];

for (const p of BuiltinCaptionPresets) {
  if (!CaptionPresetRegistry.has(p.id)) {
    CaptionPresetRegistry.register(p);
  }
}
