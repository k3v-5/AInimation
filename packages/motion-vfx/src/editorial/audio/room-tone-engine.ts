import { RoomToneProfile, AudioRegion } from "./audio-ir.types.js";

/**
 * REQ-063: Room Tone Continuity, Analysis & Synthesis Engine
 * Previene caídas a cero digital (VOICE -> DIGITAL SILENCE -> VOICE) mediante parches de suelo acústico derivados.
 */
export class RoomToneAnalyzer {
  /**
   * Analiza una señal de audio o metadatos acústicos para extraer el perfil de Room Tone
   */
  public static analyzeProfile(params: {
    locationId: string;
    samples?: Float32Array;
    fallbackNoiseFloorDb?: number;
  }): RoomToneProfile {
    const { locationId, samples, fallbackNoiseFloorDb = -48.0 } = params;

    let noiseFloorDb = fallbackNoiseFloorDb;
    let dominantFrequencyHz = 120.0;

    if (samples && samples.length > 0) {
      let sumSquares = 0;
      for (let i = 0; i < samples.length; i++) {
        sumSquares += samples[i] * samples[i];
      }
      const rms = Math.sqrt(sumSquares / samples.length);
      noiseFloorDb = rms > 0 ? 20 * Math.log10(rms) : -60.0;
      noiseFloorDb = Math.max(-80.0, Math.min(-20.0, Number(noiseFloorDb.toFixed(1))));
    }

    return {
      locationId,
      noiseFloorDb,
      dominantFrequencyHz,
      spectralBalanceScore: 0.85,
      suggestedPatchGainDb: noiseFloorDb - 3.0, // Ligera atenuación para no competir
      patchIntervals: [],
    };
  }
}

export class RoomToneMatcher {
  private readonly profiles: Map<string, RoomToneProfile> = new Map();

  public registerProfile(profile: RoomToneProfile): void {
    this.profiles.set(profile.locationId, profile);
  }

  public getProfileForLocation(locationId: string): RoomToneProfile {
    const profile = this.profiles.get(locationId);
    if (!profile) {
      // Perfil neutro por defecto
      return RoomToneAnalyzer.analyzeProfile({ locationId, fallbackNoiseFloorDb: -52.0 });
    }
    return profile;
  }
}

export class RoomToneSynthesizer {
  /**
   * Identifica silencios digitales entre eventos de diálogo y sintetiza regiones de relleno acústico
   */
  public static synthesizeContinuousBed(params: {
    dialogueRegions: Array<{ startSeconds: number; durationSeconds: number }>;
    timelineDurationSeconds: number;
    profile: RoomToneProfile;
  }): AudioRegion[] {
    const { dialogueRegions, timelineDurationSeconds, profile } = params;
    const sorted = [...dialogueRegions].sort((a, b) => a.startSeconds - b.startSeconds);

    const patchRegions: AudioRegion[] = [];
    let currentTime = 0;

    for (let i = 0; i < sorted.length; i++) {
      const region = sorted[i];
      const gapDuration = region.startSeconds - currentTime;

      // Si existe un espacio de silencio > 0.15s, se rellena con Room Tone
      if (gapDuration > 0.15) {
        patchRegions.push({
          id: `rt_patch_${i}_${Math.round(currentTime * 100)}`,
          clipId: `roomtone_${profile.locationId}`,
          busId: "ROOM_TONE",
          timelineRange: {
            startSeconds: Number(currentTime.toFixed(3)),
            durationSeconds: Number(gapDuration.toFixed(3)),
          },
          sourceRange: {
            startSeconds: 0,
            durationSeconds: Number(gapDuration.toFixed(3)),
          },
          gainDb: profile.suggestedPatchGainDb,
          pan: 0.0,
          fadeInSeconds: 0.05,
          fadeOutSeconds: 0.05,
          layer: "BACKGROUND",
          isRoomTonePatch: true,
        });
      }

      currentTime = region.startSeconds + region.durationSeconds;
    }

    // Relleno final hasta el término de la timeline si corresponde
    if (currentTime < timelineDurationSeconds) {
      const finalGap = timelineDurationSeconds - currentTime;
      if (finalGap > 0.15) {
        patchRegions.push({
          id: `rt_patch_tail_${Math.round(currentTime * 100)}`,
          clipId: `roomtone_${profile.locationId}`,
          busId: "ROOM_TONE",
          timelineRange: {
            startSeconds: Number(currentTime.toFixed(3)),
            durationSeconds: Number(finalGap.toFixed(3)),
          },
          sourceRange: {
            startSeconds: 0,
            durationSeconds: Number(finalGap.toFixed(3)),
          },
          gainDb: profile.suggestedPatchGainDb,
          pan: 0.0,
          fadeInSeconds: 0.05,
          fadeOutSeconds: 0.05,
          layer: "BACKGROUND",
          isRoomTonePatch: true,
        });
      }
    }

    return patchRegions;
  }
}
