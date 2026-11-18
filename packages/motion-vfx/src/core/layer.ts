import { cloneValue } from "../animation/interpolation.js";
import { validateId, validateNonNegativeNumber, validateTime } from "../validation/validators.js";
import { generateDeterministicLayerId } from "./id.js";
import { Property } from "./property.js";
import { Time, Vector2 } from "./types.js";

export interface LayerOptions {
  id?: string;
  name?: string;
  startTime?: Time;
  endTime?: Time;
}

export interface LayerSnapshot {
  id: string;
  name: string;
  active: boolean;
  properties?: Record<string, unknown>;
}

/**
 * Representación de una capa individual en el Timeline.
 */
export class Layer {
  public readonly id: string;
  public name: string;
  public startTime: Time;
  public endTime: Time;

  private properties = new Map<string, Property<unknown>>();

  constructor(options: LayerOptions = {}) {
    this.id = options.id ? validateId(options.id, "layer.id") : generateDeterministicLayerId();
    this.name = options.name?.trim() || this.id;
    this.startTime = validateNonNegativeNumber(options.startTime ?? 0, "layer.startTime");
    if (options.endTime === undefined || options.endTime === Infinity) {
      this.endTime = Infinity;
    } else {
      this.endTime = validateNonNegativeNumber(options.endTime, "layer.endTime");
    }

    if (this.endTime < this.startTime) {
      throw new Error(`Layer '${this.id}' endTime (${this.endTime}) cannot be less than startTime (${this.startTime}).`);
    }

    // Inicializar propiedades estándar de transformación básicas
    this.properties.set("position", new Property<Vector2>({ x: 0, y: 0 }) as Property<unknown>);
    this.properties.set("scale", new Property<Vector2>({ x: 1, y: 1 }) as Property<unknown>);
    this.properties.set("rotation", new Property<number>(0) as Property<unknown>);
    this.properties.set("opacity", new Property<number>(1) as Property<unknown>);
  }

  /**
   * Obtiene o registra una propiedad dentro de la capa.
   */
  public property<T = unknown>(name: string, initialValue?: T): Property<T> {
    const trimmed = validateId(name, "propertyName");
    if (!this.properties.has(trimmed)) {
      if (initialValue === undefined) {
        throw new Error(`Property '${trimmed}' does not exist on layer '${this.id}' and no initial value was provided.`);
      }
      this.properties.set(trimmed, new Property<T>(initialValue) as Property<unknown>);
    }
    return this.properties.get(trimmed) as Property<T>;
  }

  /**
   * Retorna todas las propiedades registradas en la capa.
   */
  public getProperties(): Map<string, Property<unknown>> {
    return this.properties;
  }

  /**
   * Comprueba si la capa está activa en el instante de tiempo dado.
   * Regla de activación: startTime <= time < endTime
   */
  public isActive(time: Time): boolean {
    const validTime = validateTime(time);
    return validTime >= this.startTime && validTime < this.endTime;
  }

  /**
   * Evalúa el estado de la capa en el instante de tiempo dado.
   * Retorna un snapshot inmutable.
   */
  public evaluate(time: Time): LayerSnapshot {
    const validTime = validateTime(time);
    const active = this.isActive(validTime);

    if (!active) {
      return {
        id: this.id,
        name: this.name,
        active: false,
      };
    }

    const evaluatedProps: Record<string, unknown> = {};
    for (const [propName, prop] of this.properties.entries()) {
      evaluatedProps[propName] = cloneValue(prop.evaluate(validTime));
    }

    return {
      id: this.id,
      name: this.name,
      active: true,
      properties: evaluatedProps,
    };
  }
}
