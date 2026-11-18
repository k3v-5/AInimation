import { ValidationError } from "../../errors/index.js";
import { Time } from "../../core/types.js";
import { validateNonNegativeNumber, validateTime } from "../../validation/validators.js";
import { TimeRangeData } from "../types/index.js";

/**
 * Representa un intervalo temporal continuo semicerrado [start, end) (Fase 5B).
 */
export class TimeRange {
  public readonly start: Time;
  public readonly end: Time;

  constructor(start: Time, end: Time) {
    const validStart = validateTime(start);
    const validEnd = validateTime(end);

    if (validEnd < validStart) {
      throw new ValidationError(
        `TimeRange 'end' (${validEnd}) cannot be smaller than 'start' (${validStart}).`
      );
    }

    this.start = validStart;
    this.end = validEnd;
  }

  public get duration(): Time {
    return this.end - this.start;
  }

  /**
   * Determina si un instante t cae dentro del intervalo [start, end) (inclusivo al inicio, exclusivo al final).
   */
  public contains(time: Time): boolean {
    const validTime = validateTime(time);
    return validTime >= this.start && validTime < this.end;
  }

  /**
   * Comprueba si este rango se solapa con otro rango [start, end).
   */
  public overlaps(other: TimeRange): boolean {
    return this.start < other.end && this.end > other.start;
  }

  public toJSON(): TimeRangeData {
    return {
      start: this.start,
      end: this.end,
    };
  }

  public static fromJSON(data: TimeRangeData): TimeRange {
    return new TimeRange(data.start, data.end);
  }
}
