import { BoundingBox, CompositionAnalysis } from "../types/index.js";

/**
 * Analizador de composición visual, rostros y zonas seguras para subtítulos (Fase 10).
 */
export class CompositionAnalyzer {
  /**
   * Determina la zona más segura para colocar subtítulos sin obstruir rostros o elementos clave.
   */
  public static determineSafeCaptionZone(
    faceBox?: BoundingBox,
    subjectBox?: BoundingBox
  ): "top" | "center" | "bottom" {
    if (faceBox) {
      const faceCenterY = faceBox.y + faceBox.height / 2;
      // Si la cara está en el tercio inferior (y > 0.66), poner subtítulos arriba
      if (faceCenterY > 0.66) return "top";
      // Si la cara está en el tercio superior o medio, poner subtítulos abajo
      return "bottom";
    }

    if (subjectBox) {
      const subjectCenterY = subjectBox.y + subjectBox.height / 2;
      if (subjectCenterY > 0.66) return "top";
      return "bottom";
    }

    return "bottom";
  }

  /**
   * Analiza la composición de una toma y calcula el espacio negativo disponible.
   */
  public static analyzeComposition(
    faceBox?: BoundingBox,
    subjectBox?: BoundingBox,
    dominantColors: string[] = ["#000000"]
  ): CompositionAnalysis {
    let occupiedArea = 0;
    if (faceBox) occupiedArea += faceBox.width * faceBox.height;
    if (subjectBox) occupiedArea += subjectBox.width * subjectBox.height;

    const negativeSpaceArea = Math.max(0, Math.min(1.0, 1.0 - occupiedArea));
    const safeCaptionZone = this.determineSafeCaptionZone(faceBox, subjectBox);

    return {
      faceBox,
      subjectBox,
      negativeSpaceArea,
      dominantColors,
      safeCaptionZone,
    };
  }
}
