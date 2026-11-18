import { Camera } from "../../camera/types/index.js";
import { generateDeterministicLayerId } from "../../core/id.js";
import { Time } from "../../core/types.js";
import { ValidationError } from "../../errors/index.js";
import { validateId } from "../../validation/validators.js";
import { SceneMarker, SceneOptions } from "../types/index.js";
import { Layer } from "./Layer.js";

/**
 * Contenedor principal de escena cinemática con capas, cámara y marcadores semánticos (Fase 5H).
 */
export class Scene {
  public readonly id: string;
  public name: string;
  public duration: Time;
  public width: number;
  public height: number;
  private _layers: Layer[] = [];
  public camera?: Camera;
  public markers: SceneMarker[] = [];

  constructor(options: SceneOptions) {
    this.id = options.id ? validateId(options.id, "scene.id") : `scene_${generateDeterministicLayerId()}`;
    this.name = options.name ?? `Scene ${this.id}`;
    this.duration = Math.max(0.01, options.duration);
    this.width = options.width ?? 1080;
    this.height = options.height ?? 1920;
    this.camera = options.camera;
    this.markers = options.markers ? [...options.markers] : [];

    if (options.layers) {
      for (const l of options.layers) {
        this.addLayer(l instanceof Layer ? l : new Layer(l));
      }
    }
  }

  public get layers(): Layer[] {
    return [...this._layers];
  }

  public get layerCount(): number {
    return this._layers.length;
  }

  public addLayer(layer: Layer): this {
    if (this._layers.some((l) => l.id === layer.id)) {
      throw new ValidationError(`DUPLICATE_LAYER_ID: Layer with id '${layer.id}' already exists in scene.`);
    }
    this._layers.push(layer);
    return this;
  }

  public removeLayer(id: string): boolean {
    const idx = this._layers.findIndex((l) => l.id === id);
    if (idx !== -1) {
      this._layers.splice(idx, 1);
      return true;
    }
    return false;
  }

  public getLayer(id: string): Layer | undefined {
    return this._layers.find((l) => l.id === id);
  }

  public addMarker(marker: SceneMarker): this {
    this.markers.push({ ...marker });
    this.markers.sort((a, b) => a.time - b.time);
    return this;
  }

  public getActiveLayers(time: Time): Layer[] {
    return this._layers.filter(
      (l) => l.visible && time >= l.start && time < l.start + l.duration
    );
  }

  public toJSON(): any {
    return {
      id: this.id,
      name: this.name,
      duration: this.duration,
      width: this.width,
      height: this.height,
      camera: this.camera ? { ...this.camera } : undefined,
      markers: this.markers.map((m) => ({ ...m })),
      layers: this._layers.map((l) => l.toJSON()),
    };
  }

  public static fromJSON(data: any): Scene {
    return new Scene({
      id: data.id,
      name: data.name,
      duration: data.duration,
      width: data.width,
      height: data.height,
      camera: data.camera,
      markers: data.markers,
      layers: (data.layers ?? []).map((l: any) => Layer.fromJSON(l)),
    });
  }
}
