import { MaskPath, MaskPoint, Vec2 } from "../types/index.js";

/**
 * Utilidades geométricas y Signed Distance Functions (SDF) para evaluación de máscaras (Fase 5G).
 */
export class MaskPathGeometry {
  /**
   * Crea un MaskPath rectangular estándar.
   */
  public static createRectanglePath(x: number, y: number, width: number, height: number): MaskPath {
    return {
      closed: true,
      points: [
        { position: { x, y } },
        { position: { x: x + width, y } },
        { position: { x: x + width, y: y + height } },
        { position: { x, y: y + height } },
      ],
    };
  }

  /**
   * Crea un MaskPath elíptico aproximado con 4 puntos de control Bézier.
   */
  public static createEllipsePath(cx: number, cy: number, rx: number, ry: number): MaskPath {
    const k = 0.552284749831; // Constante kappa para aproximar un círculo mediante 4 curvas cúbicas de Bézier
    const kx = rx * k;
    const ky = ry * k;

    return {
      closed: true,
      points: [
        {
          position: { x: cx, y: cy - ry },
          inTangent: { x: -kx, y: 0 },
          outTangent: { x: kx, y: 0 },
        },
        {
          position: { x: cx + rx, y: cy },
          inTangent: { x: 0, y: -ky },
          outTangent: { x: 0, y: ky },
        },
        {
          position: { x: cx, y: cy + ry },
          inTangent: { x: kx, y: 0 },
          outTangent: { x: -kx, y: 0 },
        },
        {
          position: { x: cx - rx, y: cy },
          inTangent: { x: 0, y: ky },
          outTangent: { x: 0, y: -ky },
        },
      ],
    };
  }

  /**
   * Calcula el cuadro delimitador (bounding box) de un camino.
   */
  public static calculateBounds(path: MaskPath): { minX: number; minY: number; maxX: number; maxY: number } {
    if (path.points.length === 0) {
      return { minX: 0, minY: 0, maxX: 0, maxY: 0 };
    }

    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;

    for (const p of path.points) {
      if (p.position.x < minX) minX = p.position.x;
      if (p.position.x > maxX) maxX = p.position.x;
      if (p.position.y < minY) minY = p.position.y;
      if (p.position.y > maxY) maxY = p.position.y;
    }

    return { minX, minY, maxX, maxY };
  }

  /**
   * Algoritmo Ray-Casting (Even-Odd rule) para determinar si un punto está dentro de un polígono cerrado.
   */
  public static isPointInsidePolygon(point: Vec2, polygon: Vec2[]): boolean {
    let inside = false;
    const n = polygon.length;
    if (n < 3) return false;

    for (let i = 0, j = n - 1; i < n; j = i++) {
      const xi = polygon[i].x,
        yi = polygon[i].y;
      const xj = polygon[j].x,
        yj = polygon[j].y;

      const intersect =
        yi > point.y !== yj > point.y &&
        point.x < ((xj - xi) * (point.y - yi)) / (yj - yi + 1e-10) + xi;

      if (intersect) inside = !inside;
    }

    return inside;
  }

  /**
   * Distancia euclidiana mínima de un punto a un segmento de línea.
   */
  public static distanceToSegment(p: Vec2, a: Vec2, b: Vec2): number {
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const lenSq = dx * dx + dy * dy;

    if (lenSq === 0) {
      const px = p.x - a.x;
      const py = p.y - a.y;
      return Math.sqrt(px * px + py * py);
    }

    let t = ((p.x - a.x) * dx + (p.y - a.y) * dy) / lenSq;
    t = Math.max(0, Math.min(1, t));

    const projX = a.x + t * dx;
    const projY = a.y + t * dy;

    const distX = p.x - projX;
    const distY = p.y - projY;

    return Math.sqrt(distX * distX + distY * distY);
  }

  /**
   * Calcula la distancia con signo (SDF) de un punto a un contorno de polígono.
   * Negativo si está dentro, positivo si está fuera.
   */
  public static signedDistanceToPolygon(point: Vec2, polygon: Vec2[]): number {
    const inside = this.isPointInsidePolygon(point, polygon);
    let minDistance = Infinity;

    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      const dist = this.distanceToSegment(point, polygon[j], polygon[i]);
      if (dist < minDistance) {
        minDistance = dist;
      }
    }

    return inside ? -minDistance : minDistance;
  }
}
