import { generateDeterministicLayerId } from "../../core/id.js";
import { Time } from "../../core/types.js";
import { EffectSerialization } from "../../effects/types/index.js";
import { Mask } from "../../masks/types/index.js";
import { Transform } from "../../transform/Transform.js";
import { validateId } from "../../validation/validators.js";
import { AlphaMode, BlendMode, LayerOptions, LayerType } from "../types/index.js";

/**
 * Representación unificada de una capa visual en el motor de composición (Fase 5H).
 */
export class Layer {
  public readonly id: string;
  public name: string;
  public type: LayerType;
  public start: Time;
  public duration: Time;
  public transform: Transform;
  public opacity: number;
  public visible: boolean;
  public blendMode: BlendMode;
  public alphaMode: AlphaMode;
  public parentId?: string;
  public effectStack?: EffectSerialization[];
  public masks: Mask[] = [];
  public compositionId?: string;

  constructor(options: LayerOptions) {
    this.id = options.id ? validateId(options.id, "layer.id") : `layer_${generateDeterministicLayerId()}`;
    this.name = options.name ?? `Layer ${this.id}`;
    this.type = options.type;
    this.start = options.start ?? 0.0;
    this.duration = options.duration ?? 10.0;
    this.transform = options.transform ?? new Transform();
    this.opacity = options.opacity !== undefined ? Math.max(0, Math.min(1, options.opacity)) : 1.0;
    this.visible = options.visible ?? true;
    this.blendMode = options.blendMode ?? "normal";
    this.alphaMode = options.alphaMode ?? "premultiplied";
    this.parentId = options.parentId;
    this.effectStack = options.effectStack;
    this.masks = options.masks ? [...options.masks] : [];
    this.compositionId = options.compositionId;
  }

  public toJSON(): LayerOptions {
    return {
      id: this.id,
      name: this.name,
      type: this.type,
      start: this.start,
      duration: this.duration,
      transform: this.transform,
      opacity: this.opacity,
      visible: this.visible,
      blendMode: this.blendMode,
      alphaMode: this.alphaMode,
      parentId: this.parentId,
      effectStack: this.effectStack,
      masks: this.masks.map((m) => ({ ...m })),
      compositionId: this.compositionId,
    };
  }

  public static fromJSON(data: any): Layer {
    return new Layer({
      id: data.id,
      name: data.name,
      type: data.type,
      start: data.start,
      duration: data.duration,
      transform: data.transform ? Transform.fromJSON(data.transform) : new Transform(),
      opacity: data.opacity,
      visible: data.visible,
      blendMode: data.blendMode,
      alphaMode: data.alphaMode,
      parentId: data.parentId,
      effectStack: data.effectStack,
      masks: data.masks,
      compositionId: data.compositionId,
    });
  }
}
