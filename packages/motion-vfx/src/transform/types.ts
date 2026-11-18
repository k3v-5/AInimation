import { Vector2 } from "../core/types.js";

/**
 * Matriz afín 2D en coordenadas homogéneas 3x3:
 * | a  c  tx |
 * | b  d  ty |
 * | 0  0   1 |
 */
export interface Matrix2D {
  readonly a: number;
  readonly b: number;
  readonly c: number;
  readonly d: number;
  readonly tx: number;
  readonly ty: number;
}

/**
 * Dimensiones y límites de un elemento.
 */
export interface Bounds {
  readonly width: number;
  readonly height: number;
}

/**
 * Caja delimitadora rectangular alineada a los ejes.
 */
export interface BoundingBox {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

/**
 * Transformación evaluada en un instante de tiempo.
 */
export interface EvaluatedTransform {
  readonly matrix: Matrix2D;
  readonly opacity: number;
}

/**
 * Interfaz para elementos que participan en jerarquías espaciales con emparentamiento (parenting).
 */
export interface Transformable {
  readonly id: string;
  readonly transform: import("./Transform.js").Transform;
  readonly bounds?: Bounds;
  readonly parent?: Transformable;
}
