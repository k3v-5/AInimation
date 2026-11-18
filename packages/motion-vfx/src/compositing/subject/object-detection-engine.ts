import {
  BoundingBox2D,
  BoundingBox2DSchema,
  DetectedSubject,
  DetectedSubjectSchema,
  Point2D,
  Point2DSchema,
} from "./detection-types.js";

/**
 * Motor de detección, filtrado y suavizado espacial de sujetos y objetos (Fase 19).
 */
export class ObjectDetectionEngine {
  /**
   * Calcula el centroide (x, y) de un bounding box 2D.
   */
  public static calculateCentroid(box: BoundingBox2D): Point2D {
    const validated = BoundingBox2DSchema.parse(box);
    return Point2DSchema.parse({
      x: Number((validated.x + validated.width / 2).toFixed(4)),
      y: Number((validated.y + validated.height / 2).toFixed(4)),
    });
  }

  /**
   * Calcula el IoU (Intersection over Union) entre dos BoundingBoxes para tracking o asociación.
   */
  public static calculateIoU(b1: BoundingBox2D, b2: BoundingBox2D): number {
    const v1 = BoundingBox2DSchema.parse(b1);
    const v2 = BoundingBox2DSchema.parse(b2);

    const xA = Math.max(v1.x, v2.x);
    const yA = Math.max(v1.y, v2.y);
    const xB = Math.min(v1.x + v1.width, v2.x + v2.width);
    const yB = Math.min(v1.y + v1.height, v2.y + v2.height);

    const interW = Math.max(0, xB - xA);
    const interH = Math.max(0, yB - yA);
    const interArea = interW * interH;

    const area1 = v1.width * v1.height;
    const area2 = v2.width * v2.height;
    const unionArea = area1 + area2 - interArea;

    if (unionArea <= 0) return 0.0;
    return Number((interArea / unionArea).toFixed(6));
  }

  /**
   * Algoritmo de Ray-Casting para determinar si un punto 2D está contenido dentro de un polígono cerrado.
   */
  public static isPointInPolygon(point: Point2D, polygon: Point2D[]): boolean {
    if (polygon.length < 3) return false;

    let inside = false;
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      const xi = polygon[i].x,
        yi = polygon[i].y;
      const xj = polygon[j].x,
        yj = polygon[j].y;

      const intersect =
        yi > point.y !== yj > point.y &&
        point.x < ((xj - xi) * (point.y - yi)) / (yj - yi + 1e-12) + xi;

      if (intersect) inside = !inside;
    }

    return inside;
  }

  /**
   * Suaviza una secuencia temporal de puntos mediante filtrado exponencial anti-jitter:
   * S_t = alpha * Y_t + (1 - alpha) * S_{t-1}
   */
  public static smoothTrajectory(points: Point2D[], alpha = 0.3): Point2D[] {
    if (points.length === 0) return [];
    const clampedAlpha = Math.max(0.01, Math.min(1.0, alpha));

    const smoothed: Point2D[] = [points[0]];
    for (let i = 1; i < points.length; i++) {
      const prev = smoothed[i - 1];
      const curr = points[i];
      smoothed.push({
        x: Number((clampedAlpha * curr.x + (1 - clampedAlpha) * prev.x).toFixed(4)),
        y: Number((clampedAlpha * curr.y + (1 - clampedAlpha) * prev.y).toFixed(4)),
      });
    }

    return smoothed;
  }

  /**
   * Suaviza temporalmente una secuencia de BoundingBoxes evitando que la máscara parpadee.
   */
  public static smoothBoundingBoxes(boxes: BoundingBox2D[], alpha = 0.3): BoundingBox2D[] {
    if (boxes.length === 0) return [];
    const clampedAlpha = Math.max(0.01, Math.min(1.0, alpha));

    const smoothed: BoundingBox2D[] = [boxes[0]];
    for (let i = 1; i < boxes.length; i++) {
      const prev = smoothed[i - 1];
      const curr = boxes[i];
      smoothed.push({
        x: Number((clampedAlpha * curr.x + (1 - clampedAlpha) * prev.x).toFixed(4)),
        y: Number((clampedAlpha * curr.y + (1 - clampedAlpha) * prev.y).toFixed(4)),
        width: Number((clampedAlpha * curr.width + (1 - clampedAlpha) * prev.width).toFixed(4)),
        height: Number((clampedAlpha * curr.height + (1 - clampedAlpha) * prev.height).toFixed(4)),
      });
    }

    return smoothed;
  }

  /**
   * Genera una detección procedural realista de sujeto (silueta de torso y cabeza) para un ancho/alto dado.
   */
  public static createProceduralPersonDetection(params: {
    frameIndex: number;
    timestampSeconds: number;
    compWidth: number;
    compHeight: number;
    zone?: "LEFT" | "CENTER" | "RIGHT";
    trackId?: string;
  }): DetectedSubject {
    const { frameIndex, timestampSeconds, compWidth, compHeight, zone = "CENTER", trackId = "track_person_1" } = params;

    let centerX = compWidth * 0.5;
    if (zone === "LEFT") centerX = compWidth * 0.28;
    if (zone === "RIGHT") centerX = compWidth * 0.72;

    const width = compWidth * 0.38;
    const height = compHeight * 0.65;
    const x = centerX - width / 2;
    const y = compHeight * 0.35; // Desde el pecho/hombros hacia abajo

    // Contorno poligonal canónico de cabeza y hombros (Bezier vertices)
    const contourPoints: Point2D[] = [
      { x: centerX - width * 0.45, y: y + height }, // Base izquierda
      { x: centerX - width * 0.4, y: y + height * 0.4 }, // Hombro izquierdo
      { x: centerX - width * 0.2, y: y + height * 0.25 }, // Cuello izquierdo
      { x: centerX - width * 0.18, y: y + height * 0.05 }, // Cabeza izquierda
      { x: centerX, y: y }, // Cima cabeza
      { x: centerX + width * 0.18, y: y + height * 0.05 }, // Cabeza derecha
      { x: centerX + width * 0.2, y: y + height * 0.25 }, // Cuello derecho
      { x: centerX + width * 0.4, y: y + height * 0.4 }, // Hombro derecho
      { x: centerX + width * 0.45, y: y + height }, // Base derecha
    ];

    return DetectedSubjectSchema.parse({
      id: `det_${trackId}_${frameIndex}`,
      frameIndex,
      timestampSeconds,
      label: "PERSON",
      confidence: 0.98,
      boundingBox: { x, y, width, height },
      contourPoints,
      trackId,
    });
  }
}
