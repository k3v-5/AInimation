import { SpeakerIdentity, SpeakerTrack, EmotionalProtectionState } from "./multicam.types.js";

/**
 * REQ-012 §6.1: SpeakerDetector
 * Abstracción desacoplada para detección de hablantes, energía vocal y estados emocionales.
 */
export class SpeakerDetector {
  /**
   * Construye las pistas de hablantes a partir de intervenciones y análisis de energía
   */
  public static buildSpeakerTracks(params: {
    identities: SpeakerIdentity[];
    turns: Array<{
      speakerId: string;
      startSeconds: number;
      endSeconds: number;
      emotionalState?: EmotionalProtectionState;
      energyLevel?: number;
    }>;
  }): Map<string, SpeakerTrack> {
    const tracks = new Map<string, SpeakerTrack>();

    for (const identity of params.identities) {
      tracks.set(identity.speakerId, {
        speakerId: identity.speakerId,
        identity,
        turns: [],
      });
    }

    for (const turn of params.turns) {
      let track = tracks.get(turn.speakerId);
      if (!track) {
        const fallbackIdentity: SpeakerIdentity = {
          speakerId: turn.speakerId,
          name: `Speaker ${turn.speakerId}`,
          role: "GUEST",
        };
        track = {
          speakerId: turn.speakerId,
          identity: fallbackIdentity,
          turns: [],
        };
        tracks.set(turn.speakerId, track);
      }

      track.turns.push({
        startSeconds: turn.startSeconds,
        endSeconds: turn.endSeconds,
        emotionalState: turn.emotionalState || "NONE",
        meanEnergy: turn.energyLevel !== undefined ? Math.max(0, Math.min(1, turn.energyLevel)) : 0.75,
      });
    }

    return tracks;
  }
}
