import { FontRegistry } from "../fonts/FontRegistry.js";
import { TextShaper } from "../shaping/TextShaper.js";
import {
  GlyphPosition,
  TextBounds,
  TextDocument,
  TextLayoutResult,
  TextLine,
  TextPaint,
  TextStyle,
  WrapMode,
} from "../types/index.js";

export interface TextLayoutConstraints {
  maxWidth?: number;
  maxLines?: number;
  wrapping?: WrapMode;
}

/**
 * Motor de maquetación tipográfica multi-línea con resolución de estilos enriquecidos (Fase 5F).
 */
export class TextLayoutEngine {
  public static calculateLayout(
    doc: TextDocument,
    constraints: TextLayoutConstraints = {}
  ): TextLayoutResult {
    const maxWidth = constraints.maxWidth;
    const wrapping = constraints.wrapping ?? "word";
    const baseStyle = doc.defaultStyle;
    const basePaint = doc.defaultPaint;

    const fontRes = FontRegistry.resolve(baseStyle.fontFamily, baseStyle.fontWeight, baseStyle.fontStyle);
    const lineHeightPx = (baseStyle.lineHeight ?? 1.25) * baseStyle.fontSize;

    // 1. Dividir párrafos por salto de línea explícito
    const paragraphs = doc.content.split("\n");
    const lines: TextLine[] = [];
    const allGlyphPositions: GlyphPosition[] = [];

    let charOffsetGlobal = 0;
    let currentY = 0;

    for (let pIdx = 0; pIdx < paragraphs.length; pIdx++) {
      const paragraphText = paragraphs[pIdx];
      const shaped = TextShaper.shape(paragraphText, baseStyle);

      let currentLineGlyphs: GlyphPosition[] = [];
      let currentLineWidth = 0;

      for (let gIdx = 0; gIdx < shaped.glyphs.length; gIdx++) {
        const glyph = shaped.glyphs[gIdx];
        const charIdx = charOffsetGlobal + gIdx;

        // Resolver estilo y paint específicos según spans aplicados
        let effectiveStyle = { ...baseStyle };
        let effectivePaint = { ...basePaint };

        if (doc.spans) {
          for (const span of doc.spans) {
            if (charIdx >= span.start && charIdx < span.end) {
              if (span.style) effectiveStyle = { ...effectiveStyle, ...span.style };
              if (span.paint) effectivePaint = { ...effectivePaint, ...span.paint };
            }
          }
        }

        const willWrap =
          wrapping !== "none" &&
          maxWidth !== undefined &&
          currentLineWidth + glyph.advanceX > maxWidth &&
          currentLineGlyphs.length > 0;

        if (willWrap) {
          // Si estamos en modo word wrapping y el glifo actual no es un espacio, buscar retroceso hasta el último espacio
          let breakIdx = currentLineGlyphs.length;
          if (wrapping === "word") {
            const lastSpace = currentLineGlyphs.map((gp) => gp.glyph.text).lastIndexOf(" ");
            if (lastSpace !== -1 && lastSpace < currentLineGlyphs.length - 1) {
              breakIdx = lastSpace + 1;
            }
          }

          const lineGlyphs = currentLineGlyphs.slice(0, breakIdx);
          const overflowGlyphs = currentLineGlyphs.slice(breakIdx);

          const lineWidth = lineGlyphs.reduce((sum, g) => sum + g.glyph.advanceX, 0);
          const lineIndex = lines.length;
          const baselineY = currentY + fontRes.metrics.ascent * baseStyle.fontSize;

          lines.push({
            lineIndex,
            text: lineGlyphs.map((g) => g.glyph.text).join(""),
            glyphs: lineGlyphs,
            width: lineWidth,
            height: lineHeightPx,
            baselineY,
          });

          currentY += lineHeightPx;

          // Iniciar nueva línea con los glifos desbordados
          currentLineGlyphs = [...overflowGlyphs];
          currentLineWidth = overflowGlyphs.reduce((sum, g) => sum + g.glyph.advanceX, 0);
        }

        const xPos = currentLineWidth;
        const gp: GlyphPosition = {
          glyph,
          x: xPos,
          y: currentY,
          lineIndex: lines.length,
          charIndex: charIdx,
          style: effectiveStyle,
          paint: effectivePaint,
        };

        currentLineGlyphs.push(gp);
        currentLineWidth += glyph.advanceX;
      }

      if (currentLineGlyphs.length > 0) {
        const lineIndex = lines.length;
        const baselineY = currentY + fontRes.metrics.ascent * baseStyle.fontSize;
        lines.push({
          lineIndex,
          text: currentLineGlyphs.map((g) => g.glyph.text).join(""),
          glyphs: currentLineGlyphs,
          width: currentLineWidth,
          height: lineHeightPx,
          baselineY,
        });
        currentY += lineHeightPx;
      }

      charOffsetGlobal += paragraphText.length + 1; // +1 por el '\n'
    }

    const totalWidth = Math.max(...lines.map((l) => l.width), 0);
    const totalHeight = Math.max(currentY, lineHeightPx);

    // Ajustar alineación horizontal (left, center, right)
    for (const line of lines) {
      let shiftX = 0;
      if (baseStyle.alignment === "center") {
        shiftX = (totalWidth - line.width) / 2;
      } else if (baseStyle.alignment === "right") {
        shiftX = totalWidth - line.width;
      }

      for (const gp of line.glyphs) {
        gp.x += shiftX;
        allGlyphPositions.push(gp);
      }
    }

    // 2. Calcular layoutBounds y visualBounds
    const layoutBounds: TextBounds = {
      x: 0,
      y: 0,
      width: totalWidth,
      height: totalHeight,
    };

    // Calcular expansión visual por trazos, sombras y fondos
    let maxStrokeWidth = 0;
    if (basePaint.strokes) {
      for (const s of basePaint.strokes) {
        if (s.width > maxStrokeWidth) maxStrokeWidth = s.width;
      }
    }

    let shadowExpansionX = 0;
    let shadowExpansionY = 0;
    if (basePaint.shadow) {
      shadowExpansionX = Math.abs(basePaint.shadow.offsetX) + basePaint.shadow.blur;
      shadowExpansionY = Math.abs(basePaint.shadow.offsetY) + basePaint.shadow.blur;
    }

    let bgPadLeft = 0, bgPadRight = 0, bgPadTop = 0, bgPadBottom = 0;
    if (basePaint.background?.padding) {
      bgPadLeft = basePaint.background.padding.left;
      bgPadRight = basePaint.background.padding.right;
      bgPadTop = basePaint.background.padding.top;
      bgPadBottom = basePaint.background.padding.bottom;
    }

    const visualBounds: TextBounds = {
      x: layoutBounds.x - maxStrokeWidth / 2 - bgPadLeft,
      y: layoutBounds.y - maxStrokeWidth / 2 - bgPadTop,
      width: layoutBounds.width + maxStrokeWidth + shadowExpansionX + bgPadLeft + bgPadRight,
      height: layoutBounds.height + maxStrokeWidth + shadowExpansionY + bgPadTop + bgPadBottom,
    };

    return {
      layoutBounds,
      visualBounds,
      lines,
      glyphs: allGlyphPositions,
    };
  }
}
