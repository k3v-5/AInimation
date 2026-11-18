import { getEasing } from "../../animation/easing.js";
import { generateDeterministicLayerId } from "../../core/id.js";
import { Time } from "../../core/types.js";
import { ValidationError } from "../../errors/index.js";
import { TimeRange } from "../../timeline/core/TimeRange.js";
import { validateId } from "../../validation/validators.js";
import { AudioClipSerialization, FadeConfig } from "../types/index.js";
import { AudioMath } from "./AudioMath.js";

export interface AudioClipOptions {
  id?: string;
  name?: string;
  assetId: string;
  timelineRange: TimeRange | { start: Time; end: Time };
  sourceRange?: TimeRange | { start: Time; end: Time };
  speed?: number;
  volume?: number;
  gainDb?: number;
  pan?: number;
  fadeIn?: FadeConfig;
  fadeOut?: FadeConfig;
  muted?: boolean;
}

/**
 * Instancia temporal de un activo de audio en la línea de tiempo (Fase 5D).
 */
export class AudioClip {
  public readonly id: string;
  public name?: string;
  public assetId: string;
  public timelineRange: TimeRange;
  public sourceRange: TimeRange;
  public speed: number;
  public volume: number;
  public gainDb: number;
  public pan: number;
  public fadeIn?: FadeConfig;
  public fadeOut?: FadeConfig;
  public muted: boolean;

  constructor(options: AudioClipOptions) {
    this.id = options.id ? validateId(options.id, "audioClip.id") : `aclip_${generateDeterministicLayerId()}`;
    this.name = options.name;
    this.assetId = validateId(options.assetId, "assetId");

    this.timelineRange =
      options.timelineRange instanceof TimeRange
        ? options.timelineRange
        : new TimeRange(options.timelineRange.start, options.timelineRange.end);

    const dur = this.timelineRange.duration;
    this.sourceRange = options.sourceRange
      ? options.sourceRange instanceof TimeRange
        ? options.sourceRange
        : new TimeRange(options.sourceRange.start, options.sourceRange.end)
      : new TimeRange(0, dur);

    this.speed = options.speed !== undefined ? options.speed : 1.0;
    this.volume = options.volume !== undefined ? Math.max(0, options.volume) : 1.0;
    this.gainDb = options.gainDb !== undefined ? options.gainDb : 0.0;
    this.pan = options.pan !== undefined ? Math.max(-1, Math.min(1, options.pan)) : 0.0;
    this.fadeIn = options.fadeIn;
    this.fadeOut = options.fadeOut;
    this.muted = options.muted ?? false;
  }

  public isActive(globalTime: Time): boolean {
    return this.timelineRange.contains(globalTime);
  }

  public getLocalTime(globalTime: Time): Time {
    return globalTime - this.timelineRange.start;
  }

  public getSourceTime(globalTime: Time): Time {
    const local = this.getLocalTime(globalTime);
    return this.sourceRange.start + local * this.speed;
  }

  /**
   * Calcula la ganancia efectiva total (volume * dbToGain * fades) para el instante local del clip.
   */
  public getGainAtTime(localTime: Time): number {
    if (this.muted || localTime < 0 || localTime >= this.timelineRange.duration) {
      return 0.0;
    }

    let fadeMultiplier = 1.0;

    // Fade In
    if (this.fadeIn && this.fadeIn.duration > 0 && localTime < this.fadeIn.duration) {
      const p = Math.max(0, Math.min(1, localTime / this.fadeIn.duration));
      const easingFn = getEasing(this.fadeIn.easing ?? "linear");
      fadeMultiplier *= easingFn(p);
    }

    // Fade Out
    if (this.fadeOut && this.fadeOut.duration > 0) {
      const timeUntilEnd = this.timelineRange.duration - localTime;
      if (timeUntilEnd < this.fadeOut.duration) {
        const p = Math.max(0, Math.min(1, timeUntilEnd / this.fadeOut.duration));
        const easingFn = getEasing(this.fadeOut.easing ?? "linear");
        fadeMultiplier *= easingFn(p);
      }
    }

    return this.volume * AudioMath.dbToGain(this.gainDb) * fadeMultiplier;
  }

  public toJSON(): AudioClipSerialization {
    return {
      id: this.id,
      name: this.name,
      assetId: this.assetId,
      timelineRange: this.timelineRange.toJSON(),
      sourceRange: this.sourceRange.toJSON(),
      speed: this.speed,
      volume: this.volume,
      gainDb: this.gainDb,
      pan: this.pan,
      fadeIn: this.fadeIn ? { ...this.fadeIn } : undefined,
      fadeOut: this.fadeOut ? { ...this.fadeOut } : undefined,
      muted: this.muted,
    };
  }

  public static fromJSON(data: AudioClipSerialization): AudioClip {
    return new AudioClip({
      id: data.id,
      name: data.name,
      assetId: data.assetId,
      timelineRange: TimeRange.fromJSON(data.timelineRange),
      sourceRange: TimeRange.fromJSON(data.sourceRange),
      speed: data.speed,
      volume: data.volume,
      gainDb: data.gainDb,
      pan: data.pan,
      fadeIn: data.fadeIn,
      fadeOut: data.fadeOut,
      muted: data.muted,
    });
  }
}
