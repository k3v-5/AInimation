import {
  AdaptiveBackgroundConfig,
  CaptionLayoutResult,
  CaptionLine,
  PositionedWord,
  RectBounds,
} from "../types/index.js";

/**
 * Generador determinista de fondos adaptativos para subtítulos (Pill y Split Boxes) (Fase 16).
 */
export class AdaptiveBackgroundEngine {
  /**
   * Genera los cuadros delimitadores de fondo para un resultado de layout dado.
   */
  public static applyBackgrounds(
    layoutResult: CaptionLayoutResult,
    config: AdaptiveBackgroundConfig
  ): CaptionLayoutResult {
    if (!config || config.type === "none") {
      return {
        ...layoutResult,
        backgrounds: [],
      };
    }

    const padding = config.padding ?? { top: 8, bottom: 8, left: 16, right: 16 };
    const globalBackgrounds: RectBounds[] = [];

    if (config.type === "pill") {
      // 1. Pill Background: Una caja redondeada por cada línea completa
      const updatedLines: CaptionLine[] = layoutResult.lines.map((line) => {
        const bgX = line.x - padding.left;
        const bgY = line.y - padding.top;
        const bgWidth = line.width + padding.left + padding.right;
        const bgHeight = line.height + padding.top + padding.bottom;

        const bounds: RectBounds = {
          x: Number(bgX.toFixed(2)),
          y: Number(bgY.toFixed(2)),
          width: Number(bgWidth.toFixed(2)),
          height: Number(bgHeight.toFixed(2)),
        };

        globalBackgrounds.push(bounds);
        return {
          ...line,
          backgroundBounds: bounds,
        };
      });

      return {
        ...layoutResult,
        lines: updatedLines,
        backgrounds: globalBackgrounds,
      };
    }

    if (config.type === "split-boxes") {
      // 2. Split Boxes: Una caja individual por cada palabra
      const updatedWords: PositionedWord[] = layoutResult.words.map((word) => {
        const bgX = word.x - padding.left;
        const bgY = word.y - padding.top;
        const bgWidth = word.width + padding.left + padding.right;
        const bgHeight = word.height + padding.top + padding.bottom;

        const bounds: RectBounds = {
          x: Number(bgX.toFixed(2)),
          y: Number(bgY.toFixed(2)),
          width: Number(bgWidth.toFixed(2)),
          height: Number(bgHeight.toFixed(2)),
        };

        globalBackgrounds.push(bounds);
        return {
          ...word,
          backgroundBounds: bounds,
        };
      });

      // Actualizar también la lista de palabras dentro de cada línea
      const updatedLines: CaptionLine[] = layoutResult.lines.map((line) => ({
        ...line,
        words: line.words.map((lw) => {
          const found = updatedWords.find((w) => w.id === lw.id);
          return found ?? lw;
        }),
      }));

      return {
        ...layoutResult,
        lines: updatedLines,
        words: updatedWords,
        backgrounds: globalBackgrounds,
      };
    }

    return layoutResult;
  }
}
