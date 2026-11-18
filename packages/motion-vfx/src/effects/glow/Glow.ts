import { Property } from "../../core/property.js";
import { Color } from "../../core/types.js";
import { BaseEffect, BaseEffectOptions } from "../core/BaseEffect.js";
import { EffectCategory } from "../types/index.js";

export interface GlowOptions extends BaseEffectOptions {
  radius?: number | Property<number>;
  intensity?: number | Property<number>;
  threshold?: number | Property<number>;
  color?: Color | Property<Color>;
}

/**
 * Efecto de Resplandor / Glow (Fase 4C).
 */
export class Glow extends BaseEffect {
  public readonly type = "glow";
  public readonly category: EffectCategory = "light";

  public radius: Property<number>;
  public intensity: Property<number>;
  public threshold: Property<number>;
  public color: Property<Color>;

  constructor(options: GlowOptions = {}) {
    super(options);

    this.radius = this.registerProperty(
      "radius",
      options.radius instanceof Property ? options.radius : new Property<number>(options.radius ?? 20)
    );

    this.intensity = this.registerProperty(
      "intensity",
      options.intensity instanceof Property ? options.intensity : new Property<number>(options.intensity ?? 1.0)
    );

    this.threshold = this.registerProperty(
      "threshold",
      options.threshold instanceof Property ? options.threshold : new Property<number>(options.threshold ?? 0.5)
    );

    this.color = this.registerProperty(
      "color",
      options.color instanceof Property
        ? options.color
        : new Property<Color>(options.color ?? { r: 1, g: 1, b: 1, a: 1 })
    );
  }
}
