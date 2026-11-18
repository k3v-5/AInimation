import {
  CaptionWord,
  EmojiPlacementInstance,
  EmojiPlacementRule,
  PositionedWord,
} from "../types/index.js";

export const DefaultEmojiCatalog: Record<string, string> = {
  money: "💸",
  fire: "🔥",
  warning: "⚠️",
  rocket: "🚀",
  idea: "💡",
  star: "⭐",
  heart: "❤️",
  time: "⏳",
  growth: "📈",
  check: "✅",
  target: "🎯",
  crown: "👑",
  shock: "😱",
  clap: "👏",
};

export const DefaultKeywordEmojiRules: EmojiPlacementRule[] = [
  { keyword: "dinero", semanticTag: "money", assetRef: "💸", priority: 1, position: "above", scale: 1.0, offset: { x: 0, y: -36 } },
  { keyword: "money", semanticTag: "money", assetRef: "💸", priority: 1, position: "above", scale: 1.0, offset: { x: 0, y: -36 } },
  { keyword: "dólares", semanticTag: "money", assetRef: "💸", priority: 1, position: "above", scale: 1.0, offset: { x: 0, y: -36 } },
  { keyword: "dollars", semanticTag: "money", assetRef: "💸", priority: 1, position: "above", scale: 1.0, offset: { x: 0, y: -36 } },
  { keyword: "fuego", semanticTag: "fire", assetRef: "🔥", priority: 1, position: "above", scale: 1.1, offset: { x: 0, y: -36 } },
  { keyword: "fire", semanticTag: "fire", assetRef: "🔥", priority: 1, position: "above", scale: 1.1, offset: { x: 0, y: -36 } },
  { keyword: "peligro", semanticTag: "warning", assetRef: "⚠️", priority: 1, position: "above", scale: 1.0, offset: { x: 0, y: -36 } },
  { keyword: "warning", semanticTag: "warning", assetRef: "⚠️", priority: 1, position: "above", scale: 1.0, offset: { x: 0, y: -36 } },
  { keyword: "error", semanticTag: "warning", assetRef: "⚠️", priority: 1, position: "above", scale: 1.0, offset: { x: 0, y: -36 } },
  { keyword: "rápido", semanticTag: "rocket", assetRef: "🚀", priority: 2, position: "above", scale: 1.0, offset: { x: 0, y: -36 } },
  { keyword: "rocket", semanticTag: "rocket", assetRef: "🚀", priority: 2, position: "above", scale: 1.0, offset: { x: 0, y: -36 } },
  { keyword: "idea", semanticTag: "idea", assetRef: "💡", priority: 1, position: "above", scale: 1.0, offset: { x: 0, y: -36 } },
  { keyword: "secreto", semanticTag: "idea", assetRef: "💡", priority: 2, position: "above", scale: 1.0, offset: { x: 0, y: -36 } },
  { keyword: "tiempo", semanticTag: "time", assetRef: "⏳", priority: 2, position: "above", scale: 1.0, offset: { x: 0, y: -36 } },
  { keyword: "crecer", semanticTag: "growth", assetRef: "📈", priority: 1, position: "above", scale: 1.0, offset: { x: 0, y: -36 } },
  { keyword: "éxito", semanticTag: "target", assetRef: "🎯", priority: 1, position: "above", scale: 1.0, offset: { x: 0, y: -36 } },
];

/**
 * Motor determinista de búsqueda y posicionamiento sincronizado de emojis e iconos (Fase 16).
 */
export class EmojiPlacementEngine {
  private rules: EmojiPlacementRule[];

  constructor(customRules?: EmojiPlacementRule[]) {
    this.rules = customRules ?? DefaultKeywordEmojiRules;
  }

  /**
   * Busca si una palabra coincide con una regla semántica de emoji.
   */
  public findMatchForWord(word: CaptionWord | PositionedWord): EmojiPlacementRule | undefined {
    const clean = word.text.replace(/[^\p{L}\p{N}]/gu, "").toLowerCase();

    // 1. Si la palabra ya tiene un tag semántico recomendado por el motor de inteligencia
    if (word.emphasis?.recommendedEmojiTag) {
      const tag = word.emphasis.recommendedEmojiTag;
      const rule = this.rules.find((r) => r.semanticTag === tag);
      if (rule) return rule;
    }

    // 2. Coincidencia por palabra clave
    const matches = this.rules.filter((r) => r.keyword.toLowerCase() === clean);
    if (matches.length === 0) return undefined;

    // Ordenar por prioridad (1 = mayor prioridad)
    matches.sort((a, b) => a.priority - b.priority);
    return matches[0];
  }

  /**
   * Genera la instancia posicional del emoji para una palabra ya ubicada en el layout.
   */
  public createPlacementInstance(
    word: PositionedWord,
    rule: EmojiPlacementRule
  ): EmojiPlacementInstance {
    const iconSize = Math.max(32, word.height * 0.85);

    let x = word.x + (word.width - iconSize) / 2 + rule.offset.x;
    let y = word.y - iconSize + rule.offset.y;

    if (rule.position === "before") {
      x = word.x - iconSize - 8 + rule.offset.x;
      y = word.y + (word.height - iconSize) / 2 + rule.offset.y;
    } else if (rule.position === "after") {
      x = word.x + word.width + 8 + rule.offset.x;
      y = word.y + (word.height - iconSize) / 2 + rule.offset.y;
    }

    return {
      assetRef: rule.assetRef,
      semanticTag: rule.semanticTag,
      x: Number(x.toFixed(2)),
      y: Number(y.toFixed(2)),
      width: Number(iconSize.toFixed(2)),
      height: Number(iconSize.toFixed(2)),
      scale: rule.scale,
      opacity: 1.0,
      position: rule.position,
      animation: word.animation,
    };
  }
}
