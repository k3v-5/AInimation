import { AssetRegistry } from "../assets/index.js";
import { BaseElement, BaseElementState } from "../elements/index.js";
import { DuplicateLayerError, LayerNotFoundError } from "../errors/index.js";
import { validateId, validateNonNegativeNumber, validatePositiveNumber, validateTime } from "../validation/validators.js";
import { generateDeterministicCompId } from "./id.js";
import { Layer, LayerSnapshot } from "./layer.js";
import { Time } from "./types.js";

export interface CompositionOptions {
  id?: string;
  name?: string;
  width: number;
  height: number;
  fps: number;
  duration: Time;
}

export interface CompositionSnapshot {
  time: Time;
  duration: Time;
  width: number;
  height: number;
  fps: number;
  layers: LayerSnapshot[];
  elements?: BaseElementState[];
}

/**
 * Contenedor principal de una composición animada y sus elementos audiovisuales.
 */
export class Composition {
  public readonly id: string;
  public name: string;
  public readonly width: number;
  public readonly height: number;
  public readonly fps: number;
  public readonly duration: Time;

  public readonly assets = new AssetRegistry();
  private layers: Layer[] = [];
  private elements: BaseElement[] = [];

  constructor(options: CompositionOptions) {
    this.id = options.id ? validateId(options.id, "composition.id") : generateDeterministicCompId();
    this.name = options.name?.trim() || this.id;
    this.width = validatePositiveNumber(options.width, "composition.width");
    this.height = validatePositiveNumber(options.height, "composition.height");
    this.fps = validatePositiveNumber(options.fps, "composition.fps");
    this.duration = validateNonNegativeNumber(options.duration, "composition.duration");
  }

  // --- MÉTODOS DE ELEMENTOS (FASE 2) ---

  /**
   * Añade un elemento a la composición. Lanza DuplicateLayerError si el ID ya existe.
   */
  public addElement(element: BaseElement): void {
    if (!element || !(element instanceof BaseElement)) {
      throw new Error("Invalid element instance.");
    }
    if (this.elements.some((e) => e.id === element.id)) {
      throw new DuplicateLayerError(element.id);
    }
    this.elements.push(element);
  }

  /**
   * Elimina un elemento por su ID.
   */
  public removeElement(id: string): boolean {
    const validId = validateId(id, "element.id");
    const index = this.elements.findIndex((e) => e.id === validId);
    if (index !== -1) {
      this.elements.splice(index, 1);
      return true;
    }
    return false;
  }

  /**
   * Obtiene un elemento por su ID.
   */
  public getElement(id: string): BaseElement | undefined {
    const validId = validateId(id, "element.id");
    return this.elements.find((e) => e.id === validId);
  }

  /**
   * Retorna una copia del array de elementos respetando el orden de apilamiento.
   */
  public getElements(): BaseElement[] {
    return [...this.elements];
  }

  /**
   * Cambia la posición de un elemento en el orden de apilamiento (stacking order).
   */
  public moveElement(id: string, newIndex: number): void {
    const validId = validateId(id, "element.id");
    const currentIndex = this.elements.findIndex((e) => e.id === validId);
    if (currentIndex === -1) {
      throw new LayerNotFoundError(validId);
    }
    if (newIndex < 0 || newIndex >= this.elements.length) {
      throw new Error(`Invalid target element index: ${newIndex}. Must be within [0, ${this.elements.length - 1}].`);
    }

    const [elem] = this.elements.splice(currentIndex, 1);
    this.elements.splice(newIndex, 0, elem);
  }

  /**
   * Mueve el elemento inmediatamente antes del elemento objetivo.
   */
  public moveBefore(id: string, targetId: string): void {
    const validId = validateId(id, "element.id");
    const validTargetId = validateId(targetId, "targetId");
    const currentIndex = this.elements.findIndex((e) => e.id === validId);
    if (currentIndex === -1) throw new LayerNotFoundError(validId);
    const targetIndex = this.elements.findIndex((e) => e.id === validTargetId);
    if (targetIndex === -1) throw new LayerNotFoundError(validTargetId);

    const [elem] = this.elements.splice(currentIndex, 1);
    const newTargetIndex = this.elements.findIndex((e) => e.id === validTargetId);
    this.elements.splice(newTargetIndex, 0, elem);
  }

  /**
   * Mueve el elemento inmediatamente después del elemento objetivo.
   */
  public moveAfter(id: string, targetId: string): void {
    const validId = validateId(id, "element.id");
    const validTargetId = validateId(targetId, "targetId");
    const currentIndex = this.elements.findIndex((e) => e.id === validId);
    if (currentIndex === -1) throw new LayerNotFoundError(validId);
    const targetIndex = this.elements.findIndex((e) => e.id === validTargetId);
    if (targetIndex === -1) throw new LayerNotFoundError(validTargetId);

    const [elem] = this.elements.splice(currentIndex, 1);
    const newTargetIndex = this.elements.findIndex((e) => e.id === validTargetId);
    this.elements.splice(newTargetIndex + 1, 0, elem);
  }

  /**
   * Trae el elemento al frente (última posición en el orden de apilamiento).
   */
  public bringToFront(id: string): void {
    const validId = validateId(id, "element.id");
    const currentIndex = this.elements.findIndex((e) => e.id === validId);
    if (currentIndex === -1) throw new LayerNotFoundError(validId);
    const [elem] = this.elements.splice(currentIndex, 1);
    this.elements.push(elem);
  }

  /**
   * Envía el elemento al fondo (primera posición en el orden de apilamiento).
   */
  public sendToBack(id: string): void {
    const validId = validateId(id, "element.id");
    const currentIndex = this.elements.findIndex((e) => e.id === validId);
    if (currentIndex === -1) throw new LayerNotFoundError(validId);
    const [elem] = this.elements.splice(currentIndex, 1);
    this.elements.unshift(elem);
  }

  // --- MÉTODOS DE LAYERS (COMPATIBILIDAD FASE 1) ---

  /**
   * Añade una capa a la composición. Lanza DuplicateLayerError si el id ya existe.
   */
  public addLayer(layer: Layer): void {
    if (!layer || !(layer instanceof Layer)) {
      throw new Error("Invalid layer instance.");
    }
    if (this.layers.some((l) => l.id === layer.id)) {
      throw new DuplicateLayerError(layer.id);
    }
    this.layers.push(layer);
  }

  /**
   * Elimina una capa por su id. Retorna true si fue eliminada.
   */
  public removeLayer(id: string): boolean {
    const validId = validateId(id, "layer.id");
    const index = this.layers.findIndex((l) => l.id === validId);
    if (index !== -1) {
      this.layers.splice(index, 1);
      return true;
    }
    return false;
  }

  /**
   * Obtiene una capa por su id.
   */
  public getLayer(id: string): Layer | undefined {
    const validId = validateId(id, "layer.id");
    return this.layers.find((l) => l.id === validId);
  }

  /**
   * Retorna una copia del array de capas respetando el orden de stacking.
   */
  public getLayers(): Layer[] {
    return [...this.layers];
  }

  /**
   * Cambia la posición de una capa en el orden de apilamiento (stacking order).
   */
  public moveLayer(id: string, newIndex: number): void {
    const validId = validateId(id, "layer.id");
    const currentIndex = this.layers.findIndex((l) => l.id === validId);
    if (currentIndex === -1) {
      throw new LayerNotFoundError(validId);
    }
    if (newIndex < 0 || newIndex >= this.layers.length) {
      throw new Error(`Invalid target layer index: ${newIndex}. Must be within [0, ${this.layers.length - 1}].`);
    }

    const [layer] = this.layers.splice(currentIndex, 1);
    this.layers.splice(newIndex, 0, layer);
  }

  /**
   * Evalúa el estado completo de la composición en el instante `time`.
   * Retorna un snapshot inmutable.
   */
  public evaluate(time: Time): CompositionSnapshot {
    const validTime = validateTime(time);

    const layerSnapshots: LayerSnapshot[] = this.layers.map((layer) => layer.evaluate(validTime));
    const elementSnapshots: BaseElementState[] = this.elements.map((element) => element.evaluate(validTime));

    return {
      time: validTime,
      duration: this.duration,
      width: this.width,
      height: this.height,
      fps: this.fps,
      layers: layerSnapshots,
      ...(this.elements.length > 0 ? { elements: elementSnapshots } : {}),
    };
  }
}
