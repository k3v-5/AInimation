import { getEasing } from "../../animation/easing.js";
import { EasingName } from "../../core/types.js";
import { ValidationError } from "../../errors/index.js";
import { TransitionContext, TransitionParameterSchema, TransitionResult } from "../types/index.js";

export interface TransitionDefinition {
  type: string;
  name: string;
  description: string;
  parameters: TransitionParameterSchema[];
  evaluate: (context: TransitionContext) => TransitionResult;
}

/**
 * Catálogo central y registro de transiciones compositivas (Fase 5C).
 */
export class TransitionRegistry {
  private static definitions = new Map<string, TransitionDefinition>();

  public static register(def: TransitionDefinition): void {
    if (!def || !def.type) {
      throw new ValidationError("Transition definition requires a valid non-empty 'type' identifier.");
    }

    if (this.definitions.has(def.type)) {
      throw new ValidationError(`DUPLICATE_TRANSITION: Transition type '${def.type}' is already registered.`);
    }

    this.definitions.set(def.type, def);
  }

  public static get(type: string): TransitionDefinition {
    const def = this.definitions.get(type);
    if (!def) {
      throw new ValidationError(`TRANSITION_NOT_FOUND: Transition type '${type}' is not registered.`);
    }
    return def;
  }

  public static has(type: string): boolean {
    return this.definitions.has(type);
  }

  public static list(): TransitionDefinition[] {
    return Array.from(this.definitions.values());
  }

  public static clear(): void {
    this.definitions.clear();
  }

  /**
   * Evalúa una transición para un tiempo y progreso dados, aplicando validación de parámetros y easing.
   */
  public static evaluate(
    type: string,
    rawProgress: number,
    time: number,
    duration: number,
    params: Record<string, unknown> = {},
    easing: EasingName = "easeInOut"
  ): TransitionResult {
    const def = this.get(type);

    // 1. Clamping de progreso lineal [0, 1]
    const clampedRaw = Math.max(0, Math.min(1, rawProgress));

    // 2. Modulación por función de easing
    const easingFn = getEasing(easing);
    const progress = easingFn(clampedRaw);

    // 3. Resolución y validación de parámetros con defaults
    const resolvedParams: Record<string, unknown> = {};
    for (const schema of def.parameters) {
      const val = params[schema.name] !== undefined ? params[schema.name] : schema.default;

      if (schema.type === "number" && typeof val === "number") {
        if (schema.min !== undefined && val < schema.min) {
          throw new ValidationError(
            `Parameter '${schema.name}' (${val}) on transition '${type}' is below minimum (${schema.min}).`
          );
        }
        if (schema.max !== undefined && val > schema.max) {
          throw new ValidationError(
            `Parameter '${schema.name}' (${val}) on transition '${type}' exceeds maximum (${schema.max}).`
          );
        }
      }

      if (schema.type === "enum" && schema.values && typeof val === "string") {
        if (!schema.values.includes(val)) {
          throw new ValidationError(
            `Parameter '${schema.name}' on transition '${type}' must be one of [${schema.values.join(", ")}]. Received '${val}'.`
          );
        }
      }

      resolvedParams[schema.name] = val;
    }

    const context: TransitionContext = {
      progress,
      rawProgress: clampedRaw,
      time,
      duration,
      params: resolvedParams,
    };

    return def.evaluate(context);
  }
}
