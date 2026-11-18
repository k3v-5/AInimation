import { KineticTextSegment, StaggerDirection } from "../types/index.js";

/**
 * Motor tipográfico cinético avanzado con staggers y resaltado de palabras (Fase 11).
 */
export class KineticTypographyEngine {
  /**
   * Segmenta una frase en palabras y calcula los staggers y estilos cinéticos.
   */
  public static segmentText(
    text: string,
    options: {
      staggerDelay?: number;
      segmentDuration?: number;
      direction?: StaggerDirection;
      emphasizedWords?: string[];
      highlightColor?: string;
    } = {}
  ): KineticTextSegment[] {
    const words = text.trim().split(/\s+/);
    const staggerDelay = options.staggerDelay ?? 0.08;
    const segmentDuration = options.segmentDuration ?? 0.35;
    const direction = options.direction ?? "forward";
    const emphasized = (options.emphasizedWords ?? []).map((w) => w.toLowerCase());
    const count = words.length;

    return words.map((word, i) => {
      let delayIndex = i;
      if (direction === "reverse") {
        delayIndex = count - 1 - i;
      } else if (direction === "center") {
        const center = (count - 1) / 2;
        delayIndex = Math.abs(i - center);
      }

      const isEmphasized = emphasized.includes(word.toLowerCase().replace(/[^a-záéíóúüñ0-9]/gi, ""));

      return {
        text: word,
        index: i,
        startDelay: delayIndex * staggerDelay,
        duration: segmentDuration,
        isEmphasized,
        scale: isEmphasized ? 1.25 : 1.0,
        color: isEmphasized ? options.highlightColor ?? "#ffeb3b" : undefined,
        glow: isEmphasized,
      };
    });
  }
}
