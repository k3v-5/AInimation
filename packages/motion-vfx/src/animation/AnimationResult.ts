import { AnimationTarget } from "./types.js";

interface TargetValueEntry {
  value: unknown;
  priority: number;
}

/**
 * Contenedor inmutable y determinista para los valores resultantes de la evaluación de animaciones.
 */
export class AnimationResult {
  private entries = new Map<string, TargetValueEntry>();

  public static targetKey(target: AnimationTarget): string {
    return `${target.elementId}::${target.propertyPath}`;
  }

  /**
   * Almacena un valor evaluado para el destino dado, respetando la prioridad de sobreescritura.
   */
  public set(target: AnimationTarget, value: unknown, priority = 0): void {
    const key = AnimationResult.targetKey(target);
    const existing = this.entries.get(key);
    if (!existing || priority >= existing.priority) {
      this.entries.set(key, { value, priority });
    }
  }

  /**
   * Obtiene el valor evaluado para el destino especificado.
   */
  public get<T = unknown>(target: AnimationTarget): T | undefined {
    const key = AnimationResult.targetKey(target);
    const entry = this.entries.get(key);
    return entry ? (entry.value as T) : undefined;
  }

  /**
   * Comprueba si existe un valor para el destino especificado.
   */
  public has(target: AnimationTarget): boolean {
    const key = AnimationResult.targetKey(target);
    return this.entries.has(key);
  }

  /**
   * Fusiona otro AnimationResult en este, respetando prioridades relativas.
   */
  public merge(other: AnimationResult): void {
    for (const [key, entry] of other.entries.entries()) {
      const existing = this.entries.get(key);
      if (!existing || entry.priority >= existing.priority) {
        this.entries.set(key, { ...entry });
      }
    }
  }

  /**
   * Retorna un mapa plano con todos los valores evaluados.
   */
  public getAll(): Map<string, unknown> {
    const map = new Map<string, unknown>();
    for (const [key, entry] of this.entries.entries()) {
      map.set(key, entry.value);
    }
    return map;
  }
}
