/**
 * REQ-025: Data Visualization Engine Constants & Presets.
 */

export const DATAVIZ_SCHEMA_VERSION = "1.0.0" as const;
export const DATAVIZ_ENGINE_VERSION = "v4.0.0-editorial-master" as const;

// Operational Limits (REQ-025 §89)
export const MAX_DATA_POINTS = 1000;
export const MAX_TIMELINE_EVENTS = 500;
export const MAX_LABEL_LENGTH = 200;
export const MAX_DESCRIPTION_LENGTH = 1000;

// Geometry & Layout Constants
export const DEFAULT_BAR_WIDTH_RATIO = 0.72; // REQ-025 §20

// Timing & Duration Defaults (REQ-025 §47)
export const DEFAULT_DURATIONS_SEC = {
  BAR_CHART: 2.0,
  LINE_GRAPH: 2.5,
  BIG_STAT: 2.0,
  CHRONOLOGY: 4.0,
} as const;

// Animation Defaults (REQ-025 §22, §28, §48)
export const DEFAULT_BAR_GROWTH_SEC = 0.8;
export const DEFAULT_LINE_WRITE_ON_SEC = 1.2;
export const DEFAULT_BIG_STAT_GROWTH_SEC = 0.8;
export const DEFAULT_BAR_STAGGER_SEC = 0.05;
export const DEFAULT_TIMELINE_STAGGER_SEC = 0.08;

// Frame Rates Allowed (REQ-025 §13)
export const ALLOWED_FPS = [24, 25, 30, 50, 60] as const;

// Composition Presets Dimensions (REQ-025 §13)
export const COMPOSITION_PRESET_DIMENSIONS = {
  LANDSCAPE_16_9: { width: 1920, height: 1080 },
  VERTICAL_9_16: { width: 1080, height: 1920 },
  SQUARE_1_1: { width: 1080, height: 1080 },
} as const;

// Editorial Typography Priorities (REQ-025 §33)
export const EDITORIAL_FONT_PRIORITIES = [
  "Impact",
  "Arial Black",
  "Anton",
  "sans-serif",
] as const;

// Editorial Color Defaults (REQ-025 §42)
export const DEFAULT_EDITORIAL_COLORS = {
  accent: "#FF1424", // TIME Carmesi
  background: "#FFFFFF",
  text: "#000000",
  muted: "#666666",
  positive: "#00C853",
  negative: "#D50000",
  primary: "#111111",
  secondary: "#333333",
} as const;
