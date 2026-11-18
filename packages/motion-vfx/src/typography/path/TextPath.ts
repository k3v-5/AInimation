import { GlyphPosition, GlyphTransform } from "../types/index.js";

export interface TextPath {
  readonly totalLength: number;
  getPointAt(distance: number): { x: number; y: number };
  getTangentAt(distance: number): { x: number; y: number; angleDegrees: number };
}

/**
 * Trazado lineal simple para texto en línea recta.
 */
export class LinearTextPath implements TextPath {
  public readonly totalLength: number;

  constructor(
    public readonly x1: number,
    public readonly y1: number,
    public readonly x2: number,
    public readonly y2: number
  ) {
    const dx = x2 - x1;
    const dy = y2 - y1;
    this.totalLength = Math.sqrt(dx * dx + dy * dy);
  }

  public getPointAt(distance: number): { x: number; y: number } {
    const t = this.totalLength > 0 ? Math.max(0, Math.min(1, distance / this.totalLength)) : 0;
    return {
      x: this.x1 + (this.x2 - this.x1) * t,
      y: this.y1 + (this.y2 - this.y1) * t,
    };
  }

  public getTangentAt(distance: number): { x: number; y: number; angleDegrees: number } {
    const dx = this.x2 - this.x1;
    const dy = this.y2 - this.y1;
    const angle = (Math.atan2(dy, dx) * 180) / Math.PI;
    return {
      x: this.totalLength > 0 ? dx / this.totalLength : 1,
      y: this.totalLength > 0 ? dy / this.totalLength : 0,
      angleDegrees: angle,
    };
  }
}

/**
 * Trazado circular/arco para texto curvado.
 */
export class ArcTextPath implements TextPath {
  public readonly totalLength: number;

  constructor(
    public readonly centerX: number,
    public readonly centerY: number,
    public readonly radius: number,
    public readonly startAngleDeg: number,
    public readonly sweepAngleDeg: number
  ) {
    this.totalLength = Math.abs((sweepAngleDeg * Math.PI) / 180) * radius;
  }

  public getPointAt(distance: number): { x: number; y: number } {
    const progress = this.totalLength > 0 ? distance / this.totalLength : 0;
    const currentAngleDeg = this.startAngleDeg + this.sweepAngleDeg * progress;
    const rad = (currentAngleDeg * Math.PI) / 180;

    return {
      x: this.centerX + this.radius * Math.cos(rad),
      y: this.centerY + this.radius * Math.sin(rad),
    };
  }

  public getTangentAt(distance: number): { x: number; y: number; angleDegrees: number } {
    const progress = this.totalLength > 0 ? distance / this.totalLength : 0;
    const currentAngleDeg = this.startAngleDeg + this.sweepAngleDeg * progress;
    const tangentAngleDeg = currentAngleDeg + (this.sweepAngleDeg >= 0 ? 90 : -90);
    const rad = (tangentAngleDeg * Math.PI) / 180;

    return {
      x: Math.cos(rad),
      y: Math.sin(rad),
      angleDegrees: tangentAngleDeg,
    };
  }
}

/**
 * Distribuidor de glifos sobre trazados geométricos (Text-On-Path) (Fase 5F).
 */
export class TextPathMapper {
  public static mapGlyphsToPath(
    glyphs: GlyphPosition[],
    path: TextPath,
    startOffset = 0
  ): { position: { x: number; y: number }; rotation: number }[] {
    let accumulatedDistance = startOffset;
    const mapped: { position: { x: number; y: number }; rotation: number }[] = [];

    for (const gp of glyphs) {
      const glyphMidDistance = accumulatedDistance + gp.glyph.advanceX / 2;
      const point = path.getPointAt(glyphMidDistance);
      const tangent = path.getTangentAt(glyphMidDistance);

      mapped.push({
        position: point,
        rotation: tangent.angleDegrees,
      });

      accumulatedDistance += gp.glyph.advanceX;
    }

    return mapped;
  }
}
