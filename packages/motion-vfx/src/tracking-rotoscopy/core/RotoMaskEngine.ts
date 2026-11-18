import { RotoMask } from "../types/index.js";

/**
 * Motor de rotoscopia y generación de máscaras alfa para sujetos y objetos (Fase 12).
 */
export class RotoMaskEngine {
  /**
   * Evalúa la opacidad alfa resultante aplicando desvanecimiento (*feather*) e inversión.
   */
  public static evaluateMaskAlpha(
    mask: RotoMask,
    distanceFromEdge: number // Distancia en px (negativa dentro, positiva fuera)
  ): number {
    let alpha = 1.0;

    if (mask.feather <= 0) {
      alpha = distanceFromEdge <= 0 ? 1.0 : 0.0;
    } else {
      // Función sigmoide/lineal de desvanecimiento
      const halfFeather = mask.feather / 2;
      if (distanceFromEdge <= -halfFeather) {
        alpha = 1.0;
      } else if (distanceFromEdge >= halfFeather) {
        alpha = 0.0;
      } else {
        alpha = 0.5 - distanceFromEdge / mask.feather;
      }
    }

    if (mask.invert) {
      alpha = 1.0 - alpha;
    }

    return Math.max(0, Math.min(1.0, alpha * mask.opacity));
  }

  /**
   * Retorna el orden de capas canónico para componer texto detrás de una persona (*Text behind person*).
   */
  public static buildOcclusionLayerOrder(
    backgroundLayerId: string,
    textLayerId: string,
    personCutoutLayerId: string
  ): string[] {
    return [backgroundLayerId, textLayerId, personCutoutLayerId];
  }
}
