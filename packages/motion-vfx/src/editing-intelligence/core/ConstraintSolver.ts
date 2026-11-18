import { BoundingBox } from "../../asset-library/types/index.js";

/**
 * Resolvedor de restricciones espaciales y temporales (*Constraint Solver*) (Fase 14).
 */
export class ConstraintSolver {
  /**
   * Resuelve la posición de subtítulos para evitar colisión con el rostro detectado.
   */
  public static resolveCaptionPlacement(
    faceBox?: BoundingBox,
    defaultPlacement: "top" | "bottom" = "bottom"
  ): "top" | "bottom" {
    if (!faceBox) return defaultPlacement;

    // Si el rostro está en el tercio inferior (y > 0.60) y el default es bottom, mover a top
    if (faceBox.y > 0.60 && defaultPlacement === "bottom") {
      return "top";
    }

    // Si el rostro está en el tercio superior (y < 0.40) y el default es top, mover a bottom
    if (faceBox.y < 0.40 && defaultPlacement === "top") {
      return "bottom";
    }

    return defaultPlacement;
  }

  /**
   * Ajusta un evento de audio para que caiga dentro de la ventana de tolerancia temporal (±100ms) del evento visual.
   */
  public static snapAudioToVisual(
    visualTime: number,
    rawAudioTime: number,
    tolerance = 0.1
  ): number {
    if (Math.abs(visualTime - rawAudioTime) <= tolerance) {
      return visualTime; // Alinear exactamente al evento visual
    }
    return rawAudioTime;
  }
}
