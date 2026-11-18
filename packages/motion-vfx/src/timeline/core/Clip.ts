import { generateDeterministicLayerId } from "../../core/id.js";
import { Time } from "../../core/types.js";
import { ValidationError } from "../../errors/index.js";
import { validateId } from "../../validation/validators.js";
import { ClipSerialization } from "../types/index.js";
import { TimeRange } from "./TimeRange.js";

export interface ClipOptions {
  id?: string;
  name?: string;
  elementId: string;
  timelineRange: TimeRange | { start: Time; end: Time };
  sourceRange?: TimeRange | { start: Time; end: Time };
  speed?: number;
  trackId?: string;
}

/**
 * Representa una aparición temporal de un elemento en la línea de tiempo (Fase 5B).
 */
export class Clip {
  public readonly id: string;
  public name?: string;
  public elementId: string;
  public timelineRange: TimeRange;
  public sourceRange?: TimeRange;
  public speed: number;
  public trackId?: string;

  constructor(options: ClipOptions) {
    this.id = options.id ? validateId(options.id, "clip.id") : `clip_${generateDeterministicLayerId()}`;
    this.name = options.name;
    this.elementId = validateId(options.elementId, "elementId");

    this.timelineRange =
      options.timelineRange instanceof TimeRange
        ? options.timelineRange
        : new TimeRange(options.timelineRange.start, options.timelineRange.end);

    this.sourceRange = options.sourceRange
      ? options.sourceRange instanceof TimeRange
        ? options.sourceRange
        : new TimeRange(options.sourceRange.start, options.sourceRange.end)
      : undefined;

    this.speed = options.speed !== undefined ? options.speed : 1.0;
    if (this.speed <= 0) {
      throw new ValidationError(`Clip speed must be greater than 0. Received: ${this.speed}`);
    }

    this.trackId = options.trackId;
  }

  /**
   * Determina si el clip está activo en el tiempo global dado [start, end).
   */
  public isActive(globalTime: Time): boolean {
    return this.timelineRange.contains(globalTime);
  }

  /**
   * Calcula el tiempo relativo local del clip respecto a su inicio.
   */
  public getLocalTime(globalTime: Time): Time {
    return globalTime - this.timelineRange.start;
  }

  /**
   * Calcula el tiempo correspondiente en el medio fuente original.
   */
  public getSourceTime(globalTime: Time): Time | undefined {
    if (!this.sourceRange) return undefined;
    const localTime = this.getLocalTime(globalTime);
    return this.sourceRange.start + localTime * this.speed;
  }

  /**
   * Divide este clip en dos sub-clips en el punto de corte `splitTime`.
   * Conserva el mapeo proporcional al sourceRange.
   */
  public split(splitTime: Time): [Clip, Clip] {
    if (!this.isActive(splitTime) || splitTime === this.timelineRange.start) {
      throw new ValidationError(
        `Split time ${splitTime} must fall strictly within clip range [${this.timelineRange.start}, ${this.timelineRange.end}).`
      );
    }

    const firstTimelineRange = new TimeRange(this.timelineRange.start, splitTime);
    const secondTimelineRange = new TimeRange(splitTime, this.timelineRange.end);

    let firstSourceRange: TimeRange | undefined;
    let secondSourceRange: TimeRange | undefined;

    if (this.sourceRange) {
      const splitOffset = (splitTime - this.timelineRange.start) * this.speed;
      const midSource = this.sourceRange.start + splitOffset;
      firstSourceRange = new TimeRange(this.sourceRange.start, midSource);
      secondSourceRange = new TimeRange(midSource, this.sourceRange.end);
    }

    const clip1 = new Clip({
      id: `${this.id}_part1`,
      name: this.name ? `${this.name} (Part 1)` : undefined,
      elementId: this.elementId,
      timelineRange: firstTimelineRange,
      sourceRange: firstSourceRange,
      speed: this.speed,
      trackId: this.trackId,
    });

    const clip2 = new Clip({
      id: `${this.id}_part2`,
      name: this.name ? `${this.name} (Part 2)` : undefined,
      elementId: this.elementId,
      timelineRange: secondTimelineRange,
      sourceRange: secondSourceRange,
      speed: this.speed,
      trackId: this.trackId,
    });

    return [clip1, clip2];
  }

  public toJSON(): ClipSerialization {
    return {
      id: this.id,
      name: this.name,
      elementId: this.elementId,
      timelineRange: this.timelineRange.toJSON(),
      sourceRange: this.sourceRange ? this.sourceRange.toJSON() : undefined,
      speed: this.speed,
      trackId: this.trackId,
    };
  }

  public static fromJSON(data: ClipSerialization): Clip {
    return new Clip({
      id: data.id,
      name: data.name,
      elementId: data.elementId,
      timelineRange: TimeRange.fromJSON(data.timelineRange),
      sourceRange: data.sourceRange ? TimeRange.fromJSON(data.sourceRange) : undefined,
      speed: data.speed,
      trackId: data.trackId,
    });
  }
}
