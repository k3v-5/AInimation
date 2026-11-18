export class TruePeakLimiter {
  /**
   * Limita muestras de audio de forma determinista para no exceder el umbral de True Peak (-1.0 dBTP = ~0.891).
   */
  public static limit(samples: Float32Array, maxPeakDb = -1.0): { limitedSamples: Float32Array; peakReduced: boolean } {
    const maxLinear = Math.pow(10, maxPeakDb / 20);
    const out = new Float32Array(samples.length);
    let peakReduced = false;

    for (let i = 0; i < samples.length; i++) {
      const absVal = Math.abs(samples[i]);
      if (absVal > maxLinear) {
        out[i] = Math.sign(samples[i]) * maxLinear;
        peakReduced = true;
      } else {
        out[i] = samples[i];
      }
    }

    return { limitedSamples: out, peakReduced };
  }
}
