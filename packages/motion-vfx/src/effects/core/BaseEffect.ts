import { Property } from "../../core/property.js";
import { Time } from "../../core/types.js";
import { BlendMode, EffectCategory, EffectContext, EffectSerialization, EvaluatedEffect } from "../types/index.js";

export interface BaseEffectOptions {
  id?: string;
  name?: string;
  enabled?: boolean;
  blendMode?: BlendMode;
}

/**
 * Clase base abstracta para todos los modificadores visuales y efectos (Fase 4C).
 * Separa formalmente el efecto (representación visual) de las propiedades animadas (Property<T>).
 */
export abstract class BaseEffect {
  public readonly id: string;
  public name: string;
  public abstract readonly type: string;
  public abstract readonly category: EffectCategory;

  public enabled: Property<boolean>;
  public blendMode: BlendMode;
  protected properties = new Map<string, Property<any>>();

  constructor(options: BaseEffectOptions = {}) {
    this.id = options.id ?? `fx_${Math.random().toString(36).substring(2, 9)}`;
    this.name = options.name ?? this.constructor.name;
    this.enabled = new Property<boolean>(options.enabled ?? true);
    this.blendMode = options.blendMode ?? "normal";
  }

  /**
   * Registra una propiedad animable en el efecto.
   */
  protected registerProperty<T>(name: string, property: Property<T>): Property<T> {
    this.properties.set(name, property);
    return property;
  }

  /**
   * Obtiene una propiedad por su nombre para ser animada o inspeccionada.
   */
  public getProperty<T = unknown>(name: string): Property<T> | undefined {
    if (name === "enabled") return this.enabled as any;
    return this.properties.get(name);
  }

  /**
   * Retorna el mapa de todas las propiedades animables registradas.
   */
  public getAllProperties(): Map<string, Property<any>> {
    return new Map(this.properties);
  }

  /**
   * Evalúa el estado del efecto en el tiempo t especificado.
   */
  public evaluate(time: Time, context?: EffectContext): EvaluatedEffect {
    const isEnabled = this.enabled.evaluate(time);
    const params: Record<string, unknown> = {};

    for (const [key, prop] of this.properties.entries()) {
      params[key] = prop.evaluate(time);
    }

    return {
      id: this.id,
      name: this.name,
      type: this.type,
      category: this.category,
      enabled: isEnabled,
      blendMode: this.blendMode,
      params,
    };
  }

  /**
   * Serializa el efecto a formato JSON.
   */
  public toJSON(): EffectSerialization {
    const params: Record<string, unknown> = {};
    for (const [key, prop] of this.properties.entries()) {
      params[key] = this.serializeProperty(prop);
    }

    return {
      id: this.id,
      name: this.name,
      type: this.type,
      enabled: this.serializeProperty(this.enabled),
      blendMode: this.blendMode,
      params,
    };
  }

  private serializeProperty(prop: Property<any>): unknown {
    const keyframes = prop.getKeyframes();
    if (keyframes.length === 0) {
      return prop.getValue();
    }
    return {
      baseValue: prop.getValue(),
      keyframes,
    };
  }
}
