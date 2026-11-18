import { ValidationError } from "../../errors/index.js";
import { EffectCategory, EffectParameterSchema, EffectSerialization } from "../types/index.js";
import { BaseEffect } from "./BaseEffect.js";

export type EffectFactory = (options?: any) => BaseEffect;

export interface EffectDescriptor {
  type: string;
  name: string;
  category: EffectCategory;
  description: string;
  parameters: EffectParameterSchema[];
  factory: EffectFactory;
}

/**
 * Registro y fábrica central de tipos de efectos (Fase 4C).
 */
export class EffectRegistry {
  private static descriptors = new Map<string, EffectDescriptor>();

  /**
   * Registra un nuevo tipo de efecto con su esquema de parámetros y función de fábrica.
   */
  public static register(descriptor: EffectDescriptor): void {
    if (!descriptor || !descriptor.type) {
      throw new ValidationError("Effect descriptor requires a non-empty 'type' identifier.");
    }

    if (this.descriptors.has(descriptor.type)) {
      throw new ValidationError(`DUPLICATE_EFFECT_TYPE: Effect type '${descriptor.type}' is already registered.`);
    }

    this.descriptors.set(descriptor.type, descriptor);
  }

  /**
   * Crea e instancia un efecto a partir de su tipo y opciones.
   */
  public static create(type: string, options: Record<string, unknown> = {}): BaseEffect {
    const descriptor = this.descriptors.get(type);
    if (!descriptor) {
      throw new ValidationError(`EFFECT_TYPE_NOT_FOUND: Effect type '${type}' is not registered.`);
    }

    // Validar parámetros contra el esquema
    this.validateParameters(descriptor, options);

    return descriptor.factory(options);
  }

  /**
   * Deserializa un efecto a partir de su representación JSON.
   */
  public static fromJSON(data: EffectSerialization): BaseEffect {
    return this.create(data.type, {
      id: data.id,
      name: data.name,
      enabled: data.enabled,
      blendMode: data.blendMode,
      ...data.params,
    });
  }

  public static has(type: string): boolean {
    return this.descriptors.has(type);
  }

  public static get(type: string): EffectDescriptor {
    const desc = this.descriptors.get(type);
    if (!desc) {
      throw new ValidationError(`EFFECT_TYPE_NOT_FOUND: Effect type '${type}' is not registered.`);
    }
    return desc;
  }

  public static list(): EffectDescriptor[] {
    return Array.from(this.descriptors.values());
  }

  public static clear(): void {
    this.descriptors.clear();
  }

  private static validateParameters(descriptor: EffectDescriptor, options: Record<string, unknown>): void {
    const schemaMap = new Map(descriptor.parameters.map((p) => [p.name, p]));

    for (const [key, val] of Object.entries(options)) {
      // Ignorar metadatos estándar de BaseEffect
      if (key === "id" || key === "name" || key === "enabled" || key === "blendMode") {
        continue;
      }

      const paramSchema = schemaMap.get(key);
      if (!paramSchema) {
        throw new ValidationError(
          `UNKNOWN_EFFECT_PARAMETER: Unknown parameter '${key}' for effect '${descriptor.type}'. Declared parameters are: ${descriptor.parameters.map((p) => p.name).join(", ")}`
        );
      }

      // Si el valor es una constante escalar (no keyframes ni Property), validar tipos y límites
      if (val !== undefined && val !== null && typeof val !== "object") {
        if (paramSchema.type === "number") {
          if (typeof val !== "number" || Number.isNaN(val)) {
            throw new ValidationError(
              `INVALID_PARAMETER_TYPE: Parameter '${key}' on effect '${descriptor.type}' must be a number.`
            );
          }
          if (paramSchema.min !== undefined && val < paramSchema.min) {
            throw new ValidationError(
              `PARAMETER_OUT_OF_RANGE: Parameter '${key}' (${val}) is below minimum (${paramSchema.min}) on effect '${descriptor.type}'.`
            );
          }
          if (paramSchema.max !== undefined && val > paramSchema.max) {
            throw new ValidationError(
              `PARAMETER_OUT_OF_RANGE: Parameter '${key}' (${val}) exceeds maximum (${paramSchema.max}) on effect '${descriptor.type}'.`
            );
          }
        }

        if (paramSchema.type === "enum") {
          if (typeof val !== "string" || (paramSchema.values && !paramSchema.values.includes(val))) {
            throw new ValidationError(
              `INVALID_ENUM_VALUE: Parameter '${key}' on effect '${descriptor.type}' must be one of [${paramSchema.values?.join(", ")}]. Received: '${val}'`
            );
          }
        }
      }
    }
  }
}
