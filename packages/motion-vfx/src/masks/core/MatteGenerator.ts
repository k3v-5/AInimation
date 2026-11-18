import { Mask, MaskMode, Matte, Vec2 } from "../types/index.js";
import { MaskPathGeometry } from "./MaskPathGeometry.js";

/**
 * Generador de Mattes y cálculo de alfa mediante Signed Distance Fields (SDF) y Feather (Fase 5G).
 */
export class MatteGenerator {
  /**
   * Función Smoothstep cúbica para difuminado continuo de bordes (Feather).
   */
  public static smoothstep(edge0: number, edge1: number, x: number): number {
    const t = Math.max(0, Math.min(1, (x - edge0) / (edge1 - edge0 + 1e-10)));
    return t * t * (3 - 2 * t);
  }

  /**
   * Genera el Matte rasterizado para una máscara individual.
   */
  public static generateSingleMaskMatte(mask: Mask, width: number, height: number): Matte {
    const alpha = new Float32Array(width * height);
    const polygon = mask.path.points.map((p) => p.position);
    const feather = Math.max(0, mask.feather);
    const expansion = mask.expansion;
    const opacity = Math.max(0, Math.min(1, mask.opacity));

    // Si el polígono tiene menos de 3 puntos, retorna matte vacío (0.0)
    if (polygon.length < 3) {
      return { width, height, alpha };
    }

    const bounds = MaskPathGeometry.calculateBounds(mask.path);
    const margin = feather + Math.abs(expansion) + 2;

    const startX = Math.max(0, Math.floor(bounds.minX - margin));
    const endX = Math.min(width, Math.ceil(bounds.maxX + margin));
    const startY = Math.max(0, Math.floor(bounds.minY - margin));
    const endY = Math.min(height, Math.ceil(bounds.maxY + margin));

    for (let y = startY; y < endY; y++) {
      for (let x = startX; x < endX; x++) {
        const pt: Vec2 = { x, y };
        const signedDist = MaskPathGeometry.signedDistanceToPolygon(pt, polygon);

        // Aplicar expansión (desplaza la distancia de corte)
        const adjustedDist = signedDist - expansion;

        let a = 0.0;
        if (feather <= 0.0) {
          a = adjustedDist <= 0.0 ? 1.0 : 0.0;
        } else {
          // Difuminar entre [-feather/2, +feather/2]
          a = 1.0 - this.smoothstep(-feather / 2, feather / 2, adjustedDist);
        }

        if (mask.inverted) {
          a = 1.0 - a;
        }

        const idx = y * width + x;
        alpha[idx] = a * opacity;
      }
    }

    return { width, height, alpha };
  }

  /**
   * Combina dos canales alfa con la operación booleana especificada.
   */
  public static blendAlpha(a: number, b: number, mode: MaskMode): number {
    switch (mode) {
      case "add":
        return a + b * (1 - a);
      case "subtract":
        return a * (1 - b);
      case "intersect":
        return a * b;
      case "difference":
        return Math.abs(a - b);
    }
  }

  /**
   * Evalúa y combina una pila completa de máscaras para producir el Matte final.
   */
  public static generateCompositeMatte(masks: Mask[], width: number, height: number): Matte {
    const totalPixels = width * height;
    const finalAlpha = new Float32Array(totalPixels);

    if (masks.length === 0) {
      finalAlpha.fill(1.0); // Sin máscaras -> Opacidad completa
      return { width, height, alpha: finalAlpha };
    }

    for (let mIdx = 0; mIdx < masks.length; mIdx++) {
      const mask = masks[mIdx];
      const maskMatte = this.generateSingleMaskMatte(mask, width, height);

      if (mIdx === 0) {
        finalAlpha.set(maskMatte.alpha);
      } else {
        for (let i = 0; i < totalPixels; i++) {
          finalAlpha[i] = this.blendAlpha(finalAlpha[i], maskMatte.alpha[i], mask.mode);
        }
      }
    }

    return { width, height, alpha: finalAlpha };
  }
}
