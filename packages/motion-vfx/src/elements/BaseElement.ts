import { generateDeterministicLayerId } from "../core/id.js";
import { Time } from "../core/types.js";
import { EvaluatedTransform, Transform, Transformable } from "../transform/index.js";
import { EffectStack } from "../effects/core/EffectStack.js";
import { validateId, validateNonNegativeNumber, validatePositiveNumber, validateTime } from "../validation/validators.js";
import { BaseElementOptions, BaseElementState, ElementType, EvaluatedElement } from "./types.js";

/**
 * Clase base abstracta para todos los elementos audiovisuales del Motion Engine.
 */
export abstract class BaseElement implements Transformable {
  public readonly id: string;
  public name: string;
  public abstract readonly type: ElementType;

  public startTime: Time;
  public duration: Time;
  public visible: boolean;

  public transform: Transform;
  public effects: EffectStack;
  public parentId?: string;

  constructor(options: BaseElementOptions = {}) {
    this.id = options.id ? validateId(options.id, "element.id") : generateDeterministicLayerId();
    this.name = options.name ?? this.id;
    this.startTime = options.startTime !== undefined ? validateTime(options.startTime) : 0;
    this.duration = options.duration !== undefined ? validatePositiveNumber(options.duration, "duration") : 10;
    this.visible = options.visible ?? true;
    this.parentId = options.parentId ? validateId(options.parentId, "parentId") : undefined;
    this.transform = new Transform();
    this.effects = new EffectStack();
  }

  /**
   * Calcula el tiempo relativo local del elemento a partir del tiempo global de la composición.
   */
  public getLocalTime(globalTime: Time): Time {
    const validGlobalTime = validateTime(globalTime);
    return validGlobalTime - this.startTime;
  }

  /**
   * Determina si el elemento se encuentra activo en el instante global dado [startTime, startTime + duration).
   */
  public isActive(globalTime: Time): boolean {
    const validGlobalTime = validateTime(globalTime);
    if (!this.visible) {
      return false;
    }
    return validGlobalTime >= this.startTime && validGlobalTime < this.startTime + this.duration;
  }

  /**
   * Clona el elemento generando un nuevo ID único de forma determinista.
   */
  public abstract clone(): BaseElement;

  /**
   * Evalúa el estado puro del elemento en el tiempo global indicado sin mutar el proyecto ni renderizar.
   */
  public abstract evaluate(globalTime: Time, parentTransform?: EvaluatedTransform): EvaluatedElement;
}
