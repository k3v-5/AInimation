import { PropertyBinding, TransformSample } from "../types/index.js";

/**
 * Motor de vinculación desacoplada entre datos de tracking y propiedades de elementos gráficos (Fase 5G).
 */
export class PropertyBindingEngine {
  public static applyBinding(
    binding: PropertyBinding,
    trackedTransform: TransformSample
  ): { position?: { x: number; y: number }; scale?: { x: number; y: number }; rotation?: number } {
    const result: { position?: { x: number; y: number }; scale?: { x: number; y: number }; rotation?: number } =
      {};

    const offsetX = binding.offset?.x ?? 0;
    const offsetY = binding.offset?.y ?? 0;
    const scaleMulX = binding.scaleMultiplier?.x ?? 1.0;
    const scaleMulY = binding.scaleMultiplier?.y ?? 1.0;
    const rotOffset = binding.rotationOffset ?? 0;

    if (binding.targetProperty === "transform" || binding.targetProperty === "position") {
      result.position = {
        x: trackedTransform.position.x + offsetX,
        y: trackedTransform.position.y + offsetY,
      };
    }

    if (binding.targetProperty === "transform" || binding.targetProperty === "scale") {
      result.scale = {
        x: trackedTransform.scale.x * scaleMulX,
        y: trackedTransform.scale.y * scaleMulY,
      };
    }

    if (binding.targetProperty === "transform" || binding.targetProperty === "rotation") {
      result.rotation = trackedTransform.rotation + rotOffset;
    }

    return result;
  }
}
