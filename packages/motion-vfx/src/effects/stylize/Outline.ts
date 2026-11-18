import { Property } from "../../core/property.js";
import { Color } from "../../core/types.js";
import { BaseEffect, BaseEffectOptions } from "../core/BaseEffect.js";
import { EffectCategory } from "../types/index.js";

export interface OutlineOptions extends BaseEffectOptions {
  width?: number | Property<number>;
  opacity?: number | Property<number>;
  color?: Color | Property<Color>;
}

/**
 * Efecto de Contorno / Outline (Fase 4C).
 */
export class Outline extends BaseEffect {
  public readonly type = "outline";
  public readonly category: EffectCategory = "stylization";

  public width: Property<number>;
  public opacity: Property<number>;
  public color: Property<Color>;

  constructor(options: OutlineOptions = {}) {
    super(options);

    this.width = this.registerProperty(
      "width",
      options.width instanceof Property ? options.width : new Property<number>(options.width ?? 2)
    );

    this.opacity = this.registerProperty(
      "opacity",
      options.opacity instanceof Property ? options.opacity : new Property<number>(options.opacity ?? 1.0)
    );

    this.color = this.registerProperty(
      "color",
      options.color instanceof Property
        ? options.color
        : new Property<Color>(options.color ?? { r: 0, g: 0, b: 0, a: 1 })
    );
  }
}
