import { generateDeterministicLayerId } from "../../core/id.js";
import { Time } from "../../core/types.js";
import { ValidationError } from "../../errors/index.js";
import { validateId } from "../../validation/validators.js";
import { TrackSerialization, TrackType } from "../types/index.js";
import { Clip } from "./Clip.js";
import { TimeRange } from "./TimeRange.js";

export interface TrackOptions {
  id?: string;
  name?: string;
  type?: TrackType;
  order?: number;
  enabled?: boolean;
  muted?: boolean;
  locked?: boolean;
  solo?: boolean;
  opacity?: number;
  clips?: Clip[];
}

/**
 * Pista de composición dentro de la línea de tiempo (Fase 5B).
 */
export class Track {
  public readonly id: string;
  public name: string;
  public type: TrackType;
  public order: number;
  public enabled: boolean;
  public muted: boolean;
  public locked: boolean;
  public solo: boolean;
  public opacity: number;
  private _clips: Clip[] = [];

  constructor(options: TrackOptions = {}) {
    this.id = options.id ? validateId(options.id, "track.id") : `track_${generateDeterministicLayerId()}`;
    this.name = options.name ?? `Track ${this.id}`;
    this.type = options.type ?? "video";
    this.order = options.order ?? 0;
    this.enabled = options.enabled ?? true;
    this.muted = options.muted ?? false;
    this.locked = options.locked ?? false;
    this.solo = options.solo ?? false;
    this.opacity = options.opacity !== undefined ? Math.max(0, Math.min(1, options.opacity)) : 1.0;

    if (options.clips) {
      for (const clip of options.clips) {
        this.addClip(clip);
      }
    }
  }

  public get clips(): Clip[] {
    return [...this._clips];
  }

  public get size(): number {
    return this._clips.length;
  }

  /**
   * Añade un clip a la pista y le asigna el trackId.
   */
  public addClip(clip: Clip): this {
    if (this.locked) {
      throw new ValidationError(`Cannot add clip to locked track '${this.id}'.`);
    }

    clip.trackId = this.id;
    this._clips.push(clip);
    // Mantener orden cronológico por start
    this._clips.sort((a, b) => a.timelineRange.start - b.timelineRange.start);
    return this;
  }

  public removeClip(clipId: string): boolean {
    if (this.locked) {
      throw new ValidationError(`Cannot remove clip from locked track '${this.id}'.`);
    }

    const idx = this._clips.findIndex((c) => c.id === clipId);
    if (idx !== -1) {
      this._clips.splice(idx, 1);
      return true;
    }
    return false;
  }

  public getClip(clipId: string): Clip | undefined {
    return this._clips.find((c) => c.id === clipId);
  }

  /**
   * Obtiene todos los clips activos en la pista para el tiempo global dado [start, end).
   */
  public getActiveClips(globalTime: Time): Clip[] {
    if (!this.enabled) return [];
    return this._clips.filter((clip) => clip.isActive(globalTime));
  }

  /**
   * Desplaza el inicio temporal de un clip conservando su duración y fuente.
   */
  public moveClip(clipId: string, newStart: Time): void {
    if (this.locked) {
      throw new ValidationError(`Cannot move clip on locked track '${this.id}'.`);
    }

    const clip = this.getClip(clipId);
    if (!clip) {
      throw new ValidationError(`Clip '${clipId}' not found on track '${this.id}'.`);
    }

    const duration = clip.timelineRange.duration;
    clip.timelineRange = new TimeRange(newStart, newStart + duration);
    this._clips.sort((a, b) => a.timelineRange.start - b.timelineRange.start);
  }

  /**
   * Recorta el inicio o final de un clip en la línea de tiempo.
   */
  public trimClip(clipId: string, newStart: Time, newEnd: Time): void {
    if (this.locked) {
      throw new ValidationError(`Cannot trim clip on locked track '${this.id}'.`);
    }

    const clip = this.getClip(clipId);
    if (!clip) {
      throw new ValidationError(`Clip '${clipId}' not found on track '${this.id}'.`);
    }

    clip.timelineRange = new TimeRange(newStart, newEnd);
    this._clips.sort((a, b) => a.timelineRange.start - b.timelineRange.start);
  }

  /**
   * Divide un clip en dos y los inserta en la pista.
   */
  public splitClip(clipId: string, splitTime: Time): [Clip, Clip] {
    if (this.locked) {
      throw new ValidationError(`Cannot split clip on locked track '${this.id}'.`);
    }

    const clip = this.getClip(clipId);
    if (!clip) {
      throw new ValidationError(`Clip '${clipId}' not found on track '${this.id}'.`);
    }

    const [clip1, clip2] = clip.split(splitTime);
    this.removeClip(clipId);
    this.addClip(clip1);
    this.addClip(clip2);

    return [clip1, clip2];
  }

  public toJSON(): TrackSerialization {
    return {
      id: this.id,
      name: this.name,
      type: this.type,
      order: this.order,
      enabled: this.enabled,
      muted: this.muted,
      locked: this.locked,
      solo: this.solo,
      opacity: this.opacity,
      clips: this._clips.map((c) => c.toJSON()),
    };
  }

  public static fromJSON(data: TrackSerialization): Track {
    return new Track({
      id: data.id,
      name: data.name,
      type: data.type,
      order: data.order,
      enabled: data.enabled,
      muted: data.muted,
      locked: data.locked,
      solo: data.solo,
      opacity: data.opacity,
      clips: data.clips.map((c) => Clip.fromJSON(c)),
    });
  }
}
