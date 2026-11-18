import { AnimationNode } from "../../animation/AnimationNode.js";
import { ValidationError } from "../../errors/index.js";
import { BaseElement } from "../../elements/BaseElement.js";
import { ElementType } from "../../elements/types.js";
import { PresetContext, PresetDefinition } from "../schema/types.js";
import { PresetRegistry } from "./registry.js";

/**
 * Resolver determinista para validar parámetros, expandir y construir árboles de animación a partir de presets.
 */
export class PresetResolver {
  /**
   * Resuelve y expande un preset por su ID sobre un elemento destino y con overrides opcionales.
   */
  public static resolve(
    presetId: string,
    target: BaseElement | { id: string; type?: ElementType },
    overrides: Record<string, unknown> = {},
    callStack: string[] = []
  ): AnimationNode {
    // 1. Detección de ciclos de dependencia entre presets
    if (callStack.includes(presetId)) {
      const cycle = [...callStack, presetId].join(" -> ");
      throw new ValidationError(`CIRCULAR_PRESET_DEPENDENCY: Circular dependency detected in preset resolution: ${cycle}`);
    }

    const preset = PresetRegistry.get(presetId);

    // 2. Comprobar compatibilidad con el tipo de elemento
    const targetType = "type" in target ? (target as any).type : undefined;
    if (targetType && preset.compatibleWith && !preset.compatibleWith.includes(targetType as any)) {
      throw new ValidationError(
        `INCOMPATIBLE_PRESET_TARGET: Preset '${preset.id}' is not compatible with element type '${targetType}'. Expected one of: ${preset.compatibleWith.join(", ")}`
      );
    }

    // 3. Validar y fusionar parámetros (defaults + overrides)
    const resolvedParams = this.validateAndMergeParameters(preset, overrides);

    const context: PresetContext = {
      target,
      parameters: resolvedParams,
    };

    // 4. Construir el árbol de animación
    return preset.build(context);
  }

  private static validateAndMergeParameters(
    preset: PresetDefinition,
    overrides: Record<string, unknown>
  ): Record<string, unknown> {
    const schemaMap = new Map(preset.parameters.map((p) => [p.name, p]));
    const result: Record<string, unknown> = {};

    // 1. Detectar parámetros desconocidos en overrides
    for (const [key, val] of Object.entries(overrides)) {
      if (!schemaMap.has(key)) {
        throw new ValidationError(
          `UNKNOWN_PRESET_PARAMETER: Unknown parameter '${key}' for preset '${preset.id}'. Declared parameters are: ${preset.parameters.map((p) => p.name).join(", ")}`
        );
      }
    }

    // 2. Aplicar defaults y validar tipos / rangos / enums
    for (const param of preset.parameters) {
      const rawVal = overrides[param.name] !== undefined ? overrides[param.name] : param.default;

      if (rawVal === undefined || rawVal === null) {
        throw new ValidationError(
          `MISSING_REQUIRED_PRESET_PARAMETER: Parameter '${param.name}' is required for preset '${preset.id}'.`
        );
      }

      // Validación por tipo
      switch (param.type) {
        case "number":
        case "duration":
        case "distance": {
          if (typeof rawVal !== "number" || Number.isNaN(rawVal)) {
            throw new ValidationError(
              `INVALID_PARAMETER_TYPE: Parameter '${param.name}' of preset '${preset.id}' must be a number. Received: ${typeof rawVal}`
            );
          }
          if (param.min !== undefined && rawVal < param.min) {
            throw new ValidationError(
              `PARAMETER_OUT_OF_RANGE: Parameter '${param.name}' (${rawVal}) is below minimum (${param.min}) for preset '${preset.id}'.`
            );
          }
          if (param.max !== undefined && rawVal > param.max) {
            throw new ValidationError(
              `PARAMETER_OUT_OF_RANGE: Parameter '${param.name}' (${rawVal}) exceeds maximum (${param.max}) for preset '${preset.id}'.`
            );
          }
          break;
        }

        case "boolean": {
          if (typeof rawVal !== "boolean") {
            throw new ValidationError(
              `INVALID_PARAMETER_TYPE: Parameter '${param.name}' of preset '${preset.id}' must be a boolean. Received: ${typeof rawVal}`
            );
          }
          break;
        }

        case "string": {
          if (typeof rawVal !== "string") {
            throw new ValidationError(
              `INVALID_PARAMETER_TYPE: Parameter '${param.name}' of preset '${preset.id}' must be a string. Received: ${typeof rawVal}`
            );
          }
          break;
        }

        case "enum": {
          if (typeof rawVal !== "string" || !param.values || !param.values.includes(rawVal)) {
            throw new ValidationError(
              `INVALID_ENUM_VALUE: Parameter '${param.name}' of preset '${preset.id}' must be one of [${param.values?.join(", ")}]. Received: '${rawVal}'`
            );
          }
          break;
        }
      }

      result[param.name] = rawVal;
    }

    return result;
  }
}
