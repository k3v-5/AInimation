import { TextCharacterToken, TextLayoutData, TextLineToken, TextWordToken } from "../types/index.js";

/**
 * Segmentador Unicode para texto en motion graphics (Fase 4B).
 * Utiliza Intl.Segmenter para grapheme clusters y descomposición jerárquica de palabras y líneas.
 */
export class TextSegmenter {
  private static graphemeSegmenter = new Intl.Segmenter(undefined, { granularity: "grapheme" });
  private static wordSegmenter = new Intl.Segmenter(undefined, { granularity: "word" });

  /**
   * Segmenta una cadena de texto en caracteres (graphemes), palabras y líneas virtuales.
   */
  public static segment(rawText: string): TextLayoutData {
    const text = rawText ?? "";

    // 1. Descomposición en líneas
    const lineStrings = text.split(/\r\n|\r|\n/);
    const lines: TextLineToken[] = [];
    const words: TextWordToken[] = [];
    const characters: TextCharacterToken[] = [];

    let globalCharIndex = 0;
    let globalWordIndex = 0;
    let globalByteOffset = 0;

    for (let lineIndex = 0; lineIndex < lineStrings.length; lineIndex++) {
      const lineStr = lineStrings[lineIndex];
      const lineWordIndices: number[] = [];
      const lineCharIndices: number[] = [];

      // Segmentar palabras de esta línea
      const wordSegments = Array.from(this.wordSegmenter.segment(lineStr));

      for (const wordSeg of wordSegments) {
        const wordText = wordSeg.segment;
        const isWordLike = wordSeg.isWordLike; // true si es palabra alfanumérica
        const isWhitespaceOnly = /^\s+$/.test(wordText);

        const wordCharIndices: number[] = [];
        const wordStartOffset = globalByteOffset + wordSeg.index;

        // Segmentar graphemes del segmento
        const graphemes = Array.from(this.graphemeSegmenter.segment(wordText));
        for (const g of graphemes) {
          const charToken: TextCharacterToken = {
            index: globalCharIndex,
            grapheme: g.segment,
            isWhitespace: /^\s$/.test(g.segment),
            wordIndex: globalWordIndex,
            lineIndex,
            start: globalByteOffset + wordSeg.index + g.index,
            end: globalByteOffset + wordSeg.index + g.index + g.segment.length,
          };

          characters.push(charToken);
          lineCharIndices.push(globalCharIndex);
          wordCharIndices.push(globalCharIndex);
          globalCharIndex++;
        }

        const wordToken: TextWordToken = {
          index: globalWordIndex,
          text: wordText,
          characterIndices: wordCharIndices,
          lineIndex,
          start: wordStartOffset,
          end: wordStartOffset + wordText.length,
        };

        words.push(wordToken);
        lineWordIndices.push(globalWordIndex);
        globalWordIndex++;
      }

      lines.push({
        index: lineIndex,
        text: lineStr,
        wordIndices: lineWordIndices,
        characterIndices: lineCharIndices,
      });

      globalByteOffset += lineStr.length + 1; // +1 por el separador de nueva línea
    }

    return {
      rawText: text,
      characters,
      words,
      lines,
    };
  }
}
