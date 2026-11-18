import { Glyph, ShapedText, TextStyle } from "../types/index.js";

/**
 * Conformador de texto (Text Shaper) y extractor de glifos y ligaduras Unicode (Fase 5F).
 */
export class TextShaper {
  private static segmenter =
    typeof Intl !== "undefined" && (Intl as any).Segmenter
      ? new (Intl as any).Segmenter("en", { granularity: "grapheme" })
      : null;

  /**
   * Divide el texto en clusters de grafemas Unicode independientes.
   */
  public static splitGraphemes(text: string): string[] {
    if (!text) return [];
    if (this.segmenter) {
      const segments = this.segmenter.segment(text);
      const result: string[] = [];
      for (const seg of segments) {
        result.push(seg.segment);
      }
      return result;
    }
    // Fallback con iterador de string (soporta surrogate pairs)
    return Array.from(text);
  }

  /**
   * Conforma una cadena de texto en glifos posicionados con cálculo de avances y ligaduras.
   */
  public static shape(text: string, style: TextStyle): ShapedText {
    const fontSize = style.fontSize;
    const tracking = style.letterSpacing ?? 0;
    const graphemes = this.splitGraphemes(text);

    const glyphs: Glyph[] = [];
    let currentX = 0;
    let clusterIndex = 0;

    for (let i = 0; i < graphemes.length; i++) {
      const g = graphemes[i];

      // Detección de ligaduras estándar (fi, ffi, fl)
      let glyphText = g;
      let advanceMultiplier = 0.55; // Factor proporcional estándar

      if (g === "f" && i + 1 < graphemes.length && graphemes[i + 1] === "i") {
        glyphText = "fi";
        advanceMultiplier = 0.75;
        i++; // Consumir siguiente carácter
      } else if (g === " " || g === "\t") {
        advanceMultiplier = 0.28;
      } else if (/[WMmw@]/.test(g)) {
        advanceMultiplier = 0.85;
      } else if (/[ijl1.,:;'!]/.test(g)) {
        advanceMultiplier = 0.28;
      } else if (/\p{Emoji}/u.test(g)) {
        advanceMultiplier = 1.0;
      }

      const advanceX = fontSize * advanceMultiplier + tracking;

      glyphs.push({
        id: clusterIndex,
        text: glyphText,
        cluster: clusterIndex,
        advanceX,
        offsetX: 0,
        offsetY: 0,
      });

      currentX += advanceX;
      clusterIndex++;
    }

    return {
      glyphs,
      totalAdvance: currentX,
    };
  }
}
