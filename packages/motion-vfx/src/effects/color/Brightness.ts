import { Property } from "../../core/property.js";
import { BaseEffect, BaseEffectOptions } from "../core/BaseEffect.js";
import { EffectCategory } from "../types/index.js";

export interface BrightnessOptions extends BaseEffectOptions {
  amount?: number | Property<number>;
}

/**
 * Efecto de Brillo / Brightness (Fase 4C).
 */
export class Brightness extends BaseEffect {
  public readonly type = "brightness";
  public readonly category: EffectCategory = "color";

  public amount: Property<number>;

  constructor(options: BrightnessOptions = {}) {
    super(options);

    this.amount = this.registerProperty(
      "amount",
      options.amount instanceof Property ? options.amount : new Property<number>(options.amount ?? 1.0)
    );
  }
}
