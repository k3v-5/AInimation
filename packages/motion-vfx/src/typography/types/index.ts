import { ColorRGBA, ShadowStyle, StrokeStyle } from "../../captions/types/index.js";
import { Time } from "../../core/types.js";

export type FontStyle = "normal" | "italic";
export type TextDirection = "ltr" | "rtl" | "auto";
export type TextAlignment = "left" | "center" | "right" | "justify";
export type TextBaseline = "alphabetic" | "top" | "middle" | "bottom";
export type WrapMode = "none" | "word" | "character";
export type StaggerMode = "forward" | "reverse" | "center" | "random";

export interface FontMetrics {
  ascent: number;
  descent: number;
  lineGap: number;
  unitsPerEm: number;
}

export interface FontResource {
  family: string;
  weight: number;
  style: FontStyle;
  metrics: FontMetrics;
  data?: unknown;
}

export interface LinearGradientFill {
  type: "linear";
  angle: number; // en grados (ej. 90 = vertical)
  stops: { offset: number; color: ColorRGBA }[];
}

export interface RadialGradientFill {
  type: "radial";
  stops: { offset: number; color: ColorRGBA }[];
}

export type PaintFill = ColorRGBA | LinearGradientFill | RadialGradientFill;

export interface TextPaintLayer {
  fill?: PaintFill;
  stroke?: StrokeStyle;
}

export interface TextBackgroundStyle {
  color: ColorRGBA;
  opacity?: number;
  padding: { top: number; right: number; bottom: number; left: number };
  cornerRadius?: number;
}

export interface TextPaint {
  fill: PaintFill;
  strokes?: StrokeStyle[];
  shadow?: ShadowStyle;
  background?: TextBackgroundStyle;
}

export interface TextStyle {
  fontFamily: string;
  fontSize: number;
  fontWeight: number;
  fontStyle?: FontStyle;
  letterSpacing: number; // tracking en px
  lineHeight: number; // multiplicador (ej. 1.25) o valor explícito
  wordSpacing?: number;
  alignment: TextAlignment;
  baseline?: TextBaseline;
  direction?: TextDirection;
  locale?: string;
}

export interface TextSpan {
  start: number; // inicio en índice de caracteres [start, end)
  end: number;
  style?: Partial<TextStyle>;
  paint?: Partial<TextPaint>;
}

export interface TextDocument {
  id: string;
  content: string;
  defaultStyle: TextStyle;
  defaultPaint: TextPaint;
  spans?: TextSpan[];
}

export interface Glyph {
  id: number;
  text: string;
  cluster: number;
  advanceX: number;
  offsetX: number;
  offsetY: number;
}

export interface ShapedText {
  glyphs: Glyph[];
  totalAdvance: number;
}

export interface GlyphPosition {
  glyph: Glyph;
  x: number;
  y: number;
  lineIndex: number;
  charIndex: number;
  style: TextStyle;
  paint: TextPaint;
}

export interface TextLine {
  lineIndex: number;
  text: string;
  glyphs: GlyphPosition[];
  width: number;
  height: number;
  baselineY: number;
}

export interface TextBounds {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface TextLayoutResult {
  layoutBounds: TextBounds;
  visualBounds: TextBounds;
  lines: TextLine[];
  glyphs: GlyphPosition[];
}

export interface GlyphTransform {
  position: { x: number; y: number };
  scale: { x: number; y: number };
  rotation: number; // grados
  opacity: number;
}

export interface TextPreset {
  id: string;
  name: string;
  description: string;
  style: TextStyle;
  paint: TextPaint;
  stagger?: {
    duration: Time;
    mode: StaggerMode;
    seed?: number;
  };
}
