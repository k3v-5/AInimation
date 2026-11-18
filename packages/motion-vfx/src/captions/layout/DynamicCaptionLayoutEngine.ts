import {
  CaptionLayoutResult,
  CaptionLine,
  CaptionStyle,
  CaptionWord,
  FontMetricProfile,
  PositionedWord,
  RectBounds,
} from "../types/index.js";

export interface DynamicLayoutOptions {
  maxWidth?: number;
  maxLines?: number;
  canvasWidth?: number;
  canvasHeight?: number;
  preventWidows?: boolean;
  fontMetricProfile?: FontMetricProfile;
}

export const DefaultFontMetricProfile: FontMetricProfile = {
  id: "standard-sans-metric@v1",
  avgCharWidthRatio: 0.55,
  spaceWidthRatio: 0.30,
  lineHeightRatio: 1.25,
  boldMultiplier: 1.12,
};

/**
 * Motor determinista de maquetación dinámica de subtítulos con función matemática de costo y prevención de huérfanas (Fase 16 / 16.1).
 */
export class DynamicCaptionLayoutEngine {
  /**
   * Maqueta una lista de palabras dentro de los límites, métricas y estilos especificados.
   */
  public static layout(
    words: CaptionWord[],
    style: CaptionStyle,
    options: DynamicLayoutOptions = {}
  ): CaptionLayoutResult {
    const maxWidth = options.maxWidth ?? 900;
    const maxLines = options.maxLines ?? 3;
    const preventWidows = options.preventWidows ?? true;
    const metrics = options.fontMetricProfile ?? DefaultFontMetricProfile;
    const fontSize = style.fontSize || 64;
    const lineHeight = style.lineHeight ?? fontSize * metrics.lineHeightRatio;
    const letterSpacing = style.letterSpacing ?? 0;
    const alignment = style.alignment ?? "center";
    const diagnostics: string[] = [];

    if (!words || words.length === 0) {
      return {
        width: 0,
        height: 0,
        x: 0,
        y: 0,
        lines: [],
        words: [],
        backgrounds: [],
        overflowStatus: "none",
        diagnostics: ["empty-words-list"],
      };
    }

    // 1. Estimar anchuras de palabras de forma 100% matemática y reproducible
    const isBold = style.fontWeight >= 700;
    const charMultiplier = isBold
      ? metrics.avgCharWidthRatio * metrics.boldMultiplier
      : metrics.avgCharWidthRatio;
    const spaceWidth = fontSize * metrics.spaceWidthRatio + letterSpacing;

    const measuredWords: Array<{ word: CaptionWord; width: number; height: number }> = words.map((w) => {
      const text = style.textTransform === "uppercase" ? w.text.toUpperCase() : w.text;
      const textWidth = Math.max(
        fontSize * 0.4,
        text.length * (fontSize * charMultiplier) + (text.length - 1) * letterSpacing
      );
      return {
        word: { ...w, text },
        width: Number(textWidth.toFixed(2)),
        height: Number(lineHeight.toFixed(2)),
      };
    });

    // 2. Generar candidatos de distribución de líneas (Greedy vs Rebalanced)
    // Candidato A: Greedy Line-Breaking
    const greedyLines: Array<Array<{ word: CaptionWord; width: number; height: number }>> = [];
    let currentLine: Array<{ word: CaptionWord; width: number; height: number }> = [];
    let currentLineWidth = 0;

    for (const mWord of measuredWords) {
      const neededWidth = currentLine.length > 0 ? spaceWidth + mWord.width : mWord.width;

      if (currentLine.length > 0 && currentLineWidth + neededWidth > maxWidth) {
        greedyLines.push(currentLine);
        currentLine = [mWord];
        currentLineWidth = mWord.width;
      } else {
        currentLine.push(mWord);
        currentLineWidth += neededWidth;
      }
    }
    if (currentLine.length > 0) {
      greedyLines.push(currentLine);
    }

    // Candidato B: Rebalanceo para prevención de huérfanas
    let chosenLines = greedyLines;

    if (preventWidows && greedyLines.length > 1) {
      const lastLineIdx = greedyLines.length - 1;
      const lastLine = greedyLines[lastLineIdx];
      const prevLine = greedyLines[lastLineIdx - 1];

      // Si la última línea tiene 1 sola palabra y la penúltima tiene >= 2 palabras
      if (lastLine.length === 1 && prevLine.length >= 2) {
        // Clonar candidato y rebalancear
        const rebalancedCandidate: Array<Array<{ word: CaptionWord; width: number; height: number }>> =
          greedyLines.map((l) => [...l]);
        const rebalancedPrev = rebalancedCandidate[lastLineIdx - 1];
        const rebalancedLast = rebalancedCandidate[lastLineIdx];

        const wordToMove = rebalancedPrev.pop()!;
        rebalancedLast.unshift(wordToMove);

        // Calcular costo de ambos candidatos
        const costA = this.calculateLayoutCost(greedyLines, maxWidth, true);
        const costB = this.calculateLayoutCost(rebalancedCandidate, maxWidth, false);

        if (costB < costA) {
          chosenLines = rebalancedCandidate;
          diagnostics.push("widow-prevented-rebalanced-lines");
        }
      }
    }

    // 3. Chequeo de Overflow
    let overflowStatus: "none" | "lines-exceeded" | "width-exceeded" = "none";
    if (chosenLines.length > maxLines) {
      overflowStatus = "lines-exceeded";
      diagnostics.push(`max-lines-exceeded: got ${chosenLines.length}, allowed ${maxLines}`);
    }

    // 4. Posicionar palabras por línea respetando alineación
    const positionedLines: CaptionLine[] = [];
    const allPositionedWords: PositionedWord[] = [];
    let totalBlockWidth = 0;
    const totalBlockHeight = chosenLines.length * lineHeight;

    for (let lIdx = 0; lIdx < chosenLines.length; lIdx++) {
      const lineWords = chosenLines[lIdx];
      const lineText = lineWords.map((mw) => mw.word.text).join(" ");
      const wordsWidthSum = lineWords.reduce((sum, mw) => sum + mw.width, 0);
      const totalSpacing = Math.max(0, (lineWords.length - 1) * spaceWidth);
      const lineWidth = wordsWidthSum + totalSpacing;
      totalBlockWidth = Math.max(totalBlockWidth, lineWidth);

      let lineStartX = 0;
      if (alignment === "center") {
        lineStartX = -lineWidth / 2;
      } else if (alignment === "right") {
        lineStartX = -lineWidth;
      } else {
        lineStartX = 0;
      }

      const lineY = lIdx * lineHeight;
      let currentWordX = lineStartX;
      const linePositionedWords: PositionedWord[] = [];

      for (const mw of lineWords) {
        const pWord: PositionedWord = {
          id: mw.word.id,
          text: mw.word.text,
          start: mw.word.start,
          end: mw.word.end,
          index: mw.word.index,
          x: Number(currentWordX.toFixed(2)),
          y: Number(lineY.toFixed(2)),
          width: mw.width,
          height: mw.height,
          line: lIdx,
          styleOverride: mw.word.styleOverride,
          prosody: mw.word.prosody,
          emphasis: mw.word.emphasis,
          animation: mw.word.animation,
          emojiPlacement: mw.word.emojiPlacement,
        };

        linePositionedWords.push(pWord);
        allPositionedWords.push(pWord);
        currentWordX += mw.width + spaceWidth;
      }

      positionedLines.push({
        lineIndex: lIdx,
        text: lineText,
        words: linePositionedWords,
        width: Number(lineWidth.toFixed(2)),
        height: Number(lineHeight.toFixed(2)),
        x: Number(lineStartX.toFixed(2)),
        y: Number(lineY.toFixed(2)),
      });
    }

    return {
      width: Number(totalBlockWidth.toFixed(2)),
      height: Number(totalBlockHeight.toFixed(2)),
      x: 0,
      y: 0,
      lines: positionedLines,
      words: allPositionedWords,
      backgrounds: [],
      overflowStatus,
      diagnostics,
    };
  }

  /**
   * Función matemática de penalización / costo para clasificar candidatos de layout.
   */
  private static calculateLayoutCost(
    lines: Array<Array<{ word: CaptionWord; width: number; height: number }>>,
    maxWidth: number,
    hasWidow: boolean
  ): number {
    let cost = 0;
    const spaceWidth = 20;

    for (const line of lines) {
      const width = line.reduce((sum, w) => sum + w.width, 0) + Math.max(0, line.length - 1) * spaceWidth;
      if (width > maxWidth) {
        cost += 100000; // Penalización insuperable por desborde
      } else {
        const slack = maxWidth - width;
        cost += (slack * slack) / 1000; // Penalización por irregularidad / raggedness
      }
    }

    if (hasWidow) {
      cost += 5000; // Penalización explícita por palabra huérfana
    }

    return cost;
  }
}
