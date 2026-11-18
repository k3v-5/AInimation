import { Time } from "../../core/types.js";
import { TimeRangeData } from "../../timeline/types/index.js";

export type { Time };

// ==========================================
// Tipos Base Visuales y Estilos (Fase 5E / 16 / 16.1)
// ==========================================

export type CaptionLayoutMode = "static" | "word-by-word" | "karaoke" | "highlight";
export type TextAlignment = "left" | "center" | "right";
export type SemanticPosition =
  | "top"
  | "center"
  | "bottom"
  | "top-left"
  | "top-right"
  | "bottom-left"
  | "bottom-right"
  | "bottom-center"
  | "top-center";

export type CaptionTimingPrecision = "segment" | "word";

export interface ColorRGBA {
  r: number;
  g: number;
  b: number;
  a?: number;
}

export interface StrokeStyle {
  width: number;
  color: ColorRGBA;
  opacity?: number;
}

export interface ShadowStyle {
  offsetX: number;
  offsetY: number;
  blur: number;
  color: ColorRGBA;
  opacity?: number;
}

export interface BackgroundStyle {
  color: ColorRGBA;
  opacity?: number;
  padding?: { top: number; right: number; bottom: number; left: number };
  cornerRadius?: number;
}

export interface WordStyleOverride {
  color?: ColorRGBA;
  scale?: number;
  fontWeight?: number;
  stroke?: StrokeStyle;
  background?: BackgroundStyle;
  glow?: { color: ColorRGBA; radius: number; intensity: number };
}

export interface CaptionStyle {
  fontFamily: string;
  fontSize: number;
  fontWeight: number;
  color: ColorRGBA;
  stroke?: StrokeStyle;
  shadow?: ShadowStyle;
  background?: BackgroundStyle;
  alignment: TextAlignment;
  letterSpacing?: number;
  lineHeight?: number;
  textTransform?: "none" | "uppercase" | "lowercase" | "capitalize";
}

// ==========================================
// Métricas Tipográficas Deterministas
// ==========================================

export interface FontMetricProfile {
  id: string;
  avgCharWidthRatio: number; // Ratio promedio de ancho de glifo respecto al fontSize (ej. 0.55)
  spaceWidthRatio: number; // Ratio de ancho del espacio (ej. 0.30)
  lineHeightRatio: number; // Ratio de altura de línea (ej. 1.25)
  boldMultiplier: number; // Multiplicador para pesos >= 800 (ej. 1.12)
}

// ==========================================
// Prosodia, Énfasis y Animación (Fase 16)
// ==========================================

export interface ProsodySignals {
  energy?: number; // 0.0 -> 1.0 (amplitud acústica normalizada)
  pitch?: number; // Hz o semitonos relativos normalizados
  speakingRate?: number; // palabras por segundo o sílabas/s
  pauseBefore?: number; // segundos de silencio antes de la palabra
  pauseAfter?: number; // segundos de silencio tras la palabra
}

export type WordAnimationType = "popScale" | "glowPulse" | "colorHighlight" | "shake" | "none";

export interface WordAnimationConfig {
  type: WordAnimationType;
  duration?: number; // duración en segundos (o relativa a la palabra)
  intensity?: number; // 0.0 -> 1.0
  color?: ColorRGBA;
  easing?: string;
  seed?: number; // para animaciones estocásticas deterministas (Shake)
}

export interface EmphasisDecision {
  isEmphasized: boolean;
  score: number; // 0.0 -> 1.0
  reasons: string[];
  priority: number; // 1 (alta) a 10 (baja)
  recommendedStyle?: string;
  recommendedAnimation?: WordAnimationType;
  recommendedEmojiTag?: string;
}

// ==========================================
// Modelo Canónico de Captions (Fase 16 / 16.1)
// ==========================================

export interface CaptionWord {
  id: string;
  text: string;
  start: Time;
  end: Time;
  index?: number;
  confidence?: number;
  prosody?: ProsodySignals;
  emphasis?: EmphasisDecision;
  animation?: WordAnimationConfig;
  styleOverride?: WordStyleOverride;
  emojiPlacement?: EmojiPlacementInstance;
}

export interface CaptionSegment {
  id: string;
  start: Time;
  end: Time;
  text: string;
  words: CaptionWord[];
  timingPrecision?: CaptionTimingPrecision;
}

export interface CaptionDocument {
  id: string;
  duration: number;
  segments: CaptionSegment[];
  timingPrecision?: CaptionTimingPrecision;
  defaultStyle?: CaptionStyle;
  safeZoneProfile?: string;
  metadata?: Record<string, any>;
  schemaVersion?: string;
}

// ==========================================
// Fondos Adaptativos (Pill / Split Boxes)
// ==========================================

export type AdaptiveBackgroundType = "none" | "pill" | "split-boxes";

export interface AdaptiveBackgroundConfig {
  type: AdaptiveBackgroundType;
  color: ColorRGBA;
  opacity?: number;
  padding?: { top: number; right: number; bottom: number; left: number };
  cornerRadius?: number;
  gap?: number; // gap entre cajas para split-boxes
}

// ==========================================
// Safe Zones (TikTok, Reels, Shorts)
// ==========================================

export interface SafeArea {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

export interface RectBounds {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface SafeZoneProfile {
  id: string;
  name: string;
  version: string;
  canvasWidth: number;
  canvasHeight: number;
  topInset: number;
  bottomInset: number;
  leftInset: number;
  rightInset: number;
  forbiddenRegions?: RectBounds[];
  source?: string;
  confidence?: number;
}

export interface SafeZoneResolutionResult {
  originalBounds: RectBounds;
  adjustedBounds: RectBounds;
  position: SemanticPosition;
  offset: { x: number; y: number };
  status: "safe" | "adjusted" | "unresolved";
  diagnostics: string[];
}

export interface PlatformProfile {
  id: string;
  name: string;
  width: number;
  height: number;
  safeArea: SafeArea;
}

// ==========================================
// Emojis / Icon Placement
// ==========================================

export interface EmojiPlacementRule {
  keyword: string;
  semanticTag: string;
  assetRef: string; // emoji Unicode o ID de asset
  priority: number;
  position: "above" | "before" | "after" | "inline";
  scale: number;
  offset: { x: number; y: number };
}

export interface EmojiPlacementInstance {
  assetRef: string;
  semanticTag: string;
  x: number;
  y: number;
  width: number;
  height: number;
  scale: number;
  opacity: number;
  position: "above" | "before" | "after" | "inline";
  animation?: WordAnimationConfig;
}

// ==========================================
// Presets Virales
// ==========================================

export type ViralPresetId =
  | "hormozi-impact"
  | "beast-clean"
  | "vox-minimal"
  | "karaoke-gradient"
  | "neon-glow";

export interface CaptionPresetOptions {
  fontSize?: number;
  color?: ColorRGBA;
  highlightColor?: ColorRGBA;
  position?: SemanticPosition;
  safeZone?: string;
  emojisEnabled?: boolean;
}

// ==========================================
// Transcripciones Raw (Fase 5E / Legacy)
// ==========================================

export interface TranscriptWord {
  id: string;
  text: string;
  start: Time;
  end: Time;
  confidence?: number;
  prosody?: ProsodySignals;
}

export interface TranscriptSegment {
  id: string;
  start: Time;
  end: Time;
  text: string;
  words?: TranscriptWord[];
}

export interface Transcript {
  id: string;
  language?: string;
  segments: TranscriptSegment[];
}

export interface Caption {
  id: string;
  timelineRange: TimeRangeData;
  words: CaptionWord[];
  style: CaptionStyle;
  layoutMode: CaptionLayoutMode;
  position: SemanticPosition;
}

// ==========================================
// Layout & Evaluación
// ==========================================

export interface PositionedWord {
  id: string;
  text: string;
  start: Time;
  end: Time;
  index?: number;
  x: number;
  y: number;
  width: number;
  height: number;
  line: number;
  styleOverride?: WordStyleOverride;
  prosody?: ProsodySignals;
  emphasis?: EmphasisDecision;
  animation?: WordAnimationConfig;
  emojiPlacement?: EmojiPlacementInstance;
  backgroundBounds?: RectBounds;
}

export interface CaptionLine {
  lineIndex: number;
  text: string;
  words: PositionedWord[];
  width: number;
  height: number;
  x: number;
  y: number;
  backgroundBounds?: RectBounds;
}

export interface CaptionLayoutResult {
  width: number;
  height: number;
  x: number;
  y: number;
  lines: CaptionLine[];
  words: PositionedWord[];
  backgrounds: RectBounds[];
  overflowStatus: "none" | "lines-exceeded" | "width-exceeded";
  diagnostics: string[];
}

export interface EvaluatedCaptionWord {
  id: string;
  text: string;
  active: boolean;
  completed: boolean;
  progress: number; // 0 -> 1 durante el tiempo de la palabra
  x: number;
  y: number;
  width: number;
  height: number;
  style: CaptionStyle;
  scale: number;
  opacity?: number;
  offset?: { x: number; y: number };
  glow?: { color: ColorRGBA; radius: number; intensity: number };
  backgroundBounds?: RectBounds;
  emoji?: EmojiPlacementInstance;
}

export interface EvaluatedCaptionState {
  captionId: string;
  active: boolean;
  activeWordId?: string;
  words: EvaluatedCaptionWord[];
  backgrounds: Array<RectBounds & { color: ColorRGBA; opacity: number; cornerRadius: number }>;
}
