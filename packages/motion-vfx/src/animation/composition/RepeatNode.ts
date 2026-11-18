import { Time } from "../../core/types.js";
import { validatePositiveNumber } from "../../validation/validators.js";
import { AnimationNode } from "../AnimationNode.js";
import { AnimationResult } from "../AnimationResult.js";
import { BaseAnimationOptions } from "../types.js";

export interface RepeatNodeOptions extends BaseAnimationOptions {
  child: AnimationNode;
  count: number;
}

/**
 * Nodo que repite un sub-árbol de animación N veces consecutivas.
 */
export class RepeatNode extends AnimationNode {
  public child: AnimationNode;
  public count: number;

  constructor(options: RepeatNodeOptions) {
    super(options);
    this.child = options.child;
    this.count = validatePositiveNumber(options.count, "repeat.count");
  }

  public get duration(): Time {
    return this.count * this.child.totalDuration;
  }

  public evaluate(time: Time): AnimationResult {
    const localTime = time - this.delay;
    const childTotal = this.child.totalDuration;

    if (childTotal <= 0) {
      return this.child.evaluate(0);
    }

    if (localTime <= 0) {
      return this.child.evaluate(0);
    }

    if (localTime >= this.duration) {
      return this.child.evaluate(childTotal);
    }

    const cycleTime = localTime % childTotal;
    return this.child.evaluate(cycleTime);
  }
}
