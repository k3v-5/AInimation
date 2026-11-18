/**
 * REQ-025 §9: Escalas matemáticas deterministas.
 * Manejo estricto de clamps en [0.0, 1.0] y cálculo del cruce en cero.
 */

export class LinearScale {
  public readonly min: number;
  public readonly max: number;
  public readonly hasZero: boolean;
  public readonly zeroNormalized: number;

  constructor(min: number, max: number) {
    if (!Number.isFinite(min) || !Number.isFinite(max)) {
      this.min = 0;
      this.max = 1;
    } else if (min > max) {
      this.min = max;
      this.max = min;
    } else {
      this.min = min;
      this.max = max;
    }

    this.hasZero = this.min <= 0 && this.max >= 0;

    if (this.max === this.min) {
      this.zeroNormalized = 0.5;
    } else if (this.min >= 0) {
      this.zeroNormalized = (0 - this.min) / (this.max - this.min);
      if (this.zeroNormalized < 0) this.zeroNormalized = 0;
    } else if (this.max <= 0) {
      this.zeroNormalized = (0 - this.min) / (this.max - this.min);
      if (this.zeroNormalized > 1) this.zeroNormalized = 1;
    } else {
      this.zeroNormalized = (0 - this.min) / (this.max - this.min);
    }
  }

  public scale(value: number): number {
    if (!Number.isFinite(value)) return 0;
    if (this.max === this.min) return 0.5;

    let norm = (value - this.min) / (this.max - this.min);
    if (norm < 0) norm = 0;
    if (norm > 1) norm = 1;
    return Math.round(norm * 10000) / 10000;
  }

  public invert(normalized: number): number {
    const clamped = Math.max(0, Math.min(1, normalized));
    if (this.max === this.min) return this.min;
    return this.min + clamped * (this.max - this.min);
  }

  public mapToPixel(value: number, pixelStart: number, pixelEnd: number): number {
    const norm = this.scale(value);
    return pixelStart + norm * (pixelEnd - pixelStart);
  }
}

export class LogarithmicScale {
  public readonly min: number;
  public readonly max: number;

  constructor(min: number, max: number) {
    this.min = min <= 0 ? 0.001 : min;
    this.max = max <= min ? this.min * 10 : max;
  }

  public scale(value: number): number {
    if (!Number.isFinite(value) || value <= 0) return 0;
    const clampedVal = Math.max(this.min, Math.min(this.max, value));
    const logMin = Math.log10(this.min);
    const logMax = Math.log10(this.max);
    if (logMax === logMin) return 0.5;
    const norm = (Math.log10(clampedVal) - logMin) / (logMax - logMin);
    return Math.max(0, Math.min(1, Math.round(norm * 10000) / 10000));
  }
}

export class BandScale {
  public readonly domain: string[];
  public readonly paddingInner: number;
  public readonly paddingOuter: number;

  constructor(domain: string[], paddingInner = 0.2, paddingOuter = 0.1) {
    this.domain = [...domain];
    this.paddingInner = Math.max(0, Math.min(0.9, paddingInner));
    this.paddingOuter = Math.max(0, Math.min(0.9, paddingOuter));
  }

  public getBandwidth(totalDimension: number): number {
    const n = this.domain.length;
    if (n === 0) return totalDimension;
    const step = totalDimension / (n - this.paddingInner + 2 * this.paddingOuter);
    return Math.max(1, step * (1 - this.paddingInner));
  }

  public getStep(totalDimension: number): number {
    const n = this.domain.length;
    if (n === 0) return totalDimension;
    return totalDimension / (n - this.paddingInner + 2 * this.paddingOuter);
  }

  public getPosition(category: string, totalDimension: number, pixelOffset = 0): number {
    const index = this.domain.indexOf(category);
    if (index === -1) return pixelOffset;
    const step = this.getStep(totalDimension);
    return pixelOffset + (this.paddingOuter + index) * step;
  }
}
