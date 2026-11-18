import { ValidationError } from "../../errors/index.js";
import { PresetDefinition, PresetSearchQuery } from "../schema/types.js";

/**
 * Catálogo central y registro de definiciones de Presets (Fase 4A).
 */
export class PresetRegistry {
  private static presets = new Map<string, PresetDefinition>();

  /**
   * Registra una nueva definición de preset.
   */
  public static register(preset: PresetDefinition): void {
    if (!preset || !preset.id) {
      throw new ValidationError("Preset must have a valid non-empty 'id'.");
    }

    if (this.presets.has(preset.id)) {
      throw new ValidationError(`DUPLICATE_PRESET_ID: Preset '${preset.id}' is already registered.`);
    }

    this.presets.set(preset.id, preset);
  }

  /**
   * Obtiene la definición de un preset por su ID.
   */
  public static get(id: string): PresetDefinition {
    const preset = this.presets.get(id);
    if (!preset) {
      throw new ValidationError(`PRESET_NOT_FOUND: Preset with ID '${id}' is not registered.`);
    }
    return preset;
  }

  /**
   * Comprueba si un preset existe en el registro.
   */
  public static has(id: string): boolean {
    return this.presets.has(id);
  }

  /**
   * Retorna la lista completa de presets registrados.
   */
  public static list(): PresetDefinition[] {
    return Array.from(this.presets.values());
  }

  /**
   * Busca presets según categoría, etiquetas o compatibilidad con tipos de elemento.
   */
  public static search(query: PresetSearchQuery = {}): PresetDefinition[] {
    return this.list().filter((p) => {
      if (query.category && p.category !== query.category) {
        return false;
      }
      if (query.compatibleWith && p.compatibleWith && !p.compatibleWith.includes(query.compatibleWith)) {
        return false;
      }
      if (query.tags && query.tags.length > 0) {
        const hasAllTags = query.tags.every((tag) => p.tags.includes(tag));
        if (!hasAllTags) return false;
      }
      return true;
    });
  }

  /**
   * Limpia el registro (útil para pruebas unitarias).
   */
  public static clear(): void {
    this.presets.clear();
  }
}
