import { CaptionPresetError } from "../../errors/index.js";
import {
  AdaptiveBackgroundConfig,
  CaptionLayoutMode,
  CaptionPresetOptions,
  CaptionStyle,
  SemanticPosition,
  ViralPresetId,
  WordAnimationType,
  WordStyleOverride,
} from "../types/index.js";

export interface ViralCaptionPreset {
  id: ViralPresetId;
  name: string;
  description: string;
  style: CaptionStyle;
  layoutMode: CaptionLayoutMode;
  position: SemanticPosition;
  activeWordOverride?: WordStyleOverride;
  backgroundConfig: AdaptiveBackgroundConfig;
  animationType: WordAnimationType;
  safeZoneProfile: string;
  emojisEnabled: boolean;
}

export const VIRAL_CAPTION_PRESETS: Record<ViralPresetId, ViralCaptionPreset> = {
  "hormozi-impact": {
    id: "hormozi-impact",
    name: "Alex Hormozi Impact",
    description: "High-contrast uppercase bold text with heavy black stroke, vibrant yellow highlight and pop scale.",
    style: {
      fontFamily: "Montserrat",
      fontSize: 74,
      fontWeight: 900,
      color: { r: 1, g: 1, b: 1, a: 1 },
      stroke: { width: 10, color: { r: 0, g: 0, b: 0, a: 1 } },
      shadow: { offsetX: 0, offsetY: 6, blur: 0, color: { r: 0, g: 0, b: 0, a: 1 }, opacity: 1 },
      alignment: "center",
      textTransform: "uppercase",
      letterSpacing: 1,
    },
    layoutMode: "highlight",
    position: "center",
    activeWordOverride: {
      color: { r: 1, g: 0.9, b: 0, a: 1 }, // Amarillo intenso #FFE600
      scale: 1.22,
      stroke: { width: 12, color: { r: 0, g: 0, b: 0, a: 1 } },
    },
    backgroundConfig: {
      type: "split-boxes",
      color: { r: 0, g: 0, b: 0, a: 0.85 },
      padding: { top: 8, bottom: 8, left: 14, right: 14 },
      cornerRadius: 8,
      gap: 10,
    },
    animationType: "popScale",
    safeZoneProfile: "tiktok-portrait",
    emojisEnabled: true,
  },

  "beast-clean": {
    id: "beast-clean",
    name: "MrBeast Clean & Bold",
    description: "Crisp centered sans-serif with smooth drop shadow, subtle pop animation and high readability.",
    style: {
      fontFamily: "Inter",
      fontSize: 66,
      fontWeight: 800,
      color: { r: 1, g: 1, b: 1, a: 1 },
      shadow: { offsetX: 0, offsetY: 8, blur: 16, color: { r: 0, g: 0, b: 0, a: 0.8 }, opacity: 0.8 },
      alignment: "center",
      textTransform: "none",
    },
    layoutMode: "highlight",
    position: "bottom-center",
    activeWordOverride: {
      color: { r: 0.2, g: 0.9, b: 1, a: 1 }, // Azul eléctrico suave
      scale: 1.12,
    },
    backgroundConfig: {
      type: "none",
      color: { r: 0, g: 0, b: 0, a: 0 },
    },
    animationType: "popScale",
    safeZoneProfile: "shorts-portrait",
    emojisEnabled: true,
  },

  "vox-minimal": {
    id: "vox-minimal",
    name: "Vox Editorial Minimal",
    description: "Elegant typography with subtle translucent pill background and refined color accents.",
    style: {
      fontFamily: "Georgia",
      fontSize: 50,
      fontWeight: 600,
      color: { r: 0.95, g: 0.95, b: 0.95, a: 1 },
      alignment: "center",
      textTransform: "none",
    },
    layoutMode: "static",
    position: "bottom-center",
    activeWordOverride: {
      color: { r: 1, g: 0.8, b: 0.4, a: 1 }, // Dorado suave
      scale: 1.05,
    },
    backgroundConfig: {
      type: "pill",
      color: { r: 0.1, g: 0.1, b: 0.12, a: 0.8 },
      padding: { top: 10, bottom: 10, left: 24, right: 24 },
      cornerRadius: 12,
    },
    animationType: "colorHighlight",
    safeZoneProfile: "reels-portrait",
    emojisEnabled: false,
  },

  "karaoke-gradient": {
    id: "karaoke-gradient",
    name: "Karaoke Gradient Flow",
    description: "Dynamic word-by-word flow with soft glow pulse advancing across syllables.",
    style: {
      fontFamily: "Poppins",
      fontSize: 62,
      fontWeight: 800,
      color: { r: 0.6, g: 0.6, b: 0.65, a: 1 }, // Grisáceo inactivo
      stroke: { width: 4, color: { r: 0, g: 0, b: 0, a: 0.6 } },
      alignment: "center",
      textTransform: "none",
    },
    layoutMode: "karaoke",
    position: "bottom-center",
    activeWordOverride: {
      color: { r: 0, g: 1, b: 0.85, a: 1 }, // Cian / Turquesa vibrante
      scale: 1.18,
      glow: {
        color: { r: 0, g: 1, b: 0.85, a: 1 },
        radius: 20,
        intensity: 0.9,
      },
    },
    backgroundConfig: {
      type: "pill",
      color: { r: 0, g: 0, b: 0, a: 0.65 },
      padding: { top: 8, bottom: 8, left: 20, right: 20 },
      cornerRadius: 24,
    },
    animationType: "glowPulse",
    safeZoneProfile: "tiktok-portrait",
    emojisEnabled: true,
  },

  "neon-glow": {
    id: "neon-glow",
    name: "Cyberpunk Neon Glow",
    description: "Ultra-vibrant glowing neon aesthetics with organic shake on punchlines.",
    style: {
      fontFamily: "Impact",
      fontSize: 70,
      fontWeight: 900,
      color: { r: 1, g: 0.2, b: 0.8, a: 1 }, // Magenta neón
      stroke: { width: 6, color: { r: 0.1, g: 0, b: 0.2, a: 1 } },
      shadow: { offsetX: 0, offsetY: 0, blur: 24, color: { r: 1, g: 0.1, b: 0.7, a: 1 }, opacity: 1 },
      alignment: "center",
      textTransform: "uppercase",
    },
    layoutMode: "highlight",
    position: "center",
    activeWordOverride: {
      color: { r: 0.1, g: 1, b: 1, a: 1 }, // Cian neón eléctrico
      scale: 1.25,
      glow: {
        color: { r: 0.1, g: 1, b: 1, a: 1 },
        radius: 28,
        intensity: 1.0,
      },
    },
    backgroundConfig: {
      type: "split-boxes",
      color: { r: 0.05, g: 0.02, b: 0.1, a: 0.9 },
      padding: { top: 6, bottom: 6, left: 12, right: 12 },
      cornerRadius: 6,
      gap: 8,
    },
    animationType: "shake",
    safeZoneProfile: "tiktok-portrait",
    emojisEnabled: true,
  },
};

/**
 * Catálogo y fábrica de presets virales declarativos (Fase 16).
 */
export class ViralCaptionPresetRegistry {
  /**
   * Obtiene una copia profunda e inmutable de un preset viral.
   */
  public static getPreset(id: ViralPresetId, options?: CaptionPresetOptions): ViralCaptionPreset {
    const base = VIRAL_CAPTION_PRESETS[id];
    if (!base) {
      throw new CaptionPresetError(`Unknown viral preset id '${id}'. Available: ${Object.keys(VIRAL_CAPTION_PRESETS).join(", ")}`);
    }

    // Clonar profundamente
    const cloned: ViralCaptionPreset = JSON.parse(JSON.stringify(base));

    // Aplicar overrides opcionales de forma tipada
    if (options) {
      if (options.fontSize !== undefined && options.fontSize > 0) {
        cloned.style.fontSize = options.fontSize;
      }
      if (options.color) {
        cloned.style.color = { ...options.color };
      }
      if (options.highlightColor && cloned.activeWordOverride) {
        cloned.activeWordOverride.color = { ...options.highlightColor };
      }
      if (options.position) {
        cloned.position = options.position;
      }
      if (options.safeZone) {
        cloned.safeZoneProfile = options.safeZone;
      }
      if (options.emojisEnabled !== undefined) {
        cloned.emojisEnabled = options.emojisEnabled;
      }
    }

    return cloned;
  }

  /**
   * Lista todos los IDs de presets virales disponibles.
   */
  public static listPresets(): ViralCaptionPreset[] {
    return Object.values(VIRAL_CAPTION_PRESETS).map((p) => JSON.parse(JSON.stringify(p)));
  }
}
