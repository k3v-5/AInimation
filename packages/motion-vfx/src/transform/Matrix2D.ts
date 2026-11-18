import { Vector2 } from "../core/types.js";
import { BoundingBox, Matrix2D as Matrix2DType } from "./types.js";

export type Matrix2D = Matrix2DType;

/**
 * Operaciones matemáticas puras para matrices afines 2D (3x3 homogéneas).
 */
export const Matrix2D = {
  /**
   * Matriz identidad afín 2D.
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
   * Crea una matriz de escala multiplicativa.
   */
  scale(sx: number, sy: number): Matrix2D {
    return { a: sx, b: 0, c: 0, d: sy, tx: 0, ty: 0 };
  },

  /**
   * Crea una matriz de rotación horaria (clockwise) a partir de grados sexagesimales.
   */
  rotation(degrees: number): Matrix2D {
    const rad = (degrees * Math.PI) / 180;
    const cos = Math.cos(rad);
    const sin = Math.sin(rad);

    // Evitar residuos de punto flotante en ángulos cardinales
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
   * Multiplica dos matrices afines 2D (a x b).
   */
  multiply(a: Matrix2D, b: Matrix2D): Matrix2D {
    return {
      a: a.a * b.a + a.c * b.b,
      b: a.b * b.a + a.d * b.b,
      c: a.a * b.c + a.c * b.d,
      d: a.b * b.c + a.d * b.d,
      tx: a.a * b.tx + a.c * b.ty + a.tx,
      ty: a.b * b.tx + a.d * b.ty + a.ty,
    };
  },

  /**
   * Aplica la transformación matricial a un punto Vector2.
   */
  transformPoint(matrix: Matrix2D, point: Vector2): Vector2 {
    return {
      x: matrix.a * point.x + matrix.c * point.y + matrix.tx,
      y: matrix.b * point.x + matrix.d * point.y + matrix.ty,
    };
  },

  /**
   * Calcula la inversa de una matriz afín 2D.
   * Si la matriz no es invertible (determinante ~ 0), devuelve la identidad.
   */
  inverse(matrix: Matrix2D): Matrix2D {
    const det = matrix.a * matrix.d - matrix.b * matrix.c;
    if (Math.abs(det) < 1e-15) {
      return Matrix2D.identity();
    }
    const invDet = 1 / det;

    return {
      a: matrix.d * invDet,
      b: -matrix.b * invDet,
      c: -matrix.c * invDet,
      d: matrix.a * invDet,
      tx: (matrix.c * matrix.ty - matrix.d * matrix.tx) * invDet,
      ty: (matrix.b * matrix.tx - matrix.a * matrix.ty) * invDet,
    };
  },

  /**
   * Descompone una matriz en traslación, escala y rotación en grados.
   */
  decompose(matrix: Matrix2D): { position: Vector2; scale: Vector2; rotationDeg: number } {
    const tx = matrix.tx;
    const ty = matrix.ty;

    const sx = Math.hypot(matrix.a, matrix.b);
    const sy = Math.hypot(matrix.c, matrix.d);

    const rad = Math.atan2(matrix.b, matrix.a);
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
   * Transforma una caja delimitadora rectangular.
   */
  transformBounds(matrix: Matrix2D, bounds: BoundingBox): BoundingBox {
    const p1 = Matrix2D.transformPoint(matrix, { x: bounds.x, y: bounds.y });
    const p2 = Matrix2D.transformPoint(matrix, { x: bounds.x + bounds.width, y: bounds.y });
    const p3 = Matrix2D.transformPoint(matrix, { x: bounds.x + bounds.width, y: bounds.y + bounds.height });
    const p4 = Matrix2D.transformPoint(matrix, { x: bounds.x, y: bounds.y + bounds.height });

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
