import { Property } from "../core/property.js";
import { Time, Vector2 } from "../core/types.js";
import { Matrix2D } from "./Matrix2D.js";
import { TransformMath } from "./TransformMath.js";
import { Bounds, EvaluatedTransform } from "./types.js";

export interface TransformOptions {
  position?: Vector2;
  scale?: Vector2;
  rotation?: number;
  opacity?: number;
  anchorPoint?: Vector2;
}

/**
 * Representación de propiedades espaciales y de opacidad de un elemento animable.
 */
export class Transform {
  public position: Property<Vector2>;
  public scale: Property<Vector2>;
  public rotation: Property<number>;
  public opacity: Property<number>;
  public anchorPoint: Property<Vector2>;

  constructor(options: TransformOptions = {}) {
    this.position = new Property<Vector2>(options.position ?? { x: 0, y: 0 });
    this.scale = new Property<Vector2>(options.scale ?? { x: 1, y: 1 });
    this.rotation = new Property<number>(options.rotation ?? 0);
    this.opacity = new Property<number>(options.opacity ?? 1);
    this.anchorPoint = new Property<Vector2>(options.anchorPoint ?? { x: 0.5, y: 0.5 });
  }

  /**
   * Evalúa la matriz local del elemento en el tiempo indicado.
   */
  public evaluateLocal(time: Time, bounds?: Bounds): Matrix2D {
    const pos = this.position.evaluate(time);
    const scl = this.scale.evaluate(time);
    const rot = this.rotation.evaluate(time);
    const anc = this.anchorPoint.evaluate(time);

    return TransformMath.composeFromBounds(pos, scl, rot, anc, bounds);
  }

  /**
   * Evalúa la opacidad local del elemento [0.0, 1.0].
   */
  public evaluateOpacity(time: Time): number {
    const opc = this.opacity.evaluate(time);
    return Math.max(0, Math.min(1, opc));
  }

  /**
   * Evalúa tanto la matriz como la opacidad en un único resultado EvaluatedTransform.
   */
  public evaluate(time: Time, bounds?: Bounds): EvaluatedTransform {
    return {
      matrix: this.evaluateLocal(time, bounds),
      opacity: this.evaluateOpacity(time),
    };
  }

  public toJSON(): any {
    return {
      position: this.position.evaluate(0),
      scale: this.scale.evaluate(0),
      rotation: this.rotation.evaluate(0),
      opacity: this.opacity.evaluate(0),
      anchorPoint: this.anchorPoint.evaluate(0),
    };
  }

  public static fromJSON(data: any): Transform {
    return new Transform({
      position: data.position,
      scale: data.scale,
      rotation: data.rotation,
      opacity: data.opacity,
      anchorPoint: data.anchorPoint,
    });
  }
}
