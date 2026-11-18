import { generateDeterministicLayerId } from "../../core/id.js";
import { Time } from "../../core/types.js";
import { ValidationError } from "../../errors/index.js";
import { validateId } from "../../validation/validators.js";
import { AudioTrackSerialization, DuckingConfig } from "../types/index.js";
import { AudioClip } from "./AudioClip.js";

export interface AudioTrackOptions {
  id?: string;
  name?: string;
  gainDb?: number;
  pan?: number;
  muted?: boolean;
  solo?: boolean;
  ducking?: DuckingConfig;
  clips?: AudioClip[];
}

/**
 * Pista de audio para mezcla de música, voz (voiceover) o efectos (SFX) (Fase 5D).
 */
export class AudioTrack {
  public readonly id: string;
  public name: string;
  public gainDb: number;
  public pan: number;
  public muted: boolean;
  public solo: boolean;
  public ducking?: DuckingConfig;
  private _clips: AudioClip[] = [];

  constructor(options: AudioTrackOptions = {}) {
    this.id = options.id ? validateId(options.id, "audioTrack.id") : `atrack_${generateDeterministicLayerId()}`;
    this.name = options.name ?? `Audio Track ${this.id}`;
    this.gainDb = options.gainDb !== undefined ? options.gainDb : 0.0;
    this.pan = options.pan !== undefined ? Math.max(-1, Math.min(1, options.pan)) : 0.0;
    this.muted = options.muted ?? false;
    this.solo = options.solo ?? false;
    this.ducking = options.ducking ? { ...options.ducking } : undefined;

    if (options.clips) {
      for (const clip of options.clips) {
        this.addClip(clip);
      }
    }
  }

  public get clips(): AudioClip[] {
    return [...this._clips];
  }

  public get size(): number {
    return this._clips.length;
  }

  public addClip(clip: AudioClip): this {
    this._clips.push(clip);
    this._clips.sort((a, b) => a.timelineRange.start - b.timelineRange.start);
    return this;
  }

  public removeClip(clipId: string): boolean {
    const idx = this._clips.findIndex((c) => c.id === clipId);
    if (idx !== -1) {
      this._clips.splice(idx, 1);
      return true;
    }
    return false;
  }

  public getClip(clipId: string): AudioClip | undefined {
    return this._clips.find((c) => c.id === clipId);
  }

  public getActiveClips(globalTime: Time): AudioClip[] {
    if (this.muted) return [];
    return this._clips.filter((c) => c.isActive(globalTime));
  }

  public toJSON(): AudioTrackSerialization {
    return {
      id: this.id,
      name: this.name,
      gainDb: this.gainDb,
      pan: this.pan,
      muted: this.muted,
      solo: this.solo,
      ducking: this.ducking ? { ...this.ducking } : undefined,
      clips: this._clips.map((c) => c.toJSON()),
    };
  }

  public static fromJSON(data: AudioTrackSerialization): AudioTrack {
    return new AudioTrack({
      id: data.id,
      name: data.name,
      gainDb: data.gainDb,
      pan: data.pan,
      muted: data.muted,
      solo: data.solo,
      ducking: data.ducking,
      clips: data.clips.map((c) => AudioClip.fromJSON(c)),
    });
  }
}
