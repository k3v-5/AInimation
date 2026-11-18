export interface OCRBoundingBox {
  x: number; // Coordenada X esquina superior izquierda en px
  y: number; // Coordenada Y esquina superior izquierda en px
  width: number; // Ancho en px
  height: number; // Alto en px
}

export interface DetectedTextRegion {
  id: string;
  text: string;
  confidence: number;
  boundingBox: OCRBoundingBox;
  timestamp: number;
}

export interface PlacementSuggestion {
  position: [number, number]; // [x, y] centro sugerido
  zone: "top" | "center" | "bottom";
  hasCollisionRisk: boolean;
}

/**
 * Motor de reconocimiento óptico de caracteres (OCR) y detección de colisiones de texto en video (Fase 6 / Mejoras).
 * Detecta texto visual preexistente (subtítulos quemados, marcas de agua, avisos) para sugerir posiciones
 * libres de colisión para el renderizado tipográfico.
 */
export class VideoOCREngine {
  /**
   * Calcula el coeficiente de intersección sobre unión (IoU) entre dos cajas delimitadoras.
   */
  public static calculateIoU(boxA: OCRBoundingBox, boxB: OCRBoundingBox): number {
    const xLeft = Math.max(boxA.x, boxB.x);
    const yTop = Math.max(boxA.y, boxB.y);
    const xRight = Math.min(boxA.x + boxA.width, boxB.x + boxB.width);
    const yBottom = Math.min(boxA.y + boxA.height, boxB.y + boxB.height);

    if (xRight <= xLeft || yBottom <= yTop) {
      return 0.0;
    }

    const intersectionArea = (xRight - xLeft) * (yBottom - yTop);
    const areaA = boxA.width * boxA.height;
    const areaB = boxB.width * boxB.height;
    const unionArea = areaA + areaB - intersectionArea;

    return unionArea > 0 ? Number((intersectionArea / unionArea).toFixed(4)) : 0.0;
  }

  /**
   * Verifica si una caja delimitadora candidata colisiona con texto preexistente detectado.
   */
  public static hasCollision(
    candidateBox: OCRBoundingBox,
    detectedRegions: DetectedTextRegion[],
    iouThreshold = 0.05
  ): boolean {
    for (const region of detectedRegions) {
      const iou = this.calculateIoU(candidateBox, region.boundingBox);
      if (iou > iouThreshold) {
        return true;
      }
    }
    return false;
  }

  /**
   * Sugiere una posición libre de colisiones (Top, Center, Bottom) en el lienzo de la composición.
   */
  public static suggestSafePlacement(
    detectedRegions: DetectedTextRegion[],
    compWidth: number,
    compHeight: number,
    textDim: { width: number; height: number }
  ): PlacementSuggestion {
    const zones: Array<{ zone: "center" | "top" | "bottom"; box: OCRBoundingBox; pos: [number, number] }> = [
      {
        zone: "center",
        pos: [compWidth / 2, compHeight / 2],
        box: {
          x: compWidth / 2 - textDim.width / 2,
          y: compHeight / 2 - textDim.height / 2,
          width: textDim.width,
          height: textDim.height,
        },
      },
      {
        zone: "top",
        pos: [compWidth / 2, compHeight * 0.22],
        box: {
          x: compWidth / 2 - textDim.width / 2,
          y: compHeight * 0.22 - textDim.height / 2,
          width: textDim.width,
          height: textDim.height,
        },
      },
      {
        zone: "bottom",
        pos: [compWidth / 2, compHeight * 0.78],
        box: {
          x: compWidth / 2 - textDim.width / 2,
          y: compHeight * 0.78 - textDim.height / 2,
          width: textDim.width,
          height: textDim.height,
        },
      },
    ];

    for (const candidate of zones) {
      if (!this.hasCollision(candidate.box, detectedRegions)) {
        return {
          position: candidate.pos,
          zone: candidate.zone,
          hasCollisionRisk: false,
        };
      }
    }

    // Si todas tienen riesgo, retornar top con bandera de colisión
    return {
      position: zones[1].pos,
      zone: zones[1].zone,
      hasCollisionRisk: true,
    };
  }
}
