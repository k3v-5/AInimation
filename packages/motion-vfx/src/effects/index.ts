import { BaseEffect } from "./core/BaseEffect.js";
import { EffectRegistry } from "./core/EffectRegistry.js";

export * from "./builtins/index.js";
export * from "./color/CinematicColorGradingEngine.js";
export * from "./core/BaseEffect.js";
export * from "./core/EffectRegistry.js";
export * from "./core/EffectStack.js";
export * from "./types/index.js";

/**
 * Función de conveniencia para instanciar cualquier efecto por tipo.
 */
export function createEffect(type: string, options: Record<string, unknown> = {}): BaseEffect {
  return EffectRegistry.create(type, options);
}
