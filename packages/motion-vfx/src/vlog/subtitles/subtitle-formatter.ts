import { SubtitleStyle } from "../contracts/subtitles.types.js";
import { VlogAspectRatio } from "../contracts/vlog.constants.js";

export interface FormattedSubtitleBlock {
  text: string;
  lines: string[];
}

/**
 * Formateador Tipográfico y Segmentador de Subtítulos (Milestone 6-B).
 * Normaliza Unicode NFKC, aplica transformaciones de texto y calcula cortes de línea
 * óptimos respetando las restricciones de aspect ratio (16:9 vs 9:16).
 */
export class SubtitleFormatter {
  /**
   * Obtiene la longitud máxima de caracteres por línea según el ratio de aspecto.
   */
  public static getMaxCharactersPerLine(aspectRatio: VlogAspectRatio = "16:9"): number {
    switch (aspectRatio) {
      case "9:16":
      case "4:5":
        return 26; // Líneas más cortas para lectura vertical cómoda
      case "1:1":
        return 32;
      case "16:9":
      case "21:9":
      default:
        return 38; // Ancho estándar horizontal
    }
  }

  /**
   * Normaliza texto crudo aplicando NFKC y descarte de caracteres de control.
   */
  public static normalizeText(text: string): string {
    if (!text) return "";
    return text
      .normalize("NFKC")
      .replace(/[\u0000-\u001F\u007F-\u009F]/g, "") // Descartar caracteres de control
      .replace(/\s+/g, " ")
      .trim();
  }

  /**
   * Formatea el texto aplicando la transformación del estilo (ej. MAYÚSCULAS en TIME Style).
   */
  public static formatText(text: string, style?: Partial<SubtitleStyle>): string {
    const clean = this.normalizeText(text);
    if (style?.textTransform === "uppercase") {
      return clean.toUpperCase();
    }
    if (style?.textTransform === "lowercase") {
      return clean.toLowerCase();
    }
    return clean;
  }

  /**
   * Divide un conjunto de palabras en líneas legibles sin partir palabras individuales.
   */
  public static wrapWordsIntoLines(
    words: string[],
    aspectRatio: VlogAspectRatio = "16:9"
  ): string[] {
    const maxChars = this.getMaxCharactersPerLine(aspectRatio);
    const lines: string[] = [];
    let currentLine = "";

    for (const word of words) {
      if (!currentLine) {
        currentLine = word;
      } else if ((currentLine + " " + word).length <= maxChars) {
        currentLine += " " + word;
      } else {
        lines.push(currentLine);
        currentLine = word;
      }
    }

    if (currentLine) {
      lines.push(currentLine);
    }

    return lines;
  }
}
