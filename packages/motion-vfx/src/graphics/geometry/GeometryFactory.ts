import { Vec2 } from "../../masks/types/index.js";
import { ArrowGeometry, Geometry, RectangleGeometry, RoundedRectangleGeometry } from "../types/index.js";

/**
 * Fábrica y generador geométrico de primitivas vectoriales (Fase 5J).
 */
export class GeometryFactory {
  /**
   * Genera los vértices del contorno de una flecha 2D.
   */
  public static createArrowPolygon(arrow: ArrowGeometry): Vec2[] {
    const dx = arrow.end.x - arrow.start.x;
    const dy = arrow.end.y - arrow.start.y;
    const length = Math.sqrt(dx * dx + dy * dy);

    if (length === 0) {
      return [{ ...arrow.start }];
    }

    const ux = dx / length;
    const uy = dy / length;
    const px = -uy;
    const py = ux;

    const headLength = Math.min(length, arrow.headLength);
    const halfHeadWidth = arrow.headWidth / 2;
    const halfShaftWidth = arrow.shaftWidth / 2;

    const shaftEnd = {
      x: arrow.start.x + ux * (length - headLength),
      y: arrow.start.y + uy * (length - headLength),
    };

    // 7 vértices del polígono de la flecha
    return [
      // Base inicio eje
      { x: arrow.start.x - px * halfShaftWidth, y: arrow.start.y - py * halfShaftWidth },
      { x: shaftEnd.x - px * halfShaftWidth, y: shaftEnd.y - py * halfShaftWidth },
      // Ala izquierda cabeza
      { x: shaftEnd.x - px * halfHeadWidth, y: shaftEnd.y - py * halfHeadWidth },
      // Punta
      { x: arrow.end.x, y: arrow.end.y },
      // Ala derecha cabeza
      { x: shaftEnd.x + px * halfHeadWidth, y: shaftEnd.y + py * halfHeadWidth },
      { x: shaftEnd.x + px * halfShaftWidth, y: shaftEnd.y + py * halfShaftWidth },
      // Base fin eje
      { x: arrow.start.x + px * halfShaftWidth, y: arrow.start.y + py * halfShaftWidth },
    ];
  }

  /**
   * Calcula el cuadro delimitador (bounding box) de una geometría.
   */
  public static calculateBounds(geometry: Geometry): { width: number; height: number } {
    switch (geometry.type) {
      case "rectangle":
      case "rounded-rectangle":
      case "ellipse":
        return { width: geometry.width, height: geometry.height };
      case "line": {
        const w = Math.abs(geometry.end.x - geometry.start.x);
        const h = Math.abs(geometry.end.y - geometry.start.y);
        return { width: w, height: h };
      }
      case "arrow": {
        const poly = this.createArrowPolygon(geometry);
        let minX = Infinity,
          minY = Infinity,
          maxX = -Infinity,
          maxY = -Infinity;
        for (const p of poly) {
          if (p.x < minX) minX = p.x;
          if (p.x > maxX) maxX = p.x;
          if (p.y < minY) minY = p.y;
          if (p.y > maxY) maxY = p.y;
        }
        return { width: Math.max(0, maxX - minX), height: Math.max(0, maxY - minY) };
      }
      case "polygon": {
        let minX = Infinity,
          minY = Infinity,
          maxX = -Infinity,
          maxY = -Infinity;
        for (const p of geometry.points) {
          if (p.x < minX) minX = p.x;
          if (p.x > maxX) maxX = p.x;
          if (p.y < minY) minY = p.y;
          if (p.y > maxY) maxY = p.y;
        }
        return { width: Math.max(0, maxX - minX), height: Math.max(0, maxY - minY) };
      }
    }
  }

  /**
   * Sujeta el radio de curvatura de un rectángulo redondeado para no exceder las dimensiones.
   */
  public static sanitizeRoundedRectangle(geom: RoundedRectangleGeometry): RoundedRectangleGeometry {
    const maxRadius = Math.min(geom.width, geom.height) / 2;
    return {
      ...geom,
      radius: Math.max(0, Math.min(geom.radius, maxRadius)),
    };
  }
}
