import { Property } from "../../core/property.js";
import { BaseEffect, BaseEffectOptions } from "../core/BaseEffect.js";
import { EffectCategory } from "../types/index.js";

export interface ContrastOptions extends BaseEffectOptions {
  amount?: number | Property<number>;
}

/**
 * Efecto de Contraste / Contrast (Fase 4C).
 */
export class Contrast extends BaseEffect {
  public readonly type = "contrast";
  public readonly category: EffectCategory = "color";

  public amount: Property<number>;

  constructor(options: ContrastOptions = {}) {
    super(options);

    this.amount = this.registerProperty(
      "amount",
      options.amount instanceof Property ? options.amount : new Property<number>(options.amount ?? 1.0)
    );
  }
}
