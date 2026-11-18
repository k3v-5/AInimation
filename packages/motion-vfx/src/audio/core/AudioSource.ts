import { TimeRange } from "../../timeline/core/TimeRange.js";
import { AudioBuffer } from "./AudioBuffer.js";

export interface AudioSource {
  readonly duration: number;
  readonly sampleRate: number;
  readonly channels: number;
  read(range: TimeRange, targetSampleRate?: number): AudioBuffer;
}

export type SyntheticSoundType = "sine" | "clicks" | "silence" | "noise";

export interface SyntheticAudioOptions {
  type: SyntheticSoundType;
  duration: number;
  sampleRate?: number;
  channels?: number;
  frequency?: number;
  clickInterval?: number; // en segundos (ej. 1.0s para clicks cada segundo)
  amplitude?: number;
}

/**
 * Proveedor de audio sintético para análisis matemático, testing y generación procedural (Fase 5D).
 */
export class SyntheticAudioSource implements AudioSource {
  public readonly duration: number;
  public readonly sampleRate: number;
  public readonly channels: number;
  private buffer: AudioBuffer;

  constructor(options: SyntheticAudioOptions) {
    this.duration = options.duration;
    this.sampleRate = options.sampleRate ?? 48000;
    this.channels = options.channels ?? 2;

    const totalFrames = Math.round(this.duration * this.sampleRate);
    this.buffer = AudioBuffer.create(this.channels, totalFrames, this.sampleRate);

    const amp = options.amplitude ?? 0.8;

    for (let c = 0; c < this.channels; c++) {
      const channelData = this.buffer.data[c];

      if (options.type === "sine") {
        const freq = options.frequency ?? 440;
        for (let i = 0; i < totalFrames; i++) {
          const t = i / this.sampleRate;
          channelData[i] = amp * Math.sin(2 * Math.PI * freq * t);
        }
      } else if (options.type === "clicks") {
        const interval = options.clickInterval ?? 1.0;
        const clickPeriodFrames = Math.round(interval * this.sampleRate);
        const clickDurationFrames = Math.min(240, Math.round(0.005 * this.sampleRate)); // 5ms click

        for (let i = 0; i < totalFrames; i++) {
          const posInPeriod = i % clickPeriodFrames;
          if (posInPeriod < clickDurationFrames) {
            // Pulso de click de alta energía
            channelData[i] = amp * Math.sin((posInPeriod / clickDurationFrames) * Math.PI);
          } else {
            channelData[i] = 0.0;
          }
        }
      } else if (options.type === "noise") {
        for (let i = 0; i < totalFrames; i++) {
          channelData[i] = (Math.random() * 2 - 1) * amp;
        }
      }
      // "silence" deja el buffer inicializado en 0.0
    }
  }

  public read(range: TimeRange, targetSampleRate?: number): AudioBuffer {
    const startFrame = Math.round(range.start * this.sampleRate);
    const endFrame = Math.round(range.end * this.sampleRate);
    const sliced = this.buffer.slice(startFrame, endFrame);

    if (targetSampleRate && targetSampleRate !== this.sampleRate) {
      return sliced.resample(targetSampleRate);
    }
    return sliced;
  }
}
