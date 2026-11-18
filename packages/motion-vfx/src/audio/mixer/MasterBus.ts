import { AudioBuffer } from "../core/AudioBuffer.js";
import { AudioMath } from "../core/AudioMath.js";

export interface MasterBusOptions {
  gainDb?: number;
  pan?: number;
  muted?: boolean;
  limiterThreshold?: number;
}

/**
 * Bus maestro de salida con ganancia general y limitador de protección contra clipping (Fase 5D).
 */
export class MasterBus {
  public gainDb: number;
  public pan: number;
  public muted: boolean;
  public limiterThreshold: number;

  constructor(options: MasterBusOptions = {}) {
    this.gainDb = options.gainDb !== undefined ? options.gainDb : 0.0;
    this.pan = options.pan !== undefined ? Math.max(-1, Math.min(1, options.pan)) : 0.0;
    this.muted = options.muted ?? false;
    this.limiterThreshold = options.limiterThreshold !== undefined ? options.limiterThreshold : 0.95;
  }

  public process(buffer: AudioBuffer): AudioBuffer {
    if (this.muted) {
      return AudioBuffer.create(buffer.channels, buffer.frames, buffer.sampleRate);
    }

    const masterGain = AudioMath.dbToGain(this.gainDb);
    const panCoeffs = AudioMath.calculateStereoPan(this.pan);

    const out = buffer.clone();

    for (let i = 0; i < out.frames; i++) {
      if (out.channels >= 2) {
        out.data[0][i] = AudioMath.softLimit(out.data[0][i] * masterGain * panCoeffs.left * Math.SQRT2, this.limiterThreshold);
        out.data[1][i] = AudioMath.softLimit(out.data[1][i] * masterGain * panCoeffs.right * Math.SQRT2, this.limiterThreshold);
      } else {
        out.data[0][i] = AudioMath.softLimit(out.data[0][i] * masterGain, this.limiterThreshold);
      }
    }

    return out;
  }
}
