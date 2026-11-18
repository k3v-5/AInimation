import { Time } from "../../core/types.js";
import { EffectContext, EffectSerialization, EvaluatedEffectStack } from "../types/index.js";
import { BaseEffect } from "./BaseEffect.js";

/**
 * Pila secuencial y ordenada de modificadores visuales aplicados a un elemento o composición (Fase 4C).
 */
export class EffectStack {
  private stack: BaseEffect[] = [];

  constructor(effects: BaseEffect[] = []) {
    this.stack = [...effects];
  }

  /**
   * Añade un efecto al final de la pila de procesamiento.
   */
  public add(effect: BaseEffect): this {
    this.stack.push(effect);
    return this;
  }

  /**
   * Inserta un efecto en una posición específica de la pila.
   */
  public insert(index: number, effect: BaseEffect): this {
    this.stack.splice(index, 0, effect);
    return this;
  }

  /**
   * Elimina un efecto por su ID.
   */
  public remove(id: string): boolean {
    const idx = this.stack.findIndex((e) => e.id === id);
    if (idx !== -1) {
      this.stack.splice(idx, 1);
      return true;
    }
    return false;
  }

  /**
   * Obtiene un efecto por su ID.
   */
  public get(id: string): BaseEffect | undefined {
    return this.stack.find((e) => e.id === id);
  }

  /**
   * Obtiene el primer efecto que coincida con el tipo especificado.
   */
  public getByType<T extends BaseEffect>(type: string): T | undefined {
    return this.stack.find((e) => e.type === type) as T | undefined;
  }

  /**
   * Retorna una copia superficial de la lista ordenada de efectos.
   */
  public get effects(): BaseEffect[] {
    return [...this.stack];
  }

  public get length(): number {
    return this.stack.length;
  }

  public clear(): void {
    this.stack = [];
  }

  /**
   * Evalúa todos los efectos de la pila en orden estricto para el tiempo t dado.
   */
  public evaluate(time: Time, context?: EffectContext): EvaluatedEffectStack {
    const evaluatedEffects = this.stack.map((effect) => effect.evaluate(time, context));
    return {
      effects: evaluatedEffects,
    };
  }

  /**
   * Serializa la pila completa de efectos.
   */
  public toJSON(): EffectSerialization[] {
    return this.stack.map((effect) => effect.toJSON());
  }
}
