import { EasingName, Time } from "../../core/types.js";
import { TimeRangeData } from "../../timeline/types/index.js";

export interface AudioBufferData {
  sampleRate: number;
  channels: number;
  frames: number;
  data: Float32Array[];
}

export interface FadeConfig {
  duration: Time;
  easing?: EasingName;
}

export interface DuckingConfig {
  sourceTrackId: string; // Pista disparadora (ej. voz)
  attenuationDb: number; // Reducción de ganancia (ej. -8 dB)
  thresholdRms: number; // Umbral de energía RMS para activar ducking
  attackTime?: Time; // Tiempo de rampa de entrada (ej. 0.05s)
  releaseTime?: Time; // Tiempo de recuperación (ej. 0.2s)
}

export interface AudioClipSerialization {
  id: string;
  name?: string;
  assetId: string;
  timelineRange: TimeRangeData;
  sourceRange: TimeRangeData;
  speed: number;
  volume: number;
  gainDb: number;
  pan: number;
  fadeIn?: FadeConfig;
  fadeOut?: FadeConfig;
  muted: boolean;
}

export interface AudioTrackSerialization {
  id: string;
  name: string;
  gainDb: number;
  pan: number;
  muted: boolean;
  solo: boolean;
  ducking?: DuckingConfig;
  clips: AudioClipSerialization[];
}

export interface Beat {
  time: Time;
  strength: number;
  type?: "beat" | "downbeat" | "onset";
}

export interface BeatMap {
  bpm?: number;
  beats: Beat[];
}

export interface SilenceInterval {
  start: Time;
  end: Time;
  duration: Time;
}

export interface WaveformPeak {
  min: number;
  max: number;
  rms: number;
}

export interface AudioEvent {
  type: "beat" | "onset" | "silence_start" | "silence_end" | "energy_peak";
  time: Time;
  value?: number;
  metadata?: Record<string, unknown>;
}
