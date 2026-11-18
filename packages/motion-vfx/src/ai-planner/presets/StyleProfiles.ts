import { StyleProfile } from "../types/index.js";

export const BuiltinStyleProfiles: Record<string, StyleProfile> = {
  "fast-tiktok": {
    id: "fast-tiktok",
    name: "Fast-Paced TikTok / Reels",
    palette: {
      primary: { r: 1.0, g: 0.9, b: 0.0, a: 1.0 }, // Amarillo viral
      secondary: { r: 0.0, g: 0.9, b: 1.0, a: 1.0 }, // Cian
      accent: { r: 1.0, g: 0.2, b: 0.4, a: 1.0 }, // Magenta punch
      background: { r: 0.05, g: 0.05, b: 0.08, a: 1.0 },
    },
    captionStyle: "word-pop",
    defaultTransition: "zoom",
    motionIntensity: "high",
  },
  "modern-youtube": {
    id: "modern-youtube",
    name: "Modern YouTube Explainer",
    palette: {
      primary: { r: 0.1, g: 0.5, b: 1.0, a: 1.0 }, // Azul tech
      secondary: { r: 0.2, g: 0.8, b: 0.4, a: 1.0 }, // Verde acento
      accent: { r: 1.0, g: 0.6, b: 0.0, a: 1.0 }, // Naranja
      background: { r: 0.1, g: 0.1, b: 0.12, a: 1.0 },
    },
    captionStyle: "karaoke",
    defaultTransition: "wipe",
    motionIntensity: "medium",
  },
  cinematic: {
    id: "cinematic",
    name: "Cinematic Documentary",
    palette: {
      primary: { r: 0.9, g: 0.85, b: 0.75, a: 1.0 }, // Cálido marfil
      secondary: { r: 0.6, g: 0.5, b: 0.4, a: 1.0 },
      accent: { r: 0.8, g: 0.3, b: 0.2, a: 1.0 },
      background: { r: 0.02, g: 0.02, b: 0.03, a: 1.0 },
    },
    captionStyle: "minimal",
    defaultTransition: "fade",
    motionIntensity: "low",
  },
};
