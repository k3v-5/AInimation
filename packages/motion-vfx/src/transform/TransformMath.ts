import { Vector2 } from "../core/types.js";
import { Matrix2D } from "./Matrix2D.js";
import { Bounds } from "./types.js";

/**
 * Fórmulas matemáticas y cálculos de orden de composición espacial para el Transform System.
 */
export const TransformMath = {
  /**
   * Convierte un punto de anclaje normalizado [0, 1] a coordenadas en píxeles según las dimensiones (bounds).
   */
  getAnchorOffset(anchorPoint: Vector2, bounds?: Bounds): Vector2 {
    const w = bounds?.width ?? 0;
    const h = bounds?.height ?? 0;
    return {
      x: anchorPoint.x * w,
      y: anchorPoint.y * h,
    };
  },

  /**
   * Compone la matriz afín local utilizando el orden de transformación estricto:
   * M = T(position) * R(rotation) * S(scale) * T(-anchorOffset)
   *
   * Garantiza que el punto de anclaje del elemento se posicione exactamente en `position`,
   * y que el escalado y la rotación ocurran alrededor de dicho punto de anclaje.
   */
  composeLocalMatrix(
    position: Vector2,
    scale: Vector2,
    rotationDeg: number,
    anchorOffset: Vector2
  ): Matrix2D {
    const tPos = Matrix2D.translation(position.x, position.y);
    const rRot = Matrix2D.rotation(rotationDeg);
    const sScl = Matrix2D.scale(scale.x, scale.y);
    const tAnchorNeg = Matrix2D.translation(-anchorOffset.x, -anchorOffset.y);

    // M = T(pos) * ( R(rot) * ( S(scale) * T(-anchor) ) )
    const mST = Matrix2D.multiply(sScl, tAnchorNeg);
    const mRST = Matrix2D.multiply(rRot, mST);
    return Matrix2D.multiply(tPos, mRST);
  },

  /**
   * Compone la matriz con pivote interno explícito:
   * M = T(position) * T(anchor) * R(rotation) * S(scale) * T(-anchor)
   */
  composeWithExplicitPivot(
    position: Vector2,
    scale: Vector2,
    rotationDeg: number,
    anchorOffset: Vector2
  ): Matrix2D {
    const tPos = Matrix2D.translation(position.x, position.y);
    const tAnchorPos = Matrix2D.translation(anchorOffset.x, anchorOffset.y);
    const rRot = Matrix2D.rotation(rotationDeg);
    const sScl = Matrix2D.scale(scale.x, scale.y);
    const tAnchorNeg = Matrix2D.translation(-anchorOffset.x, -anchorOffset.y);

    const mST = Matrix2D.multiply(sScl, tAnchorNeg);
    const mRST = Matrix2D.multiply(rRot, mST);
    const mTRST = Matrix2D.multiply(tAnchorPos, mRST);
    return Matrix2D.multiply(tPos, mTRST);
  },

  /**
   * Compone la matriz afín local a partir de un punto de anclaje normalizado [0, 1] y los límites del elemento.
   */
  composeFromBounds(
    position: Vector2,
    scale: Vector2,
    rotationDeg: number,
    anchorPoint: Vector2,
    bounds?: Bounds
  ): Matrix2D {
    const anchorOffset = TransformMath.getAnchorOffset(anchorPoint, bounds);
    return TransformMath.composeLocalMatrix(position, scale, rotationDeg, anchorOffset);
  },
};
