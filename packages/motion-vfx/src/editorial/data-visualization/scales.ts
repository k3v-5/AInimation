import { ScaleType } from "./types.js";

/**
 * REQ-025 §14, §15, §40: Escaladores deterministas de mapeo de datos a coordenadas de pantalla.
 */

export class VisualScales {
  public static linear(
    value: number,
    domainMin: number,
    domainMax: number,
    rangeMin: number,
    rangeMax: number
  ): number {
    if (domainMax === domainMin) return (rangeMin + rangeMax) / 2;
    const norm = (value - domainMin) / (domainMax - domainMin);
    return rangeMin + norm * (rangeMax - rangeMin);
  }

  public static ordinal(
    index: number,
    totalCount: number,
    rangeMin: number,
    rangeMax: number
  ): { position: number; bandWidth: number } {
    if (totalCount <= 0) return { position: rangeMin, bandWidth: 0 };
    const step = (rangeMax - rangeMin) / totalCount;
    const bandWidth = step * 0.75;
    const position = rangeMin + index * step + (step - bandWidth) / 2;
    return { position, bandWidth };
  }
}

/**
 * REQ-025 §8.1: Linear Scale con inversión vertical para composición After Effects.
 *
 * Fórmula de inversión:
 *   y = y_max - ((x - x_min) / (x_max - x_min)) * (y_max - y_min)
 */
export class LinearScale {
  public readonly min: number;
  public readonly max: number;
  public readonly pixelStart: number;
  public readonly pixelEnd: number;
  public readonly invertVertical: boolean;

  constructor(
    minOrDomain: number | { min: number; max: number },
    maxOrRange: number | { min: number; max: number },
    pixelStartOrInvert: number | boolean = 0,
    pixelEnd = 1080,
    invertVertical = false
  ) {
    if (typeof minOrDomain === "object" && typeof maxOrRange === "object") {
      this.min = minOrDomain.min;
      this.max = minOrDomain.max;
      this.pixelStart = maxOrRange.min;
      this.pixelEnd = maxOrRange.max;
      this.invertVertical = Boolean(pixelStartOrInvert);
    } else {
      this.min = Number(minOrDomain);
      this.max = Number(maxOrRange);
      this.pixelStart = Number(pixelStartOrInvert);
      this.pixelEnd = Number(pixelEnd);
      this.invertVertical = Boolean(invertVertical);
    }
  }

  public map(value: number): number {
    if (!Number.isFinite(value)) return (this.pixelStart + this.pixelEnd) / 2;
    if (Math.abs(this.max - this.min) < 1e-12) {
      return (this.pixelStart + this.pixelEnd) / 2;
    }

    const t = (value - this.min) / (this.max - this.min);
    if (this.invertVertical) {
      return this.pixelEnd - t * (this.pixelEnd - this.pixelStart);
    }
    return this.pixelStart + t * (this.pixelEnd - this.pixelStart);
  }

  public scale(value: number): number {
    return this.map(value);
  }

  public invert(pixel: number): number {
    if (Math.abs(this.pixelEnd - this.pixelStart) < 1e-12) return this.min;
    let t: number;
    if (this.invertVertical) {
      t = (this.pixelEnd - pixel) / (this.pixelEnd - this.pixelStart);
    } else {
      t = (pixel - this.pixelStart) / (this.pixelEnd - this.pixelStart);
    }
    return this.min + t * (this.max - this.min);
  }

  public get zeroPixel(): number {
    return this.map(0);
  }

  public getZeroBaseline(): number {
    if (this.min > 0) {
      // Estrictamente positivo: el baseline es el fondo del dominio
      return this.invertVertical ? this.pixelEnd : this.pixelStart;
    }
    if (this.max < 0) {
      // Estrictamente negativo: el baseline es el tope
      return this.invertVertical ? this.pixelStart : this.pixelEnd;
    }
    return this.map(0);
  }
}

/**
 * REQ-025 §8.2: Time Scale para mapeo proporcional de timestamps.
 *
 * Fórmula:
 *   x(t) = x_min + ((t - t_min) / (t_max - t_min)) * (x_max - x_min)
 */
export class TimeScale {
  public readonly tMin: number;
  public readonly tMax: number;
  public readonly pixelStart: number;
  public readonly pixelEnd: number;

  constructor(
    tMinOrDomain: number | { minTime: number; maxTime: number },
    tMaxOrRange: number | { min: number; max: number },
    pixelStart = 0,
    pixelEnd = 1920
  ) {
    if (typeof tMinOrDomain === "object" && typeof tMaxOrRange === "object") {
      this.tMin = tMinOrDomain.minTime;
      this.tMax = tMinOrDomain.maxTime;
      this.pixelStart = tMaxOrRange.min;
      this.pixelEnd = tMaxOrRange.max;
    } else {
      this.tMin = Number(tMinOrDomain);
      this.tMax = Number(tMaxOrRange);
      this.pixelStart = Number(pixelStart);
      this.pixelEnd = Number(pixelEnd);
    }
  }

  public map(timestamp: number): number {
    if (!Number.isFinite(timestamp)) return (this.pixelStart + this.pixelEnd) / 2;
    if (Math.abs(this.tMax - this.tMin) < 1e-12) {
      return (this.pixelStart + this.pixelEnd) / 2;
    }

    const t = (timestamp - this.tMin) / (this.tMax - this.tMin);
    return this.pixelStart + t * (this.pixelEnd - this.pixelStart);
  }

  public scale(timestamp: number): number {
    return this.map(timestamp);
  }
}

/**
 * REQ-025 §8.3: Ordinal Scale para distribución uniforme de categorías.
 *
 * Fórmula:
 *   x_i = x_min + ((i + 0.5) / N) * (x_max - x_min)
 */
export class OrdinalScale {
  public readonly count: number;
  public readonly pixelStart: number;
  public readonly pixelEnd: number;
  public readonly paddingRatio: number;
  private readonly categoryMap: Map<string, number> = new Map();

  constructor(
    countOrCategories: number | string[],
    pixelStartOrRange: number | { min: number; max: number },
    pixelEndOrPadding: number = 1920,
    paddingRatio = 0.2
  ) {
    if (Array.isArray(countOrCategories)) {
      this.count = Math.max(1, countOrCategories.length);
      for (let i = 0; i < countOrCategories.length; i++) {
        this.categoryMap.set(countOrCategories[i], i);
      }
      const range = typeof pixelStartOrRange === "object" ? pixelStartOrRange : { min: 0, max: 1920 };
      this.pixelStart = range.min;
      this.pixelEnd = range.max;
      this.paddingRatio = typeof pixelEndOrPadding === "number" ? pixelEndOrPadding : 0.2;
    } else {
      this.count = Math.max(1, Number(countOrCategories));
      this.pixelStart = typeof pixelStartOrRange === "number" ? pixelStartOrRange : 0;
      this.pixelEnd = Number(pixelEndOrPadding);
      this.paddingRatio = paddingRatio;
    }
  }

  public getBandCenter(index: number): number {
    const i = Math.max(0, Math.min(index, this.count - 1));
    return this.pixelStart + ((i + 0.5) / this.count) * (this.pixelEnd - this.pixelStart);
  }

  public scale(categoryOrIndex: string | number): number {
    let idx: number;
    if (typeof categoryOrIndex === "number") {
      idx = categoryOrIndex;
    } else {
      idx = this.categoryMap.get(categoryOrIndex) ?? 0;
    }
    return this.getBandCenter(idx);
  }

  public getBandwidth(paddingRatio?: number): number {
    const pad = paddingRatio !== undefined ? paddingRatio : this.paddingRatio;
    const totalSpan = Math.abs(this.pixelEnd - this.pixelStart);
    const step = totalSpan / this.count;
    return step * (1 - pad);
  }

  public bandwidth(): number {
    return this.getBandwidth();
  }

  public step(): number {
    return Math.abs(this.pixelEnd - this.pixelStart) / this.count;
  }
}
