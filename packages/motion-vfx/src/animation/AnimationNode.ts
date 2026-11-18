import { generateDeterministicLayerId } from "../core/id.js";
import { Time } from "../core/types.js";
import { validateId, validateNonNegativeNumber } from "../validation/validators.js";
import { AnimationResult } from "./AnimationResult.js";
import { AnimationLifecycleState, BaseAnimationOptions } from "./types.js";

/**
 * Clase base abstracta para todos los nodos del árbol de animación (Composite Pattern).
 */
export abstract class AnimationNode {
  public readonly id: string;
  public delay: Time;
  public priority: number;

  constructor(options: BaseAnimationOptions = {}) {
    this.id = options.id ? validateId(options.id, "animation.id") : generateDeterministicLayerId();
    this.delay = options.delay !== undefined ? validateNonNegativeNumber(options.delay, "delay") : 0;
    this.priority = options.priority ?? 0;
  }

  /**
   * Duración neta de la animación en segundos (sin contar el delay inicial).
   */
  public abstract get duration(): Time;

  /**
   * Duración total de la animación en segundos (delay + duration).
   */
  public get totalDuration(): Time {
    return this.delay + this.duration;
  }

  /**
   * Determina el estado del ciclo de vida de la animación en el tiempo local indicado.
   */
  public getState(time: Time): AnimationLifecycleState {
    if (time < this.delay) {
      return "before";
    }
    if (time > this.totalDuration) {
      return "after";
    }
    return "active";
  }

  /**
   * Evalúa la animación en el tiempo local y produce un AnimationResult puro sin mutar el proyecto.
   */
  public abstract evaluate(time: Time): AnimationResult;
}
