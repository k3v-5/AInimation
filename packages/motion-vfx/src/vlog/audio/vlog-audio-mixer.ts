import crypto from "node:crypto";
import {
  AudioMixConfig,
  AudioMixConfigSchema,
  VlogAudioTrack,
} from "../contracts/audio.types.js";
import { AUDIO_SPECS } from "../contracts/vlog.constants.js";
import { AudioDuckingEngine, DialogueInterval, DuckingOptions } from "./audio-ducking-engine.js";

export interface AudioTrackDescriptor {
  id: string;
  name: string;
  type: "VOICE" | "CRITICAL_SFX" | "MUSIC" | "AMBIENCE";
  audioFilePath: string;
  timelineStartSeconds: number;
  timelineEndSeconds: number;
  customVolumeDb?: number;
}

export interface AudioMixPlan {
  projectId: string;
  locale: string;
  tracks: VlogAudioTrack[];
  config: AudioMixConfig;
  checksumSha256: string;
}

/**
 * Mezclador de Audio Jerárquico y Planificador de Buses (Milestone 7).
 * Coordina buses para Diálogo (0dB), Música (-14dB con Ducking a -10dB), SFX (-3dB)
 * y Ambiente (-18dB) garantizando techo de True Peak (-1.0 dBTP) y entrega canónica 44.1kHz Stereo.
 */
export class VlogAudioMixer {
  /**
   * Genera el plan maestro de mezcla de audio para un idioma.
   */
  public static createMixPlan(
    projectId: string,
    locale: string,
    trackDescriptors: AudioTrackDescriptor[],
    dialogueIntervals: DialogueInterval[] = [],
    duckingOptions: DuckingOptions = {},
    customConfig?: Partial<AudioMixConfig>
  ): AudioMixPlan {
    const config: AudioMixConfig = {
      masterSampleRateHz: customConfig?.masterSampleRateHz ?? AUDIO_SPECS.MASTER_DEFAULT.sampleRate, // 44100
      channels: customConfig?.channels ?? AUDIO_SPECS.MASTER_DEFAULT.channels, // 2 (Stereo)
      voiceLevelDb: customConfig?.voiceLevelDb ?? 0.0,
      musicLevelDb: customConfig?.musicLevelDb ?? -14.0,
      sfxLevelDb: customConfig?.sfxLevelDb ?? -3.0,
      ambienceLevelDb: customConfig?.ambienceLevelDb ?? -18.0,
      duckingDb: customConfig?.duckingDb ?? -10.0,
      truePeakCeilingDbTP: customConfig?.truePeakCeilingDbTP ?? -1.0,
      enableLimiter: customConfig?.enableLimiter ?? true,
    };

    AudioMixConfigSchema.parse(config);

    // 1. Identificar pistas de voz y música
    const voiceTrack = trackDescriptors.find((t) => t.type === "VOICE");
    const musicTrack = trackDescriptors.find((t) => t.type === "MUSIC");

    // 2. Si existen voz y música, calcular envolvente de ducking
    const duckingEnvelope =
      musicTrack && (voiceTrack || dialogueIntervals.length > 0)
        ? AudioDuckingEngine.generateDuckingEnvelope(
            musicTrack.id,
            voiceTrack ? voiceTrack.id : "voice_dialogue_master",
            dialogueIntervals,
            duckingOptions
          )
        : undefined;

    // 3. Mapear descriptores a pistas procesadas con ganancias asignadas por bus
    const tracks: VlogAudioTrack[] = trackDescriptors.map((desc) => {
      let defaultGain = 0.0;
      switch (desc.type) {
        case "VOICE":
          defaultGain = config.voiceLevelDb;
          break;
        case "MUSIC":
          defaultGain = config.musicLevelDb;
          break;
        case "CRITICAL_SFX":
          defaultGain = config.sfxLevelDb;
          break;
        case "AMBIENCE":
          defaultGain = config.ambienceLevelDb;
          break;
      }

      return {
        id: desc.id,
        name: desc.name,
        type: desc.type,
        audioFilePath: desc.audioFilePath,
        timelineStartSeconds: desc.timelineStartSeconds,
        timelineEndSeconds: desc.timelineEndSeconds,
        volumeDb: desc.customVolumeDb ?? defaultGain,
        isMuted: false,
        isSolo: false,
        duckingEnvelope: desc.type === "MUSIC" ? duckingEnvelope : undefined,
      };
    });

    // 4. Hash SHA-256 determinista del plan
    const payload = JSON.stringify({
      projectId,
      locale,
      config,
      tracks: tracks.map((t) => ({
        id: t.id,
        type: t.type,
        vol: t.volumeDb,
        duckKeyframes: t.duckingEnvelope?.keyframes.length ?? 0,
      })),
    });

    const checksumSha256 = crypto.createHash("sha256").update(payload).digest("hex");

    return {
      projectId,
      locale,
      tracks,
      config,
      checksumSha256,
    };
  }
}
