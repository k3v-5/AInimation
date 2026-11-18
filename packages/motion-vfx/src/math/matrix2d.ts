import { Vector2 } from "../core/types.js";

/**
 * Matriz de transformación afín 2D en coordenadas homogéneas 3x3:
 * | a  c  tx |
 * | b  d  ty |
 * | 0  0   1 |
 */
export interface Matrix2D {
  a: number;
  b: number;
  c: number;
  d: number;
  tx: number;
  ty: number;
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface DecomposedTransform {
  position: Vector2;
  scale: Vector2;
  rotationDeg: number;
}

export const Matrix2D = {
  /**
   * Matriz identidad.
   */
  identity(): Matrix2D {
    return { a: 1, b: 0, c: 0, d: 1, tx: 0, ty: 0 };
  },

  /**
   * Crea una matriz de traslación.
   */
  translation(tx: number, ty: number): Matrix2D {
    return { a: 1, b: 0, c: 0, d: 1, tx, ty };
  },

  /**
   * Crea una matriz de rotación a partir de un ángulo en grados (clockwise).
   */
  rotation(degrees: number): Matrix2D {
    const rad = (degrees * Math.PI) / 180;
    const cos = Math.cos(rad);
    const sin = Math.sin(rad);
    // Limpieza de pequeños errores de punto flotante en ángulos cardinales
    const cleanCos = Math.abs(cos) < 1e-15 ? 0 : cos;
    const cleanSin = Math.abs(sin) < 1e-15 ? 0 : sin;

    return {
      a: cleanCos,
      b: cleanSin,
      c: -cleanSin,
      d: cleanCos,
      tx: 0,
      ty: 0,
    };
  },

  /**
   * Crea una matriz de escala multiplicativa.
   */
  scale(sx: number, sy: number): Matrix2D {
    return { a: sx, b: 0, c: 0, d: sy, tx: 0, ty: 0 };
  },

  /**
   * Multiplica dos matrices afines 2D (m1 x m2).
   */
  multiply(m1: Matrix2D, m2: Matrix2D): Matrix2D {
    return {
      a: m1.a * m2.a + m1.c * m2.b,
      b: m1.b * m2.a + m1.d * m2.b,
      c: m1.a * m2.c + m1.c * m2.d,
      d: m1.b * m2.c + m1.d * m2.d,
      tx: m1.a * m2.tx + m1.c * m2.ty + m1.tx,
      ty: m1.b * m2.tx + m1.d * m2.ty + m1.ty,
    };
  },

  /**
   * Aplica la matriz de transformación a un punto Vector2.
   */
  transformPoint(m: Matrix2D, p: Vector2): Vector2 {
    return {
      x: m.a * p.x + m.c * p.y + m.tx,
      y: m.b * p.x + m.d * p.y + m.ty,
    };
  },

  /**
   * Inversa de una matriz afín 2D.
   */
  invert(m: Matrix2D): Matrix2D {
    const det = m.a * m.d - m.b * m.c;
    if (Math.abs(det) < 1e-15) {
      return Matrix2D.identity();
    }
    const invDet = 1 / det;

    return {
      a: m.d * invDet,
      b: -m.b * invDet,
      c: -m.c * invDet,
      d: m.a * invDet,
      tx: (m.c * m.ty - m.d * m.tx) * invDet,
      ty: (m.b * m.tx - m.a * m.ty) * invDet,
    };
  },

  /**
   * Transforma un punto del espacio mundial al espacio local (usando la inversa de m).
   */
  inverseTransformPoint(m: Matrix2D, p: Vector2): Vector2 {
    const inv = Matrix2D.invert(m);
    return Matrix2D.transformPoint(inv, p);
  },

  /**
   * Compone la matriz afín local combinando Traslación, Rotación y Escala.
   * Si anchorOffset es proporcionado, se aplica como pivot:
   * M = T(pos) * R(rot) * S(scale) * T(-anchorOffset)
   */
  compose(position: Vector2, scale: Vector2, rotationDeg: number, anchorOffset: Vector2 = { x: 0, y: 0 }): Matrix2D {
    const tPos = Matrix2D.translation(position.x, position.y);
    const rDeg = Matrix2D.rotation(rotationDeg);
    const sVec = Matrix2D.scale(scale.x, scale.y);
    const tAnchorInv = Matrix2D.translation(-anchorOffset.x, -anchorOffset.y);

    const mRS = Matrix2D.multiply(rDeg, sVec);
    const mTRS = Matrix2D.multiply(tPos, mRS);
    return Matrix2D.multiply(mTRS, tAnchorInv);
  },

  /**
   * Compone la matriz afín usando coordenadas de anchorPoint normalizadas [0, 1] y dimensiones de caja.
   */
  composeWithNormalizedAnchor(
    position: Vector2,
    scale: Vector2,
    rotationDeg: number,
    anchorPoint: Vector2,
    dimensions?: { width: number; height: number }
  ): Matrix2D {
    const w = dimensions?.width ?? 0;
    const h = dimensions?.height ?? 0;
    const anchorOffset: Vector2 = {
      x: anchorPoint.x * w,
      y: anchorPoint.y * h,
    };
    return Matrix2D.compose(position, scale, rotationDeg, anchorOffset);
  },

  /**
   * Descompone una matriz afín 2D en sus componentes primitivos (posición, escala, rotación).
   */
  decompose(m: Matrix2D): DecomposedTransform {
    const tx = m.tx;
    const ty = m.ty;

    const sx = Math.hypot(m.a, m.b);
    const sy = Math.hypot(m.c, m.d);

    const rad = Math.atan2(m.b, m.a);
    let rotationDeg = (rad * 180) / Math.PI;
    if (rotationDeg < 0) {
      rotationDeg += 360;
    }

    return {
      position: { x: tx, y: ty },
      scale: { x: sx, y: sy },
      rotationDeg,
    };
  },

  /**
   * Transforma una caja delimitadora (Bounding Box) mediante la matriz afín.
   */
  transformBounds(m: Matrix2D, bounds: BoundingBox): BoundingBox {
    const p1 = Matrix2D.transformPoint(m, { x: bounds.x, y: bounds.y });
    const p2 = Matrix2D.transformPoint(m, { x: bounds.x + bounds.width, y: bounds.y });
    const p3 = Matrix2D.transformPoint(m, { x: bounds.x + bounds.width, y: bounds.y + bounds.height });
    const p4 = Matrix2D.transformPoint(m, { x: bounds.x, y: bounds.y + bounds.height });

    const minX = Math.min(p1.x, p2.x, p3.x, p4.x);
    const maxX = Math.max(p1.x, p2.x, p3.x, p4.x);
    const minY = Math.min(p1.y, p2.y, p3.y, p4.y);
    const maxY = Math.max(p1.y, p2.y, p3.y, p4.y);

    return {
      x: minX,
      y: minY,
      width: maxX - minX,
      height: maxY - minY,
    };
  },
};
