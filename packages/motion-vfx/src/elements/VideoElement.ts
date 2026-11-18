import { Time } from "../core/types.js";
import { EvaluatedTransform, Matrix2D } from "../transform/index.js";
import { validateId, validateNonNegativeNumber, validateTime } from "../validation/validators.js";
import { BaseElement } from "./BaseElement.js";
import { BaseElementOptions, ElementType, EvaluatedVideoState } from "./types.js";

export interface VideoElementOptions extends BaseElementOptions {
  assetId: string;
  sourceStartTime?: Time;
  speed?: number;
}

/**
 * Elemento de video con mapeo de tiempo fuente, velocidad y soporte de trim.
 */
export class VideoElement extends BaseElement {
  public readonly type: ElementType = "video";
  public assetId: string;
  public sourceStartTime: Time;
  public speed: number;

  constructor(options: VideoElementOptions) {
    super(options);
    this.assetId = validateId(options.assetId, "assetId");
    this.sourceStartTime = options.sourceStartTime !== undefined ? validateTime(options.sourceStartTime) : 0;
    this.speed = options.speed !== undefined ? options.speed : 1.0;
  }

  /**
   * Calcula el instante exacto en el recurso de video fuente (source time) correspondiente a un tiempo global.
   */
  public getSourceTime(globalTime: Time): Time {
    const localTime = this.getLocalTime(globalTime);
    return this.sourceStartTime + (localTime * this.speed);
  }

  public clone(): VideoElement {
    const cloned = new VideoElement({
      name: `${this.name}_copy`,
      startTime: this.startTime,
      duration: this.duration,
      visible: this.visible,
      parentId: this.parentId,
      assetId: this.assetId,
      sourceStartTime: this.sourceStartTime,
    });

    cloned.transform.position.setValue(this.transform.position.getValue());
    cloned.transform.scale.setValue(this.transform.scale.getValue());
    cloned.transform.rotation.setValue(this.transform.rotation.getValue());
    cloned.transform.opacity.setValue(this.transform.opacity.getValue());
    cloned.transform.anchorPoint.setValue(this.transform.anchorPoint.getValue());

    return cloned;
  }

  public evaluate(globalTime: Time, parentTransform?: EvaluatedTransform): EvaluatedVideoState {
    const active = this.isActive(globalTime);
    const localTime = this.getLocalTime(globalTime);
    const sourceTime = this.getSourceTime(globalTime);

    const transformEval = parentTransform
      ? {
          matrix: Matrix2D.multiply(parentTransform.matrix, this.transform.evaluateLocal(globalTime)),
          opacity: parentTransform.opacity * this.transform.evaluateOpacity(globalTime),
        }
      : this.transform.evaluate(globalTime);

    return {
      id: this.id,
      name: this.name,
      type: "video",
      active,
      localTime,
      visible: this.visible,
      assetId: this.assetId,
      sourceTime,
      transform: transformEval,
    };
  }
}
