import { Caption, CaptionLayoutResult, CaptionLine, PositionedWord } from "../types/index.js";

/**
 * Motor de layout tipográfico para cálculo de líneas, anchos y cajas de palabras (Fase 5E).
 */
export class CaptionLayoutEngine {
  /**
   * Mide el ancho estimado de una palabra en función del tamaño de fuente.
   */
  public static measureWordWidth(text: string, fontSize: number): number {
    const avgCharWidth = fontSize * 0.55;
    return text.length * avgCharWidth;
  }

  public static calculateLayout(caption: Caption, maxWidth = 900): CaptionLayoutResult {
    const fontSize = caption.style.fontSize;
    const spaceWidth = fontSize * 0.3;
    const lineHeight = fontSize * 1.25;

    const lines: CaptionLine[] = [];
    let currentLineWords: PositionedWord[] = [];
    let currentLineWidth = 0;
    let lineIndex = 0;

    for (let i = 0; i < caption.words.length; i++) {
      const word = caption.words[i];
      const wordWidth = this.measureWordWidth(word.text, fontSize);

      const willExceed =
        currentLineWords.length > 0 && currentLineWidth + spaceWidth + wordWidth > maxWidth;

      if (willExceed) {
        // Guardar línea actual
        lines.push({
          lineIndex,
          text: currentLineWords.map((w) => w.text).join(" "),
          words: [...currentLineWords],
          width: currentLineWidth,
          height: lineHeight,
          x: 0,
          y: lineIndex * lineHeight,
        });

        currentLineWords = [];
        currentLineWidth = 0;
        lineIndex++;
      }

      const xOffset = currentLineWidth > 0 ? currentLineWidth + spaceWidth : 0;
      currentLineWords.push({
        id: word.id,
        text: word.text,
        start: word.start,
        end: word.end,
        index: i,
        x: xOffset,
        y: lineIndex * lineHeight,
        width: wordWidth,
        height: fontSize,
        line: lineIndex,
        styleOverride: word.styleOverride,
      });

      currentLineWidth += (currentLineWidth > 0 ? spaceWidth : 0) + wordWidth;
    }

    if (currentLineWords.length > 0) {
      lines.push({
        lineIndex,
        text: currentLineWords.map((w) => w.text).join(" "),
        words: [...currentLineWords],
        width: currentLineWidth,
        height: lineHeight,
        x: 0,
        y: lineIndex * lineHeight,
      });
    }

    const totalHeight = lines.length * lineHeight;
    const maxLineWidth = Math.max(...lines.map((l) => l.width), 0);

    // Ajustar alineación horizontal en cada línea (left, center, right)
    const allPositionedWords: PositionedWord[] = [];
    for (const line of lines) {
      let lineShiftX = 0;
      if (caption.style.alignment === "center") {
        lineShiftX = (maxLineWidth - line.width) / 2;
      } else if (caption.style.alignment === "right") {
        lineShiftX = maxLineWidth - line.width;
      }

      line.x = lineShiftX;

      for (const word of line.words) {
        word.x += lineShiftX;
        allPositionedWords.push(word);
      }
    }

    return {
      width: maxLineWidth,
      height: totalHeight,
      x: 0,
      y: 0,
      lines,
      words: allPositionedWords,
      backgrounds: [],
      overflowStatus: "none",
      diagnostics: [],
    };
  }
}
