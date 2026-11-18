import { VisualizationStyle, SafeZoneConfig, AspectRatio } from "./types.js";

/**
 * REQ-025: Constantes canónicas del Data Visualization Engine.
 */

export const ASPECT_RATIO_DIMENSIONS: Record<AspectRatio, { width: number; height: number }> = {
  "16:9": { width: 1920, height: 1080 },
  "9:16": { width: 1080, height: 1920 },
  "1:1": { width: 1080, height: 1080 },
};

export const STANDARD_RESOLUTIONS = [
  { width: 1920, height: 1080, label: "FHD 16:9" },
  { width: 1080, height: 1920, label: "Shorts/TikTok 9:16" },
  { width: 1080, height: 1080, label: "Square 1:1" },
  { width: 3840, height: 2160, label: "4K UHD 16:9" },
] as const;

export const DEFAULT_SAFE_ZONE: SafeZoneConfig = {
  top: 90,
  right: 90,
  bottom: 90,
  left: 90,
  unit: "PX",
};

export const TIME_EDITORIAL_STYLE: VisualizationStyle = {
  backgroundColor: "#0D0D0D",
  primaryColor: "#FF1424", // Crimson Red
  secondaryColor: "#E0E0E0",
  accentColor: "#FF1424",
  textColor: "#FFFFFF",
  fontFamily: "Impact",
  fontWeight: 900,
  titleFontSize: 48,
  labelFontSize: 24,
  valueFontSize: 32,
  tracking: -20,
  gridOpacity: 0.15,
  borderWidth: 2,
};

export const DEFAULT_VISUALIZATION_STYLE: VisualizationStyle = {
  backgroundColor: "#1A1A1A",
  primaryColor: "#007ACC",
  secondaryColor: "#808080",
  accentColor: "#FF8C00",
  textColor: "#FFFFFF",
  fontFamily: "Arial Black",
  fontWeight: 700,
  titleFontSize: 40,
  labelFontSize: 20,
  valueFontSize: 28,
  tracking: 0,
  gridOpacity: 0.2,
  borderWidth: 2,
};

export const DEFAULT_ANIMATION_CONFIG = {
  entranceDurationSeconds: 1.2,
  exitDurationSeconds: 0.8,
  easing: "EASE_OUT" as const,
  staggerSeconds: 0.08,
  overshoot: 0.0,
};

export const EPSILON = 1e-6;
export const ENGINE_VERSION = "4.0.0";
export const HUMAN_REVIEW_CONFIDENCE_THRESHOLD = 0.70;

// REQ-025 TIME Editorial Constants
export const CRIMSON = "#FF1424";
export const WHITE = "#FFFFFF";
export const BLACK = "#000000";

export const DEFAULT_VISUALIZATION_VIEWPORT = {
  width: 1920,
  height: 1080,
  safeMarginTop: 90,
  safeMarginRight: 90,
  safeMarginBottom: 90,
  safeMarginLeft: 90,
};

export const DEFAULT_VISUALIZATION_THEME = {
  backgroundColor: BLACK,
  primaryColor: CRIMSON,
  secondaryColor: WHITE,
  accentColor: CRIMSON,
  textColor: WHITE,
  mutedTextColor: "#888888",
  gridColor: "#333333",
  negativeColor: "#FF4444",
  fontFamily: "Impact",
  fontWeight: 900,
};
