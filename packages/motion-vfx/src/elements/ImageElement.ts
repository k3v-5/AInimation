import { Time } from "../core/types.js";
import { EvaluatedTransform, Matrix2D } from "../transform/index.js";
import { validateId } from "../validation/validators.js";
import { BaseElement } from "./BaseElement.js";
import { BaseElementOptions, ElementType, EvaluatedImageState } from "./types.js";

export interface ImageElementOptions extends BaseElementOptions {
  assetId: string;
}

/**
 * Elemento de imagen que referencia un activo del catálogo central.
 */
export class ImageElement extends BaseElement {
  public readonly type: ElementType = "image";
  public assetId: string;

  constructor(options: ImageElementOptions) {
    super(options);
    this.assetId = validateId(options.assetId, "assetId");
  }

  public clone(): ImageElement {
    const cloned = new ImageElement({
      name: `${this.name}_copy`,
      startTime: this.startTime,
      duration: this.duration,
      visible: this.visible,
      parentId: this.parentId,
      assetId: this.assetId,
    });

    cloned.transform.position.setValue(this.transform.position.getValue());
    cloned.transform.scale.setValue(this.transform.scale.getValue());
    cloned.transform.rotation.setValue(this.transform.rotation.getValue());
    cloned.transform.opacity.setValue(this.transform.opacity.getValue());
    cloned.transform.anchorPoint.setValue(this.transform.anchorPoint.getValue());

    return cloned;
  }

  public evaluate(globalTime: Time, parentTransform?: EvaluatedTransform): EvaluatedImageState {
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
      type: "image",
      active,
      localTime,
      visible: this.visible,
      assetId: this.assetId,
      transform: transformEval,
    };
  }
}
