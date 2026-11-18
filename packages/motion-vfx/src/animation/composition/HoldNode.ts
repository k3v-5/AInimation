import { Time } from "../../core/types.js";
import { validatePositiveNumber } from "../../validation/validators.js";
import { AnimationNode } from "../AnimationNode.js";
import { AnimationResult } from "../AnimationResult.js";
import { BaseAnimationOptions } from "../types.js";

export interface HoldNodeOptions extends BaseAnimationOptions {
  duration: Time;
}

/**
 * Nodo semántico para retener el estado de una animación en una secuencia durante un período de tiempo.
 */
export class HoldNode extends AnimationNode {
  private _duration: Time;

  constructor(options: HoldNodeOptions) {
    super(options);
    this._duration = validatePositiveNumber(options.duration, "hold.duration");
  }

  public get duration(): Time {
    return this._duration;
  }

  public evaluate(_time: Time): AnimationResult {
    return new AnimationResult();
  }
}
