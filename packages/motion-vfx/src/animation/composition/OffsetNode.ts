import { Time } from "../../core/types.js";
import { AnimationNode } from "../AnimationNode.js";
import { AnimationResult } from "../AnimationResult.js";
import { BaseAnimationOptions } from "../types.js";

export interface OffsetNodeOptions extends BaseAnimationOptions {
  child: AnimationNode;
  offsetTime: Time;
}

/**
 * Nodo que desplaza temporalmente la ejecución de su sub-árbol hijo (adelanto o retraso relativo).
 */
export class OffsetNode extends AnimationNode {
  public child: AnimationNode;
  public offsetTime: Time;

  constructor(options: OffsetNodeOptions) {
    super(options);
    this.child = options.child;
    this.offsetTime = options.offsetTime;
  }

  public get duration(): Time {
    return Math.max(0, this.child.totalDuration + this.offsetTime);
  }

  public evaluate(time: Time): AnimationResult {
    const localTime = time - this.delay;
    const childEvalTime = localTime - this.offsetTime;
    return this.child.evaluate(childEvalTime);
  }
}
