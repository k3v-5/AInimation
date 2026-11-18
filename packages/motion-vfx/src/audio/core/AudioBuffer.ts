import { ValidationError } from "../../errors/index.js";

/**
 * Contenedor de muestras de audio multi-canal desacoplado de dependencias externas (Fase 5D).
 */
export class AudioBuffer {
  public readonly sampleRate: number;
  public readonly channels: number;
  public readonly frames: number;
  public readonly data: Float32Array[];

  constructor(channels: number, frames: number, sampleRate = 48000, initialData?: Float32Array[]) {
    if (channels <= 0 || frames < 0 || sampleRate <= 0) {
      throw new ValidationError(
        `Invalid AudioBuffer parameters: channels=${channels}, frames=${frames}, sampleRate=${sampleRate}`
      );
    }

    this.channels = channels;
    this.frames = frames;
    this.sampleRate = sampleRate;

    if (initialData) {
      this.data = initialData.map((channelData) => new Float32Array(channelData));
    } else {
      this.data = Array.from({ length: channels }, () => new Float32Array(frames));
    }
  }

  public get duration(): number {
    return this.frames / this.sampleRate;
  }

  public static create(channels: number, frames: number, sampleRate = 48000): AudioBuffer {
    return new AudioBuffer(channels, frames, sampleRate);
  }

  public clone(): AudioBuffer {
    return new AudioBuffer(this.channels, this.frames, this.sampleRate, this.data);
  }

  public slice(startFrame: number, endFrame: number): AudioBuffer {
    const start = Math.max(0, Math.min(this.frames, startFrame));
    const end = Math.max(start, Math.min(this.frames, endFrame));
    const slicedFrames = end - start;

    const slicedData = this.data.map((ch) => ch.slice(start, end));
    return new AudioBuffer(this.channels, slicedFrames, this.sampleRate, slicedData);
  }

  public applyGain(gain: number): void {
    for (let c = 0; c < this.channels; c++) {
      const ch = this.data[c];
      for (let i = 0; i < this.frames; i++) {
        ch[i] *= gain;
      }
    }
  }

  public mixFrom(source: AudioBuffer, gain = 1.0, destOffsetFrame = 0): void {
    const copyFrames = Math.min(source.frames, this.frames - destOffsetFrame);
    if (copyFrames <= 0) return;

    for (let c = 0; c < this.channels; c++) {
      const srcCh = source.data[Math.min(c, source.channels - 1)];
      const destCh = this.data[c];
      for (let i = 0; i < copyFrames; i++) {
        destCh[destOffsetFrame + i] += srcCh[i] * gain;
      }
    }
  }

  /**
   * Realiza un remuestreo lineal al targetSampleRate especificado.
   */
  public resample(targetSampleRate: number): AudioBuffer {
    if (targetSampleRate === this.sampleRate || this.frames === 0) {
      return this.clone();
    }

    const ratio = targetSampleRate / this.sampleRate;
    const targetFrames = Math.round(this.frames * ratio);
    const result = AudioBuffer.create(this.channels, targetFrames, targetSampleRate);

    for (let c = 0; c < this.channels; c++) {
      const src = this.data[c];
      const dest = result.data[c];

      for (let i = 0; i < targetFrames; i++) {
        const srcPos = i / ratio;
        const i0 = Math.floor(srcPos);
        const i1 = Math.min(this.frames - 1, i0 + 1);
        const frac = srcPos - i0;
        dest[i] = src[i0] * (1 - frac) + src[i1] * frac;
      }
    }

    return result;
  }
}
