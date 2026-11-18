import { TargetPlatform, SOCIAL_PLATFORM_PROFILES } from "../core/TargetPlatform.js";
import { AudioComplianceReport } from "./PlatformAudioProfile.js";
import { TruePeakLimiter } from "./TruePeakLimiter.js";

export class LoudnessNormalizer {
  /**
   * Calcula LUFS integrado aproximado a partir de muestras de audio.
   */
  public static measureLufs(samples: Float32Array): number {
    if (samples.length === 0) return -70.0;

    let sumSquares = 0;
    for (let i = 0; i < samples.length; i++) {
      sumSquares += samples[i] * samples[i];
    }
    const rms = Math.sqrt(sumSquares / samples.length);
    if (rms <= 0.000001) return -70.0;

    const db = 20 * Math.log10(rms);
    return Math.round(db * 10) / 10;
  }

  /**
   * Normaliza muestras de audio para cumplir con el perfil de sonoridad de la plataforma.
   */
  public static normalize(samples: Float32Array, platform: TargetPlatform): {
    normalizedSamples: Float32Array;
    report: AudioComplianceReport;
  } {
    const profile = SOCIAL_PLATFORM_PROFILES[platform];
    const initialLufs = this.measureLufs(samples);

    const gainAdjustmentDb = profile.targetLufs - initialLufs;
    const gainMultiplier = Math.pow(10, gainAdjustmentDb / 20);

    const scaled = new Float32Array(samples.length);
    let maxPeak = 0;

    for (let i = 0; i < samples.length; i++) {
      scaled[i] = samples[i] * gainMultiplier;
      const abs = Math.abs(scaled[i]);
      if (abs > maxPeak) maxPeak = abs;
    }

    const initialTruePeakDb = maxPeak > 0 ? 20 * Math.log10(maxPeak) : -70.0;

    // Aplicar True Peak Limiting a -1.0 dBTP
    const { limitedSamples } = TruePeakLimiter.limit(scaled, profile.maxTruePeakDb);
    const finalLufs = this.measureLufs(limitedSamples);

    let finalMaxPeak = 0;
    for (let i = 0; i < limitedSamples.length; i++) {
      const abs = Math.abs(limitedSamples[i]);
      if (abs > finalMaxPeak) finalMaxPeak = abs;
    }
    const finalTruePeakDb = finalMaxPeak > 0 ? 20 * Math.log10(finalMaxPeak) : -70.0;

    const report: AudioComplianceReport = {
      platform,
      targetLufs: profile.targetLufs,
      initialLufs,
      gainAdjustmentDb: Math.round(gainAdjustmentDb * 10) / 10,
      finalLufs,
      initialTruePeakDb: Math.round(initialTruePeakDb * 10) / 10,
      finalTruePeakDb: Math.round(finalTruePeakDb * 10) / 10,
      compliant: Math.abs(finalLufs - profile.targetLufs) <= 1.0 && finalTruePeakDb <= profile.maxTruePeakDb + 0.1,
    };

    return {
      normalizedSamples: limitedSamples,
      report,
    };
  }
}
