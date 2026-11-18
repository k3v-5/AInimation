import { Time } from "../../core/types.js";
import { validatePositiveNumber } from "../../validation/validators.js";
import { AnimationNode } from "../AnimationNode.js";
import { AnimationResult } from "../AnimationResult.js";
import { BaseAnimationOptions } from "../types.js";

export interface DelayNodeOptions extends BaseAnimationOptions {
  duration: Time;
}

/**
 * Nodo de animación que consume una duración temporal sin modificar propiedades.
 */
export class DelayNode extends AnimationNode {
  private _duration: Time;

  constructor(options: DelayNodeOptions) {
    super(options);
    this._duration = validatePositiveNumber(options.duration, "delay.duration");
  }

  public get duration(): Time {
    return this._duration;
  }

  public evaluate(_time: Time): AnimationResult {
    return new AnimationResult();
  }
}
