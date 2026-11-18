/**
 * REQ-036 §5.1: Rational Timebase & Framerate Engine for OpenTimelineIO
 */

export interface RationalFramerate {
  nominalFps: number;
  rateNumerator: number;
  rateDenominator: number;
  effectiveFps: number;
}

export const STANDARD_FRAMERATES: Record<number | string, RationalFramerate> = {
  23.976: { nominalFps: 23.976, rateNumerator: 24000, rateDenominator: 1001, effectiveFps: 23.976023976 },
  24: { nominalFps: 24, rateNumerator: 24, rateDenominator: 1, effectiveFps: 24.0 },
  25: { nominalFps: 25, rateNumerator: 25, rateDenominator: 1, effectiveFps: 25.0 },
  29.97: { nominalFps: 29.97, rateNumerator: 30000, rateDenominator: 1001, effectiveFps: 29.97002997 },
  30: { nominalFps: 30, rateNumerator: 30, rateDenominator: 1, effectiveFps: 30.0 },
  50: { nominalFps: 50, rateNumerator: 50, rateDenominator: 1, effectiveFps: 50.0 },
  59.94: { nominalFps: 59.94, rateNumerator: 60000, rateDenominator: 1001, effectiveFps: 59.94005994 },
  60: { nominalFps: 60, rateNumerator: 60, rateDenominator: 1, effectiveFps: 60.0 },
};

export class OtioTimeEngine {
  public static getRationalRate(fps: number): RationalFramerate {
    const match = STANDARD_FRAMERATES[fps] || STANDARD_FRAMERATES[Number(fps.toFixed(2))] || STANDARD_FRAMERATES[Number(fps.toFixed(3))];
    if (match) return match;

    // Si no es un valor estándar conocido, se asume entero o división exacta
    return {
      nominalFps: fps,
      rateNumerator: Math.round(fps * 1000),
      rateDenominator: 1000,
      effectiveFps: fps,
    };
  }

  public static secondsToFrames(seconds: number, fps: number): number {
    const rational = this.getRationalRate(fps);
    return Math.round(seconds * (rational.rateNumerator / rational.rateDenominator));
  }

  public static framesToSeconds(frames: number, fps: number): number {
    const rational = this.getRationalRate(fps);
    return Number((frames * (rational.rateDenominator / rational.rateNumerator)).toFixed(6));
  }
}
