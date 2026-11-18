import {
  SelectedTextTarget,
  TextLayoutData,
  TextSelectorConfig,
  TextStaggerConfig,
} from "../types/index.js";

/**
 * Generador pseudo-aleatorio lineal determinista para reproducción exacta de TextOrder "random".
 */
class DeterministicPRNG {
  private state: number;

  constructor(seed: number = 42) {
    this.state = seed % 2147483647;
    if (this.state <= 0) this.state += 2147483646;
  }

  public next(): number {
    this.state = (this.state * 16807) % 2147483647;
    return (this.state - 1) / 2147483646;
  }
}

/**
 * Selector de subtargets tipográficos y cálculo de retardos escalonados (Fase 4B).
 */
export class TextSelector {
  /**
   * Selecciona los subtargets virtuales del texto con sus correspondientes retardos.
   */
  public static select(
    elementId: string,
    layout: TextLayoutData,
    config: TextSelectorConfig,
    stagger?: TextStaggerConfig | number
  ): SelectedTextTarget[] {
    const scope = config.scope ?? "character";
    const excludeWhitespace = config.excludeWhitespace !== false;
    const order = config.order ?? "forward";

    // 1. Recolectar candidatos según el scope
    let candidates: Array<{
      targetId: string;
      tokenText: string;
      rawIndex: number;
      wordIndex?: number;
      charIndexInWord?: number;
    }> = [];

    switch (scope) {
      case "element": {
        candidates.push({
          targetId: elementId,
          tokenText: layout.rawText,
          rawIndex: 0,
        });
        break;
      }

      case "line": {
        layout.lines.forEach((line, i) => {
          candidates.push({
            targetId: `${elementId}:line:${i}`,
            tokenText: line.text,
            rawIndex: i,
          });
        });
        break;
      }

      case "word": {
        layout.words.forEach((word, i) => {
          const isWhitespace = /^\s+$/.test(word.text);
          if (!excludeWhitespace || !isWhitespace) {
            candidates.push({
              targetId: `${elementId}:word:${i}`,
              tokenText: word.text,
              rawIndex: i,
              wordIndex: i,
            });
          }
        });
        break;
      }

      case "character": {
        layout.characters.forEach((char, i) => {
          if (!excludeWhitespace || !char.isWhitespace) {
            const word = layout.words[char.wordIndex];
            const charIndexInWord = word ? word.characterIndices.indexOf(char.index) : 0;
            candidates.push({
              targetId: `${elementId}:char:${i}`,
              tokenText: char.grapheme,
              rawIndex: i,
              wordIndex: char.wordIndex,
              charIndexInWord: Math.max(0, charIndexInWord),
            });
          }
        });
        break;
      }
    }

    // 2. Aplicar range filter si está definido
    if (config.range) {
      const start = config.range.start ?? 0;
      const end = config.range.end ?? candidates.length;
      candidates = candidates.filter((_, idx) => idx >= start && idx < end);
    }

    const total = candidates.length;
    if (total === 0) return [];

    // 3. Reordenar según TextOrder
    const orderedIndices: number[] = Array.from({ length: total }, (_, i) => i);

    switch (order) {
      case "reverse":
        orderedIndices.reverse();
        break;

      case "center": {
        const mid = (total - 1) / 2;
        orderedIndices.sort((a, b) => Math.abs(a - mid) - Math.abs(b - mid));
        break;
      }

      case "edges": {
        const mid = (total - 1) / 2;
        orderedIndices.sort((a, b) => Math.abs(b - mid) - Math.abs(a - mid));
        break;
      }

      case "random": {
        const prng = new DeterministicPRNG(config.seed ?? 12345);
        for (let i = orderedIndices.length - 1; i > 0; i--) {
          const j = Math.floor(prng.next() * (i + 1));
          const temp = orderedIndices[i];
          orderedIndices[i] = orderedIndices[j];
          orderedIndices[j] = temp;
        }
        break;
      }

      case "forward":
      default:
        // Mantener orden natural
        break;
    }

    // 4. Calcular delays
    const flatStaggerDelay = typeof stagger === "number" ? stagger : (stagger?.delay ?? 0.05);
    const hasNestedStagger =
      typeof stagger === "object" &&
      stagger !== null &&
      stagger.wordDelay !== undefined &&
      stagger.characterDelay !== undefined;

    const results: SelectedTextTarget[] = [];

    for (let orderPos = 0; orderPos < total; orderPos++) {
      const candidateIndex = orderedIndices[orderPos];
      const item = candidates[candidateIndex];

      let delay = 0;
      if (hasNestedStagger && item.wordIndex !== undefined && item.charIndexInWord !== undefined) {
        // Fórmula de Stagger Anidado: (w * wordDelay) + (c * charDelay)
        const wDelay = (stagger as TextStaggerConfig).wordDelay ?? 0;
        const cDelay = (stagger as TextStaggerConfig).characterDelay ?? 0;
        delay = item.wordIndex * wDelay + item.charIndexInWord * cDelay;
      } else {
        // Stagger plano basado en orden posicional
        delay = orderPos * flatStaggerDelay;
      }

      results.push({
        targetId: item.targetId,
        elementId,
        scope,
        index: candidateIndex,
        total,
        delay,
        tokenText: item.tokenText,
      });
    }

    return results;
  }
}
