import { AudioPunctuationEvent, AudioPunctuationType } from "./audio-ir.types.js";

/**
 * REQ-069: Master Audio Punctuation Engine
 * Mapea eventos narrativos a signos de puntuación sonora cinematográfica.
 */
export class AudioPunctuationEngine {
  /**
   * Genera eventos de puntuación de audio a partir de los beats del arco narrativo
   */
  public static generatePunctuationPlan(
    beats: Array<{ id: string; type: string; timestampSeconds: number; durationSeconds?: number }>
  ): AudioPunctuationEvent[] {
    const events: AudioPunctuationEvent[] = [];

    for (const beat of beats) {
      switch (beat.type) {
        case "HOOK":
          events.push({
            id: `punc_hook_${beat.id}`,
            type: "EMPHASIS",
            timestampSeconds: beat.timestampSeconds,
            associatedBeatType: "HOOK",
            assetId: "sfx_impact_sub",
            gainDb: -3.0,
            durationSeconds: 1.5,
          });
          break;

        case "CONFLICT":
        case "ESCALATION":
          events.push({
            id: `punc_conflict_${beat.id}`,
            type: "TRANSITION",
            timestampSeconds: beat.timestampSeconds,
            associatedBeatType: beat.type,
            assetId: "sfx_whoosh_tension",
            gainDb: -6.0,
            durationSeconds: 1.0,
          });
          break;

        case "REVELATION":
          events.push({
            id: `punc_revelation_${beat.id}`,
            type: "REVELATION",
            timestampSeconds: beat.timestampSeconds,
            associatedBeatType: "REVELATION",
            assetId: "sfx_revelation_chime",
            gainDb: -2.0,
            durationSeconds: 2.5,
          });
          break;

        case "REFLECTION":
        case "RESOLUTION":
          events.push({
            id: `punc_resolution_${beat.id}`,
            type: "FULL_STOP",
            timestampSeconds: beat.timestampSeconds + (beat.durationSeconds ?? 3.0),
            associatedBeatType: beat.type,
            gainDb: 0.0,
            durationSeconds: 2.0,
          });
          break;

        default:
          break;
      }
    }

    return events.sort((a, b) => a.timestampSeconds - b.timestampSeconds);
  }
}
