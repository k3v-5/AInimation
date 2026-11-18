import { Time } from "../../core/types.js";

export type AudioEventType =
  | "beat"
  | "onset"
  | "speech-start"
  | "speech-end"
  | "word"
  | "pause"
  | "emphasis";

export type SnapMode = "none" | "beat" | "bar" | "subdivision" | "onset" | "word";
export type MappingMode = "linear" | "clamp" | "exponential" | "logarithmic";

export interface AudioSource {
  id: string;
  duration: Time;
  sampleRate: number;
  channels: number;
}

export interface WaveformData {
  samples: number[]; // Normalizados [-1, 1] o [0, 1]
  resolution: number; // Muestras por segundo
}

export interface AmplitudeSample {
  time: Time;
  value: number; // [0, 1]
}

export interface EnergySample {
  time: Time;
  value: number; // RMS [0, 1]
}

export interface FrequencyBand {
  name: string;
  minHz: number;
  maxHz: number;
}

export interface FrequencySample {
  time: Time;
  bands: Record<string, number>; // Ej. { sub: 0.2, bass: 0.8, mid: 0.4, high: 0.1 }
}

export interface Beat {
  time: Time;
  strength: number; // [0, 1]
  confidence?: number; // [0, 1]
}

export interface BeatData {
  bpm?: number;
  beats: Beat[];
}

export interface TempoSegment {
  start: Time;
  end: Time;
  bpm: number;
}

export interface Onset {
  time: Time;
  strength: number;
}

export interface SpeechWord {
  text: string;
  start: Time;
  end: Time;
  confidence?: number;
}

export interface SpeechSegment {
  start: Time;
  end: Time;
  text: string;
  confidence?: number;
  words: SpeechWord[];
}

export interface SpeechData {
  segments: SpeechSegment[];
}

export interface AudioEvent {
  id: string;
  type: AudioEventType;
  time: Time;
  duration?: Time;
  strength?: number;
  confidence?: number;
  metadata?: Record<string, unknown>;
}

export interface SilenceSegment {
  start: Time;
  end: Time;
  duration: Time;
}

export interface BeatGrid {
  bpm: number;
  offset: Time;
  subdivision: number; // 1, 2, 4, 8, 16
}

export interface MusicalBar {
  barIndex: number;
  start: Time;
  end: Time;
  beats: Beat[];
}

export interface AudioMapping {
  mode: MappingMode;
  inputRange: [number, number]; // [minIn, maxIn]
  outputRange: [number, number]; // [minOut, maxOut]
  threshold?: {
    value: number;
    below: number;
    above: number;
  };
}

export interface EnvelopeSettings {
  attackTime: number; // en segundos (ej. 0.05s)
  releaseTime: number; // en segundos (ej. 0.2s)
}

export interface AudioBinding {
  id: string;
  signalName: string; // ej. "bass", "rms", "amplitude"
  targetLayerId: string;
  targetProperty: string; // ej. "scale", "opacity", "camera.zoom"
  mapping: AudioMapping;
  envelope?: EnvelopeSettings;
}

export interface AudioTrigger {
  id: string;
  eventType: AudioEventType;
  targetAction: string; // ej. "restart-animation", "scene-cut", "text-pop"
  cooldown?: Time; // Tiempo mínimo de espera entre disparos
}

export interface AnalysisMetadata {
  analyzerVersion: string;
  settingsHash: string;
  sourceHash: string;
}

export interface AudioAnalysis {
  sourceId: string;
  duration: Time;
  waveform?: WaveformData;
  amplitude?: AmplitudeSample[];
  energy?: EnergySample[];
  frequencies?: FrequencySample[];
  beats?: BeatData;
  onsets?: Onset[];
  speech?: SpeechData;
  metadata?: AnalysisMetadata;
}
