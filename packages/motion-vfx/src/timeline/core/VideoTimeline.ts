import { Time } from "../../core/types.js";
import { ValidationError } from "../../errors/index.js";
import { validateNonNegativeNumber, validatePositiveNumber } from "../../validation/validators.js";
import {
  EvaluatedClip,
  Marker,
  TimeBase,
  TimelineSerialization,
  TimelineState,
} from "../types/index.js";
import { Clip } from "./Clip.js";
import { Track } from "./Track.js";

export interface VideoTimelineOptions {
  duration?: Time;
  timeBase?: TimeBase;
  tracks?: Track[];
  markers?: Marker[];
}

/**
 * Línea de tiempo multi-pista NLE determinista para edición de video (Fase 5B).
 */
export class VideoTimeline {
  public duration: Time;
  public timeBase: TimeBase;
  private _tracks: Track[] = [];
  private _markers: Marker[] = [];

  constructor(options: VideoTimelineOptions = {}) {
    this.duration =
      options.duration !== undefined
        ? validateNonNegativeNumber(options.duration, "timeline.duration")
        : 30.0;
    this.timeBase = options.timeBase ?? { fps: 30 };
    if (this.timeBase.fps <= 0) {
      throw new ValidationError(`Timeline fps must be > 0. Received: ${this.timeBase.fps}`);
    }

    if (options.tracks) {
      for (const track of options.tracks) {
        this.addTrack(track);
      }
    }

    if (options.markers) {
      this._markers = [...options.markers];
    }
  }

  public get tracks(): Track[] {
    return [...this._tracks];
  }

  public get markers(): Marker[] {
    return [...this._markers];
  }

  public addTrack(track: Track): this {
    if (this._tracks.some((t) => t.id === track.id)) {
      throw new ValidationError(`Track with id '${track.id}' already exists.`);
    }
    this._tracks.push(track);
    // Ordenar pistas por 'order' ascendente (las de mayor orden se renderizan encima)
    this._tracks.sort((a, b) => a.order - b.order);
    return this;
  }

  public removeTrack(trackId: string): boolean {
    const idx = this._tracks.findIndex((t) => t.id === trackId);
    if (idx !== -1) {
      this._tracks.splice(idx, 1);
      return true;
    }
    return false;
  }

  public getTrack(trackId: string): Track | undefined {
    return this._tracks.find((t) => t.id === trackId);
  }

  public getClip(clipId: string): { track: Track; clip: Clip } | undefined {
    for (const track of this._tracks) {
      const clip = track.getClip(clipId);
      if (clip) {
        return { track, clip };
      }
    }
    return undefined;
  }

  public addMarker(marker: Marker): this {
    this._markers.push({ ...marker });
    this._markers.sort((a, b) => a.time - b.time);
    return this;
  }

  public removeMarker(markerId: string): boolean {
    const idx = this._markers.findIndex((m) => m.id === markerId);
    if (idx !== -1) {
      this._markers.splice(idx, 1);
      return true;
    }
    return false;
  }

  /**
   * Obtiene todos los clips activos en el instante global time de acuerdo a las reglas de pistas.
   */
  public getActiveClips(globalTime: Time): EvaluatedClip[] {
    const activeClips: EvaluatedClip[] = [];

    // Comprobar si hay alguna pista en modo Solo
    const hasSolo = this._tracks.some((t) => t.solo);

    for (const track of this._tracks) {
      if (!track.enabled) continue;
      if (hasSolo && !track.solo) continue;

      const trackClips = track.getActiveClips(globalTime);
      for (const clip of trackClips) {
        activeClips.push({
          clipId: clip.id,
          name: clip.name,
          elementId: clip.elementId,
          trackId: track.id,
          trackType: track.type,
          localTime: clip.getLocalTime(globalTime),
          sourceTime: clip.getSourceTime(globalTime),
          speed: clip.speed,
          opacity: track.opacity,
        });
      }
    }

    return activeClips;
  }

  /**
   * Evaluación pura del estado de la línea de tiempo en el instante time.
   */
  public evaluate(globalTime: Time): TimelineState {
    const frame = Math.round(globalTime * this.timeBase.fps);
    const activeClips = this.getActiveClips(globalTime);

    return {
      time: globalTime,
      frame,
      activeClips,
    };
  }

  public splitClip(clipId: string, splitTime: Time): [Clip, Clip] {
    const found = this.getClip(clipId);
    if (!found) {
      throw new ValidationError(`Clip '${clipId}' not found in any track.`);
    }
    return found.track.splitClip(clipId, splitTime);
  }

  public moveClip(clipId: string, newStart: Time): void {
    const found = this.getClip(clipId);
    if (!found) {
      throw new ValidationError(`Clip '${clipId}' not found in any track.`);
    }
    found.track.moveClip(clipId, newStart);
  }

  public trimClip(clipId: string, newStart: Time, newEnd: Time): void {
    const found = this.getClip(clipId);
    if (!found) {
      throw new ValidationError(`Clip '${clipId}' not found in any track.`);
    }
    found.track.trimClip(clipId, newStart, newEnd);
  }

  public toJSON(): TimelineSerialization {
    return {
      duration: this.duration,
      timeBase: { ...this.timeBase },
      tracks: this._tracks.map((t) => t.toJSON()),
      markers: this._markers.map((m) => ({ ...m })),
    };
  }

  public static fromJSON(data: TimelineSerialization): VideoTimeline {
    return new VideoTimeline({
      duration: data.duration,
      timeBase: data.timeBase,
      tracks: data.tracks.map((t) => Track.fromJSON(t)),
      markers: data.markers,
    });
  }
}
