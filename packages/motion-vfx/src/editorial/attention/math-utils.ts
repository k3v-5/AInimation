import crypto from "node:crypto";

/**
 * Reusable mathematical utilities and canonical cryptographic serializer for the attention suite.
 */
export class MathUtils {
  /**
   * Clamps a value into [min, max], normalizing -0 to 0 and rejecting non-finite values.
   */
  public static clamp(val: number, min: number, max: number): number {
    if (!Number.isFinite(val)) {
      throw new Error(`Invalid non-finite number passed to clamp: ${val}`);
    }
    if (Object.is(val, -0)) {
      val = 0;
    }
    return Math.max(min, Math.min(max, val));
  }

  /**
   * Analytic solution to dA/dt = -lambda * (A - A_base):
   * A(t) = A_base + (current - A_base) * exp(-lambda * dt)
   */
  public static exponentialDecay(
    current: number,
    baseline: number,
    lambda: number,
    dtSeconds: number
  ): number {
    const c = this.clamp(current, 0.0, 1.0);
    const b = this.clamp(baseline, 0.0, 1.0);
    const l = Math.max(0.0, lambda);
    const dt = Math.max(0.0, dtSeconds);

    const result = b + (c - b) * Math.exp(-l * dt);
    return this.clamp(Number(result.toFixed(4)), 0.0, 1.0);
  }

  /**
   * Commutative, order-independent stimulus composition:
   * A' = 1 - (1 - A) * PROD(1 - k_i)
   */
  public static composeStimuli(current: number, stimuliCoefficients: number[]): number {
    const c = this.clamp(current, 0.0, 1.0);
    if (stimuliCoefficients.length === 0) {
      return c;
    }

    let prod = 1.0 - c;
    for (const k of stimuliCoefficients) {
      const clampedK = this.clamp(k, 0.0, 0.9999);
      prod *= 1.0 - clampedK;
    }

    const composed = 1.0 - prod;
    return this.clamp(Number(composed.toFixed(4)), 0.0, 1.0);
  }

  /**
   * Recursively canonicalizes an object or array:
   * - Keys sorted lexicographically
   * - Numbers formatted to fixed 4 decimals and normalized (-0 -> 0)
   * - Non-finite numbers rejected
   * - Undefined fields and 'checksumSha256' omitted
   */
  public static canonicalize(val: unknown): unknown {
    if (val === null || val === undefined) {
      return val;
    }

    if (typeof val === "number") {
      if (!Number.isFinite(val)) {
        throw new Error(`Cannot canonicalize non-finite number: ${val}`);
      }
      if (Object.is(val, -0)) {
        return 0;
      }
      return Number(val.toFixed(4));
    }

    if (typeof val === "string" || typeof val === "boolean") {
      return val;
    }

    if (Array.isArray(val)) {
      return val.map((item) => this.canonicalize(item));
    }

    if (typeof val === "object") {
      const sortedKeys = Object.keys(val as Record<string, unknown>).sort();
      const result: Record<string, unknown> = {};

      for (const key of sortedKeys) {
        if (key === "checksumSha256") {
          continue; // Exclude checksum from its own payload
        }
        const itemVal = (val as Record<string, unknown>)[key];
        if (itemVal !== undefined) {
          result[key] = this.canonicalize(itemVal);
        }
      }

      return result;
    }

    return String(val);
  }

  /**
   * Deterministic stringification of canonicalized data.
   */
  public static canonicalStringify(val: unknown): string {
    return JSON.stringify(this.canonicalize(val));
  }

  /**
   * Computes deterministic SHA-256 over the canonical string representation.
   */
  public static computeCanonicalSha256(val: unknown): string {
    const str = this.canonicalStringify(val);
    return crypto.createHash("sha256").update(str).digest("hex");
  }
}
