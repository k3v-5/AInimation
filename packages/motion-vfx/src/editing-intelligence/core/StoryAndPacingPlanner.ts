import { PacingProfile, PacingProfileType } from "../types/index.js";

export const BuiltinPacingProfiles: Record<PacingProfileType, PacingProfile> = {
  fast_social: {
    name: "fast_social",
    averageShotDuration: 2.0,
    minShotDuration: 1.2,
    maxShotDuration: 3.5,
    motionDensity: 0.85,
    sfxDensity: 0.9,
  },
  medium_social: {
    name: "medium_social",
    averageShotDuration: 3.5,
    minShotDuration: 2.0,
    maxShotDuration: 5.0,
    motionDensity: 0.65,
    sfxDensity: 0.7,
  },
  educational: {
    name: "educational",
    averageShotDuration: 5.0,
    minShotDuration: 3.0,
    maxShotDuration: 8.0,
    motionDensity: 0.45,
    sfxDensity: 0.5,
  },
  cinematic: {
    name: "cinematic",
    averageShotDuration: 6.5,
    minShotDuration: 4.0,
    maxShotDuration: 12.0,
    motionDensity: 0.35,
    sfxDensity: 0.4,
  },
};

/**
 * Planificador narrativo y motor de ritmo editorial (*Pacing Engine*) (Fase 14).
 */
export class StoryAndPacingPlanner {
  public static getPacingProfile(type: PacingProfileType): PacingProfile {
    return BuiltinPacingProfiles[type] ?? BuiltinPacingProfiles.fast_social;
  }

  /**
   * Calcula la duración ideal de tomas segmentadas a lo largo de la duración total.
   */
  public static planShotDurations(
    totalDuration: number,
    profileType: PacingProfileType
  ): number[] {
    const profile = this.getPacingProfile(profileType);
    const durations: number[] = [];
    let remaining = totalDuration;

    while (remaining > 0) {
      const shotDur = Math.min(remaining, profile.averageShotDuration);
      durations.push(Math.round(shotDur * 100) / 100);
      remaining -= shotDur;
    }

    return durations;
  }
}
