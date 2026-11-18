import { Composition } from "../../core/composition.js";

export class ThumbnailScorer {
  /**
   * Evalúa el potencial de impacto de un fotograma para ser seleccionado como miniatura/portada.
   * Pondera presencia de texto legible, densidad visual y dinamismo temporal.
   */
  public static scoreFrame(comp: Composition, timeSeconds: number): number {
    const snapshot = comp.evaluate(timeSeconds);
    const elements = snapshot?.elements ?? [];

    if (elements.length === 0) return 0;

    let textScore = 0;
    let visualScore = 0;

    for (const el of elements) {
      if (el.type === "text" || el.name?.toLowerCase().includes("title") || el.name?.toLowerCase().includes("caption")) {
        textScore = 0.6; // presencia garantizada de texto
      } else {
        visualScore += 0.1;
      }
    }

    const totalScore = Math.min(1.0, textScore + Math.min(0.4, visualScore * 0.4));
    return Math.round(totalScore * 100) / 100;
  }
}
