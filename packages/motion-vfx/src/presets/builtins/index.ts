import { PresetRegistry } from "../core/registry.js";
import { popInPreset } from "./popIn.js";

/**
 * Registra todos los presets nativos built-in en el PresetRegistry.
 */
export function registerBuiltinPresets(): void {
  if (!PresetRegistry.has(popInPreset.id)) {
    PresetRegistry.register(popInPreset);
  }
}

// Auto-registro al importar el módulo
registerBuiltinPresets();

export * from "./popIn.js";
