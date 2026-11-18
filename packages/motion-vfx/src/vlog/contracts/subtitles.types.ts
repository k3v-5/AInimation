import { z } from "zod";
import { SupportedLocaleSchema } from "./language.types.js";
import { SupportedLocale } from "./vlog.constants.js";

/** Modos de renderizado de subtítulos */
export type SubtitleMode = "STANDARD" | "WORD_BY_WORD" | "KARAOKE" | "EMPHASIS";

export const SubtitleModeSchema = z.enum(["STANDARD", "WORD_BY_WORD", "KARAOKE", "EMPHASIS"]);

/** Palabra individual en subtítulo para animación Karaoke */
export interface SubtitleWord {
  word: string;
  startSeconds: number;
  endSeconds: number;
  isHighlighted: boolean;
  highlightColor?: string;
}

export const SubtitleWordSchema = z.object({
  word: z.string().min(1),
  startSeconds: z.number().min(0),
  endSeconds: z.number().min(0),
  isHighlighted: z.boolean().default(false),
  highlightColor: z.string().optional(),
});

/** Estilo tipográfico y visual para subtítulos (TIME Style / Minimal / Hormozi) */
export interface SubtitleStyle {
  fontFamily: string;
  fontSizePx: number;
  lineHeightPx?: number;
  fillColor: string; // Hex ej. "#FFFFFF"
  strokeColor?: string;
  strokeWidthPx?: number;
  highlightFillColor: string; // Hex ej. "#FF1424" (Carmesí)
  textTransform: "none" | "uppercase" | "lowercase";
  letterSpacing: number; // Negativo ej. -20 para condensado
  verticalStretchPercent: number; // 120% - 150% (Estilo TIME Editorial)
  boxBackground?: {
    enabled: boolean;
    color: string;
    opacity: number;
    paddingPx: number;
    borderRadiusPx: number;
  };
}

export const SubtitleStyleSchema = z.object({
  fontFamily: z.string().min(1),
  fontSizePx: z.number().positive(),
  lineHeightPx: z.number().positive().optional(),
  fillColor: z.string(),
  strokeColor: z.string().optional(),
  strokeWidthPx: z.number().min(0).optional(),
  highlightFillColor: z.string(),
  textTransform: z.enum(["none", "uppercase", "lowercase"]).default("uppercase"),
  letterSpacing: z.number().default(0),
  verticalStretchPercent: z.number().min(100).max(200).default(100),
  boxBackground: z.object({
    enabled: z.boolean(),
    color: z.string(),
    opacity: z.number().min(0).max(1),
    paddingPx: z.number().min(0),
    borderRadiusPx: z.number().min(0),
  }).optional(),
});

/** Subtitle Cue o bloque temporal de visualización */
export interface SubtitleCue {
  id: string;
  locale: SupportedLocale;
  startSeconds: number;
  endSeconds: number;
  text: string;
  words: SubtitleWord[];
  position: {
    normalizedX: number; // [0, 1]
    normalizedY: number; // [0, 1]
    alignment: "left" | "center" | "right";
  };
  styleOverride?: Partial<SubtitleStyle>;
}

export const SubtitleCueSchema = z.object({
  id: z.string().min(1),
  locale: SupportedLocaleSchema,
  startSeconds: z.number().min(0),
  endSeconds: z.number().min(0),
  text: z.string(),
  words: z.array(SubtitleWordSchema),
  position: z.object({
    normalizedX: z.number().min(0).max(1).default(0.5),
    normalizedY: z.number().min(0).max(1).default(0.85),
    alignment: z.enum(["left", "center", "right"]).default("center"),
  }),
  styleOverride: SubtitleStyleSchema.partial().optional(),
});

/** Pista completa de subtítulos para un idioma */
export interface SubtitleTrack {
  id: string;
  locale: SupportedLocale;
  mode: SubtitleMode;
  cues: SubtitleCue[];
  style: SubtitleStyle;
  checksumSha256: string;
}

export const SubtitleTrackSchema = z.object({
  id: z.string().min(1),
  locale: SupportedLocaleSchema,
  mode: SubtitleModeSchema,
  cues: z.array(SubtitleCueSchema),
  style: SubtitleStyleSchema,
  checksumSha256: z.string().min(64).max(64),
});

/** Estilo maestro por defecto: Editorial Poster / TIME Style */
export const DEFAULT_TIME_EDITORIAL_SUBTITLE_STYLE: SubtitleStyle = {
  fontFamily: "Impact",
  fontSizePx: 72,
  fillColor: "#FFFFFF",
  strokeColor: "#000000",
  strokeWidthPx: 4,
  highlightFillColor: "#FF1424", // Rojo Carmesí TIME Style
  textTransform: "uppercase",
  letterSpacing: -20,
  verticalStretchPercent: 135,
};
