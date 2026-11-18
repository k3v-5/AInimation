import { Time } from "../core/types.js";
import { EvaluatedTransform, Matrix2D } from "../transform/index.js";
import { BaseElement } from "./BaseElement.js";
import { BaseElementOptions, ElementType, EvaluatedShapeState, ShapeData, ShapeStyle, ShapeType } from "./types.js";

export interface ShapeElementOptions extends BaseElementOptions {
  shapeType: ShapeType;
  shapeData?: ShapeData;
  style?: ShapeStyle;
}

/**
 * Elemento de forma vectorial geométrica (rectángulos, elipses, líneas).
 */
export class ShapeElement extends BaseElement {
  public readonly type: ElementType = "shape";
  public shapeType: ShapeType;
  public shapeData: ShapeData;
  public style: ShapeStyle;

  constructor(options: ShapeElementOptions) {
    super(options);
    this.shapeType = options.shapeType;
    this.shapeData = options.shapeData ?? this.getDefaultShapeData(options.shapeType);
    this.style = {
      fill: options.style?.fill ? { ...options.style.fill } : undefined,
      stroke: options.style?.stroke ? { ...options.style.stroke } : undefined,
      strokeWidth: options.style?.strokeWidth ?? 0,
    };
  }

  private getDefaultShapeData(type: ShapeType): ShapeData {
    switch (type) {
      case "rectangle":
        return { width: 100, height: 100, cornerRadius: 0 };
      case "ellipse":
        return { radiusX: 50, radiusY: 50 };
      case "line":
        return { endPoint: { x: 100, y: 100 } };
    }
  }

  public clone(): ShapeElement {
    const cloned = new ShapeElement({
      name: `${this.name}_copy`,
      startTime: this.startTime,
      duration: this.duration,
      visible: this.visible,
      parentId: this.parentId,
      shapeType: this.shapeType,
      shapeData: JSON.parse(JSON.stringify(this.shapeData)),
      style: {
        fill: this.style.fill ? { ...this.style.fill } : undefined,
        stroke: this.style.stroke ? { ...this.style.stroke } : undefined,
        strokeWidth: this.style.strokeWidth,
      },
    });

    cloned.transform.position.setValue(this.transform.position.getValue());
    cloned.transform.scale.setValue(this.transform.scale.getValue());
    cloned.transform.rotation.setValue(this.transform.rotation.getValue());
    cloned.transform.opacity.setValue(this.transform.opacity.getValue());
    cloned.transform.anchorPoint.setValue(this.transform.anchorPoint.getValue());

    return cloned;
  }

  public evaluate(globalTime: Time, parentTransform?: EvaluatedTransform): EvaluatedShapeState {
    const active = this.isActive(globalTime);
    const localTime = this.getLocalTime(globalTime);

    const transformEval = parentTransform
      ? {
          matrix: Matrix2D.multiply(parentTransform.matrix, this.transform.evaluateLocal(globalTime)),
          opacity: parentTransform.opacity * this.transform.evaluateOpacity(globalTime),
        }
      : this.transform.evaluate(globalTime);

    return {
      id: this.id,
      name: this.name,
      type: "shape",
      active,
      localTime,
      visible: this.visible,
      shapeType: this.shapeType,
      shapeData: JSON.parse(JSON.stringify(this.shapeData)),
      style: {
        fill: this.style.fill ? { ...this.style.fill } : undefined,
        stroke: this.style.stroke ? { ...this.style.stroke } : undefined,
        strokeWidth: this.style.strokeWidth,
      },
      transform: transformEval,
    };
  }
}
