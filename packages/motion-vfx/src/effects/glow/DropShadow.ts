import { Property } from "../../core/property.js";
import { Color } from "../../core/types.js";
import { BaseEffect, BaseEffectOptions } from "../core/BaseEffect.js";
import { EffectCategory } from "../types/index.js";

export interface DropShadowOptions extends BaseEffectOptions {
  offsetX?: number | Property<number>;
  offsetY?: number | Property<number>;
  blur?: number | Property<number>;
  spread?: number | Property<number>;
  opacity?: number | Property<number>;
  color?: Color | Property<Color>;
}

/**
 * Efecto de Sombra Paralela / Drop Shadow (Fase 4C).
 */
export class DropShadow extends BaseEffect {
  public readonly type = "dropShadow";
  public readonly category: EffectCategory = "shadow";

  public offsetX: Property<number>;
  public offsetY: Property<number>;
  public blur: Property<number>;
  public spread: Property<number>;
  public opacity: Property<number>;
  public color: Property<Color>;

  constructor(options: DropShadowOptions = {}) {
    super(options);

    this.offsetX = this.registerProperty(
      "offsetX",
      options.offsetX instanceof Property ? options.offsetX : new Property<number>(options.offsetX ?? 5)
    );

    this.offsetY = this.registerProperty(
      "offsetY",
      options.offsetY instanceof Property ? options.offsetY : new Property<number>(options.offsetY ?? 5)
    );

    this.blur = this.registerProperty(
      "blur",
      options.blur instanceof Property ? options.blur : new Property<number>(options.blur ?? 10)
    );

    this.spread = this.registerProperty(
      "spread",
      options.spread instanceof Property ? options.spread : new Property<number>(options.spread ?? 0)
    );

    this.opacity = this.registerProperty(
      "opacity",
      options.opacity instanceof Property ? options.opacity : new Property<number>(options.opacity ?? 0.5)
    );

    this.color = this.registerProperty(
      "color",
      options.color instanceof Property
        ? options.color
        : new Property<Color>(options.color ?? { r: 0, g: 0, b: 0, a: 1 })
    );
  }
}
