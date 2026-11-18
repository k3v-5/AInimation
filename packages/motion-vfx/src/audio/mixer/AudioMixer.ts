import { TimeRange } from "../../timeline/core/TimeRange.js";
import { AudioBuffer } from "../core/AudioBuffer.js";
import { AudioMath } from "../core/AudioMath.js";
import { AudioSource } from "../core/AudioSource.js";
import { AudioTrack } from "../core/AudioTrack.js";
import { MasterBus } from "./MasterBus.js";

export interface AudioMixerOptions {
  sampleRate?: number;
  channels?: number;
  masterBus?: MasterBus;
}

/**
 * Motor de mezcla multi-pista determinista con auto-ducking y protección acústica (Fase 5D).
 */
export class AudioMixer {
  public readonly sampleRate: number;
  public readonly channels: number;
  public readonly masterBus: MasterBus;

  constructor(options: AudioMixerOptions = {}) {
    this.sampleRate = options.sampleRate ?? 48000;
    this.channels = options.channels ?? 2;
    this.masterBus = options.masterBus ?? new MasterBus();
  }

  public mix(
    tracks: AudioTrack[],
    timeRange: TimeRange,
    sourceProvider: (assetId: string) => AudioSource | undefined
  ): AudioBuffer {
    const totalFrames = Math.round(timeRange.duration * this.sampleRate);
    const accumulator = AudioBuffer.create(this.channels, totalFrames, this.sampleRate);

    if (tracks.length === 0 || totalFrames === 0) {
      return this.masterBus.process(accumulator);
    }

    const hasSolo = tracks.some((t) => t.solo);

    // 1. Detección de pistas activas para auto-ducking
    const duckedTracks = new Set<string>();
    for (const track of tracks) {
      if (track.ducking) {
        const triggerTrack = tracks.find((t) => t.id === track.ducking?.sourceTrackId);
        if (triggerTrack && !triggerTrack.muted) {
          const triggerClips = triggerTrack.clips.filter((c) => c.timelineRange.overlaps(timeRange) && !c.muted);
          if (triggerClips.length > 0) {
            duckedTracks.add(track.id);
          }
        }
      }
    }

    // 2. Mezcla de cada pista
    for (const track of tracks) {
      if (track.muted) continue;
      if (hasSolo && !track.solo) continue;

      let trackGainMultiplier = AudioMath.dbToGain(track.gainDb);
      if (duckedTracks.has(track.id) && track.ducking) {
        // Aplicar atenuación de ducking
        trackGainMultiplier *= AudioMath.dbToGain(track.ducking.attenuationDb);
      }

      const trackPanCoeffs = AudioMath.calculateStereoPan(track.pan);

      for (const clip of track.clips) {
        if (clip.muted || !clip.timelineRange.overlaps(timeRange)) {
          continue;
        }

        const source = sourceProvider(clip.assetId);
        if (!source) continue;

        // Calcular intervalo de solapamiento
        const overlapStart = Math.max(timeRange.start, clip.timelineRange.start);
        const overlapEnd = Math.min(timeRange.end, clip.timelineRange.end);
        const overlapDuration = overlapEnd - overlapStart;

        if (overlapDuration <= 0) continue;

        // Mapear tiempo al source media
        const clipLocalStart = overlapStart - clip.timelineRange.start;
        const sourceStart = clip.sourceRange.start + clipLocalStart * clip.speed;
        const sourceDuration = overlapDuration * clip.speed;
        const sourceRange = new TimeRange(sourceStart, sourceStart + sourceDuration);

        // Leer buffer de la fuente a la frecuencia del mixer
        const rawBuffer = source.read(sourceRange, this.sampleRate);
        const clipFrames = Math.min(rawBuffer.frames, Math.round(overlapDuration * this.sampleRate));
        const destOffsetFrame = Math.round((overlapStart - timeRange.start) * this.sampleRate);

        const clipPanCoeffs = AudioMath.calculateStereoPan(clip.pan);

        // Sumar muestras con ganancia temporalizada (fades + volume + ducking)
        for (let i = 0; i < clipFrames; i++) {
          const sampleLocalTime = clipLocalStart + i / this.sampleRate;
          const clipGain = clip.getGainAtTime(sampleLocalTime);
          const effectiveGain = clipGain * trackGainMultiplier;

          const leftGain = effectiveGain * clipPanCoeffs.left * trackPanCoeffs.left * 2;
          const rightGain = effectiveGain * clipPanCoeffs.right * trackPanCoeffs.right * 2;

          const srcL = rawBuffer.data[0][i];
          const srcR = rawBuffer.channels >= 2 ? rawBuffer.data[1][i] : srcL;

          const destIndex = destOffsetFrame + i;
          if (destIndex < totalFrames) {
            accumulator.data[0][destIndex] += srcL * leftGain;
            accumulator.data[1][destIndex] += srcR * rightGain;
          }
        }
      }
    }

    return this.masterBus.process(accumulator);
  }
}
