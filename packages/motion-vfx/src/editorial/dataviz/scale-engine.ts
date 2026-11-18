import { normalizeNumber } from "./data-normalizer.js";
import { ScaleError, UnsupportedScaleError } from "./errors.js";
import { DataVizScale, ScaleType } from "./types.js";

/**
 * REQ-025 §14, §15, §16, §95, §96: Visual Scale & Nice Ticks Engine.
 */
export class ScaleEngine {
  public static createScale(type: string, domain: [number, number], range: [number, number]): LinearScale {
    if (type === "LOG" || type === "LOGARITHMIC") {
      throw new UnsupportedScaleError("Logarithmic scales are not supported in this engine version"); // REQ-025 §16
    }
    if (type !== "LINEAR" && type !== "TIME_LINEAR") {
      throw new ScaleError(`Unsupported scale type: ${type}`, "INVALID_SCALE_TYPE");
    }
    return new LinearScale(domain, range);
  }

  /**
   * REQ-025 §95 & §96: Deterministic "Nice Numbers" algorithm for axis ticks.
   * Preferred step multipliers: 1, 2, 2.5, 5, 10
   */
  public static generateNiceTicks(min: number, max: number, targetTicks = 5): number[] {
    if (!Number.isFinite(min) || !Number.isFinite(max)) {
      throw new ScaleError("Domain bounds must be finite numbers", "NON_FINITE_TICK_BOUNDS");
    }

    if (min === max) {
      return [normalizeNumber(min)];
    }

    const realMin = Math.min(min, max);
    const realMax = Math.max(min, max);
    const span = realMax - realMin;

    const rawStep = span / Math.max(1, targetTicks);
    const power = Math.floor(Math.log10(rawStep));
    const fraction = rawStep / Math.pow(10, power);

    let niceFraction = 1;
    if (fraction <= 1.5) {
      niceFraction = 1;
    } else if (fraction <= 2.25) {
      niceFraction = 2;
    } else if (fraction <= 3.5) {
      niceFraction = 2.5;
    } else if (fraction <= 7.5) {
      niceFraction = 5;
    } else {
      niceFraction = 10;
    }

    const step = niceFraction * Math.pow(10, power);
    const firstTick = Math.ceil(realMin / step) * step;
    const ticks: number[] = [];

    // Avoid infinite loop due to floating point precision
    const epsilon = step * 1e-6;
    for (let t = firstTick; t <= realMax + epsilon; t += step) {
      ticks.push(normalizeNumber(t));
      if (ticks.length > 50) break; // safety guard
    }

    return ticks;
  }
}

export class LinearScale {
  private readonly domainMin: number;
  private readonly domainMax: number;
  private readonly rangeMin: number;
  private readonly rangeMax: number;
  private readonly warning?: string;

  constructor(domain: [number, number], range: [number, number]) {
    if (!Number.isFinite(domain[0]) || !Number.isFinite(domain[1])) {
      throw new ScaleError("Scale domain values must be finite numbers", "INVALID_SCALE_DOMAIN");
    }
    if (!Number.isFinite(range[0]) || !Number.isFinite(range[1])) {
      throw new ScaleError("Scale range values must be finite numbers", "INVALID_SCALE_RANGE");
    }

    this.domainMin = domain[0];
    this.domainMax = domain[1];
    this.rangeMin = range[0];
    this.rangeMax = range[1];

    if (this.domainMin === this.domainMax) {
      this.warning = "CONSTANT_DOMAIN"; // REQ-025 §15
    }
  }

  public map(x: number): number {
    if (!Number.isFinite(x)) {
      throw new ScaleError(`Cannot map non-finite value: ${x}`, "NON_FINITE_INPUT");
    }

    // Constant domain: place at exact midpoint of visual range (§15)
    if (this.domainMin === this.domainMax) {
      return normalizeNumber((this.rangeMin + this.rangeMax) / 2.0);
    }

    const t = (x - this.domainMin) / (this.domainMax - this.domainMin);
    const rawPixel = this.rangeMin + t * (this.rangeMax - this.rangeMin);

    // Clamp to visual range bounds
    const lower = Math.min(this.rangeMin, this.rangeMax);
    const upper = Math.max(this.rangeMin, this.rangeMax);
    const clamped = Math.max(lower, Math.min(upper, rawPixel));

    return normalizeNumber(clamped);
  }

  public invert(pixel: number): number {
    if (!Number.isFinite(pixel)) {
      throw new ScaleError(`Cannot invert non-finite pixel: ${pixel}`, "NON_FINITE_PIXEL");
    }
    if (this.rangeMin === this.rangeMax) {
      return normalizeNumber(this.domainMin);
    }
    const t = (pixel - this.rangeMin) / (this.rangeMax - this.rangeMin);
    const rawVal = this.domainMin + t * (this.domainMax - this.domainMin);
    return normalizeNumber(rawVal);
  }

  public getDomain(): [number, number] {
    return [this.domainMin, this.domainMax];
  }

  public getRange(): [number, number] {
    return [this.rangeMin, this.rangeMax];
  }

  public getWarning(): string | undefined {
    return this.warning;
  }

  public toIRScale(id: string): DataVizScale {
    return {
      id,
      type: "LINEAR",
      domain: [this.domainMin, this.domainMax],
      range: [this.rangeMin, this.rangeMax],
      warning: this.warning,
    };
  }
}
