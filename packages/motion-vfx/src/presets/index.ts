import { AnimationNode } from "../animation/AnimationNode.js";
import { BaseElement } from "../elements/BaseElement.js";
import { ElementType } from "../elements/types.js";
import { PresetResolver } from "./core/resolver.js";

export * from "./builtins/index.js";
export * from "./core/registry.js";
export * from "./core/resolver.js";
export * from "./schema/types.js";

/**
 * Función de conveniencia de alto nivel para aplicar un preset a un elemento.
 */
export function applyPreset(
  presetId: string,
  target: BaseElement | { id: string; type?: ElementType },
  overrides: Record<string, unknown> = {}
): AnimationNode {
  return PresetResolver.resolve(presetId, target, overrides);
}
