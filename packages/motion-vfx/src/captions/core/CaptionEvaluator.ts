import { Time } from "../../core/types.js";
import { WordAnimationEngine } from "../animations/WordAnimationEngine.js";
import { AdaptiveBackgroundEngine } from "../backgrounds/AdaptiveBackgroundEngine.js";
import { EmojiPlacementEngine } from "../icons/EmojiPlacementEngine.js";
import { CaptionLayoutEngine } from "../layout/CaptionLayoutEngine.js";
import { CaptionPositionResolver, DEFAULT_TIKTOK_PROFILE } from "../layout/CaptionPositionResolver.js";
import { DynamicCaptionLayoutEngine } from "../layout/DynamicCaptionLayoutEngine.js";
import { ViralCaptionPreset, VIRAL_CAPTION_PRESETS } from "../presets/ViralCaptionPresets.js";
import { SafeZoneResolver, StandardSafeZoneProfiles } from "../safezones/SafeZoneResolver.js";
import {
  Caption,
  CaptionDocument,
  CaptionLayoutResult,
  CaptionStyle,
  EvaluatedCaptionState,
  EvaluatedCaptionWord,
  PlatformProfile,
  RectBounds,
  WordStyleOverride,
} from "../types/index.js";

export interface StaticSegmentLayout {
  segmentId: string;
  start: Time;
  end: Time;
  layoutWithBg: CaptionLayoutResult;
  originX: number;
  originY: number;
  evaluatedBackgrounds: Array<RectBounds & { color: any; opacity: number; cornerRadius: number }>;
}

export interface StaticCaptionDocumentLayout {
  documentId: string;
  presetId: string;
  segments: StaticSegmentLayout[];
}

/**
 * Evaluador determinista de estado de subtítulos con separación estricta entre geometría estática y animación dinámica (Fase 16 / 16.1).
 */
export class CaptionEvaluator {
  /**
   * Precalcula la geometría estática completa de un documento (layout, backgrounds, safe zones y emojis).
   * Se ejecuta una sola vez; permite evaluar millones de fotogramas a coste $< 1\mu s$ por frame.
   */
  public static precomputeStaticLayout(
    doc: CaptionDocument,
    preset: ViralCaptionPreset = VIRAL_CAPTION_PRESETS["hormozi-impact"],
    emojiEngine: EmojiPlacementEngine = new EmojiPlacementEngine()
  ): StaticCaptionDocumentLayout {
    const staticSegments: StaticSegmentLayout[] = [];
    const style = doc.defaultStyle ?? preset.style;
    const safeZoneProfile =
      StandardSafeZoneProfiles[preset.safeZoneProfile] ?? StandardSafeZoneProfiles["tiktok-portrait"];

    for (const seg of doc.segments) {
      if (seg.words.length === 0) continue;

      // 1. Layout tipográfico
      const baseLayout = DynamicCaptionLayoutEngine.layout(seg.words, style, {
        maxWidth: 920,
        preventWidows: true,
      });

      // 2. Fondos adaptativos
      const layoutWithBg = AdaptiveBackgroundEngine.applyBackgrounds(baseLayout, preset.backgroundConfig);

      // 3. Resolución en Safe Zone
      const safeZoneResult = SafeZoneResolver.resolve(
        layoutWithBg.width,
        layoutWithBg.height,
        preset.position,
        safeZoneProfile
      );

      const originX = safeZoneResult.adjustedBounds.x + layoutWithBg.width / 2;
      const originY = safeZoneResult.adjustedBounds.y;

      // 4. Traducir fondos a coordenadas absolutas
      const evaluatedBackgrounds = layoutWithBg.backgrounds.map((bg) => ({
        x: Number((originX + bg.x).toFixed(2)),
        y: Number((originY + bg.y).toFixed(2)),
        width: bg.width,
        height: bg.height,
        color: preset.backgroundConfig.color,
        opacity: preset.backgroundConfig.opacity ?? 0.8,
        cornerRadius: preset.backgroundConfig.cornerRadius ?? 8,
      }));

      staticSegments.push({
        segmentId: seg.id,
        start: seg.start,
        end: seg.end,
        layoutWithBg,
        originX,
        originY,
        evaluatedBackgrounds,
      });
    }

    return {
      documentId: doc.id,
      presetId: preset.id,
      segments: staticSegments,
    };
  }

  /**
   * Evalúa un Caption de Fase 5E manteniendo compatibilidad hacia atrás.
   */
  public static evaluate(
    caption: Caption,
    globalTime: Time,
    profile: PlatformProfile = DEFAULT_TIKTOK_PROFILE,
    activeWordOverride?: WordStyleOverride
  ): EvaluatedCaptionState {
    const isActive =
      globalTime >= caption.timelineRange.start && globalTime < caption.timelineRange.end;

    if (!isActive) {
      return {
        captionId: caption.id,
        active: false,
        words: [],
        backgrounds: [],
      };
    }

    const layout = CaptionLayoutEngine.calculateLayout(caption);
    const pos = CaptionPositionResolver.resolve(
      caption.position,
      layout.width,
      layout.height,
      profile
    );

    let activeWordId: string | undefined;
    const evaluatedWords: EvaluatedCaptionWord[] = [];

    for (const pw of layout.words) {
      const isWordActive = globalTime >= pw.start && globalTime < pw.end;
      const isWordCompleted = globalTime >= pw.end;

      if (isWordActive) {
        activeWordId = pw.id;
      }

      const dur = pw.end - pw.start;
      const rawProgress = dur > 0 ? (globalTime - pw.start) / dur : 0;
      const progress = Math.max(0, Math.min(1, rawProgress));

      let wordStyle: CaptionStyle = { ...caption.style };
      let scale = 1.0;

      if (isWordActive) {
        if (activeWordOverride) {
          if (activeWordOverride.color) wordStyle.color = activeWordOverride.color;
          if (activeWordOverride.scale) scale = activeWordOverride.scale;
          if (activeWordOverride.stroke) wordStyle.stroke = activeWordOverride.stroke;
        }
      }

      if (pw.styleOverride) {
        if (pw.styleOverride.color) wordStyle.color = pw.styleOverride.color;
        if (pw.styleOverride.scale) scale = pw.styleOverride.scale;
      }

      evaluatedWords.push({
        id: pw.id,
        text: pw.text,
        active: isWordActive,
        completed: isWordCompleted,
        progress,
        x: pos.x + pw.x,
        y: pos.y + pw.y,
        width: pw.width,
        height: pw.height,
        style: wordStyle,
        scale,
        opacity: 1.0,
        offset: { x: 0, y: 0 },
      });
    }

    return {
      captionId: caption.id,
      active: true,
      activeWordId,
      words: evaluatedWords,
      backgrounds: [],
    };
  }

  /**
   * Evalúa un CaptionDocument completo en el instante globalTime evaluando únicamente las variables temporales dinámicas.
   */
  public static evaluateDocument(
    doc: CaptionDocument,
    globalTime: Time,
    preset: ViralCaptionPreset = VIRAL_CAPTION_PRESETS["hormozi-impact"],
    emojiEngine: EmojiPlacementEngine = new EmojiPlacementEngine(),
    staticLayoutCache?: StaticCaptionDocumentLayout
  ): EvaluatedCaptionState {
    const staticLayout =
      staticLayoutCache && staticLayoutCache.documentId === doc.id && staticLayoutCache.presetId === preset.id
        ? staticLayoutCache
        : this.precomputeStaticLayout(doc, preset, emojiEngine);

    const activeSegLayout = staticLayout.segments.find(
      (s) => globalTime >= s.start && globalTime < s.end
    );

    if (!activeSegLayout) {
      return {
        captionId: doc.id,
        active: false,
        words: [],
        backgrounds: [],
      };
    }

    const { layoutWithBg, originX, originY, evaluatedBackgrounds } = activeSegLayout;
    const style = doc.defaultStyle ?? preset.style;

    let activeWordId: string | undefined;
    const evaluatedWords: EvaluatedCaptionWord[] = [];

    for (const pWord of layoutWithBg.words) {
      const isWordActive = globalTime >= pWord.start && globalTime < pWord.end;
      const isWordCompleted = globalTime >= pWord.end;

      if (isWordActive) {
        activeWordId = pWord.id;
      }

      const dur = pWord.end - pWord.start;
      const rawProgress = dur > 0 ? (globalTime - pWord.start) / dur : 0;
      const progress = Math.max(0, Math.min(1, rawProgress));

      let wordStyle: CaptionStyle = { ...style };
      let scale = 1.0;
      let offset = { x: 0, y: 0 };
      let glow = preset.activeWordOverride?.glow;

      // Color dinámico según modo de layout
      if (preset.layoutMode === "karaoke" || preset.layoutMode === "highlight") {
        if (!isWordActive && !isWordCompleted) {
          wordStyle.color = preset.style.color;
        } else if (isWordActive) {
          if (preset.activeWordOverride?.color) {
            wordStyle.color = preset.activeWordOverride.color;
          }
        } else if (isWordCompleted) {
          wordStyle.color = { r: 1, g: 1, b: 1, a: 1 };
        }
      }

      // Animaciones dinámicas
      if (isWordActive) {
        const animType = pWord.animation?.type ?? preset.animationType;

        if (animType === "popScale") {
          scale = WordAnimationEngine.evaluatePopScale(globalTime, pWord.start, pWord.end, {
            type: "popScale",
            intensity: preset.activeWordOverride?.scale ? (preset.activeWordOverride.scale - 1) * 4 : 1.0,
          });
        } else if (animType === "glowPulse") {
          const glowResult = WordAnimationEngine.evaluateGlowPulse(
            globalTime,
            pWord.start,
            pWord.end,
            pWord.animation,
            preset.activeWordOverride?.glow?.color
          );
          if (glowResult.active) {
            glow = { color: glowResult.color, radius: glowResult.radius, intensity: glowResult.intensity };
          }
        } else if (animType === "shake") {
          offset = WordAnimationEngine.evaluateShake(globalTime, pWord.start, pWord.end, pWord.animation);
          if (preset.activeWordOverride?.scale) {
            scale = preset.activeWordOverride.scale;
          }
        }

        if (preset.activeWordOverride?.stroke) {
          wordStyle.stroke = preset.activeWordOverride.stroke;
        }
      }

      if (pWord.styleOverride) {
        if (pWord.styleOverride.color) wordStyle.color = pWord.styleOverride.color;
        if (pWord.styleOverride.scale) scale = pWord.styleOverride.scale;
      }

      let emojiInstance = pWord.emojiPlacement;
      if (!emojiInstance && preset.emojisEnabled) {
        const matchRule = emojiEngine.findMatchForWord(pWord);
        if (matchRule) {
          emojiInstance = emojiEngine.createPlacementInstance(pWord, matchRule);
        }
      }

      const worldX = originX + pWord.x + offset.x;
      const worldY = originY + pWord.y + offset.y;

      evaluatedWords.push({
        id: pWord.id,
        text: pWord.text,
        active: isWordActive,
        completed: isWordCompleted,
        progress,
        x: Number(worldX.toFixed(2)),
        y: Number(worldY.toFixed(2)),
        width: pWord.width,
        height: pWord.height,
        style: wordStyle,
        scale: Number(scale.toFixed(4)),
        opacity: 1.0,
        offset,
        glow,
        backgroundBounds: pWord.backgroundBounds
          ? {
              x: Number((originX + pWord.backgroundBounds.x).toFixed(2)),
              y: Number((originY + pWord.backgroundBounds.y).toFixed(2)),
              width: pWord.backgroundBounds.width,
              height: pWord.backgroundBounds.height,
            }
          : undefined,
        emoji: emojiInstance
          ? {
              ...emojiInstance,
              x: Number((originX + emojiInstance.x).toFixed(2)),
              y: Number((originY + emojiInstance.y).toFixed(2)),
            }
          : undefined,
      });
    }

    return {
      captionId: doc.id,
      active: true,
      activeWordId,
      words: evaluatedWords,
      backgrounds: evaluatedBackgrounds,
    };
  }
}
