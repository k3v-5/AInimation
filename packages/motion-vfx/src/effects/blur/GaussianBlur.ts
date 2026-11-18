import { Property } from "../../core/property.js";
import { BaseEffect, BaseEffectOptions } from "../core/BaseEffect.js";
import { EffectCategory } from "../types/index.js";

export interface GaussianBlurOptions extends BaseEffectOptions {
  amount?: number | Property<number>;
  quality?: "low" | "medium" | "high" | Property<string>;
}

/**
 * Efecto Gaussian Blur (Fase 4C).
 */
export class GaussianBlur extends BaseEffect {
  public readonly type = "blur";
  public readonly category: EffectCategory = "blur";

  public amount: Property<number>;
  public quality: Property<string>;

  constructor(options: GaussianBlurOptions = {}) {
    super(options);

    this.amount = this.registerProperty(
      "amount",
      options.amount instanceof Property ? options.amount : new Property<number>(options.amount ?? 0)
    );

    this.quality = this.registerProperty(
      "quality",
      options.quality instanceof Property ? options.quality : new Property<string>(options.quality ?? "medium")
    );
  }
}
