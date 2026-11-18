import { Composition, CompositionOptions } from "../../core/composition.js";
import { generateDeterministicLayerId } from "../../core/id.js";
import { Time } from "../../core/types.js";
import { Marker } from "../../timeline/types/index.js";
import { validateId, validateNonNegativeNumber, validateTime } from "../../validation/validators.js";
import { EvaluatedSceneState, SceneMetadata, SceneSerialization } from "../types/index.js";

export interface SceneOptions {
  id?: string;
  duration: Time;
  composition?: Composition | CompositionOptions;
  metadata?: SceneMetadata;
  markers?: Marker[];
}

/**
 * Unidad compositiva temporal modular (Fase 5C).
 * Posee duración propia, roles semánticos (hook, intro, cta, etc.) y una composición asociada.
 */
export class Scene {
  public readonly id: string;
  public duration: Time;
  public composition: Composition;
  public metadata: SceneMetadata;
  private _markers: Marker[] = [];

  constructor(options: SceneOptions) {
    this.id = options.id ? validateId(options.id, "scene.id") : `scene_${generateDeterministicLayerId()}`;
    this.duration = validateNonNegativeNumber(options.duration, "scene.duration");

    if (options.composition instanceof Composition) {
      this.composition = options.composition;
    } else {
      this.composition = new Composition({
        id: `comp_${this.id}`,
        name: options.metadata?.name ?? `Composition ${this.id}`,
        width: options.composition?.width ?? 1920,
        height: options.composition?.height ?? 1080,
        fps: options.composition?.fps ?? 30,
        duration: this.duration,
      });
    }

    this.metadata = options.metadata ? { ...options.metadata } : {};

    if (options.markers) {
      this._markers = [...options.markers];
    }
  }

  public get markers(): Marker[] {
    return [...this._markers];
  }

  public addMarker(marker: Marker): this {
    this._markers.push({ ...marker });
    this._markers.sort((a, b) => a.time - b.time);
    return this;
  }

  /**
   * Determina si la escena está activa en el tiempo local [0, duration).
   */
  public isActive(localTime: Time): boolean {
    if (typeof localTime !== "number" || !Number.isFinite(localTime) || Number.isNaN(localTime)) {
      return false;
    }
    return localTime >= 0 && localTime < this.duration;
  }

  /**
   * Evalúa la escena en el tiempo local especificado.
   */
  public evaluate(localTime: Time): EvaluatedSceneState {
    const validTime = validateTime(localTime);
    const active = this.isActive(validTime);
    const compSnapshot = this.composition.evaluate(validTime);

    return {
      id: this.id,
      localTime: validTime,
      active,
      metadata: { ...this.metadata },
      elements: compSnapshot.elements ?? compSnapshot.layers,
    };
  }

  public toJSON(): SceneSerialization {
    return {
      id: this.id,
      duration: this.duration,
      metadata: { ...this.metadata },
      markers: this._markers.map((m) => ({ ...m })),
      composition: {
        id: this.composition.id,
        name: this.composition.name,
        width: this.composition.width,
        height: this.composition.height,
        fps: this.composition.fps,
        duration: this.composition.duration,
      },
    };
  }

  public static fromJSON(data: SceneSerialization): Scene {
    const compData = data.composition as any;
    const comp = new Composition({
      id: compData.id,
      name: compData.name,
      width: compData.width,
      height: compData.height,
      fps: compData.fps,
      duration: compData.duration,
    });

    return new Scene({
      id: data.id,
      duration: data.duration,
      composition: comp,
      metadata: data.metadata,
      markers: data.markers,
    });
  }
}
