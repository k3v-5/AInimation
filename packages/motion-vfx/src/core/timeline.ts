import { validateNonNegativeNumber, validatePositiveNumber, validateTime } from "../validation/validators.js";
import { Time } from "./types.js";

/**
 * Utilidad de conversión entre tiempo continuo y frames cuantizados.
 */
export class Timeline {
  public readonly fps: number;
  public readonly duration: Time;

  constructor(fps: number, duration: Time) {
    this.fps = validatePositiveNumber(fps, "timeline.fps");
    this.duration = validateNonNegativeNumber(duration, "timeline.duration");
  }

  /**
   * Convierte un número de frame a tiempo continuo en segundos.
   */
  public frameToTime(frame: number): Time {
    if (typeof frame !== "number" || !Number.isFinite(frame) || Number.isNaN(frame)) {
      throw new Error(`Frame must be a finite number. Received: ${String(frame)}`);
    }
    return frame / this.fps;
  }

  /**
   * Convierte un tiempo en segundos al frame redondeado más cercano.
   */
  public timeToFrame(time: Time): number {
    const validTime = validateTime(time);
    return Math.round(validTime * this.fps);
  }

  /**
   * Calcula el número total de frames de la duración.
   */
  public totalFrames(): number {
    return Math.round(this.duration * this.fps);
  }
}
