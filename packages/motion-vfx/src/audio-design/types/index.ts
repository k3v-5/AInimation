import { Time } from "../../core/types.js";

export type AudioTrackType = "voice" | "music" | "sfx" | "ambience";

export type AudioPriority = "critical" | "high" | "normal" | "low";

export interface BeatInfo {
  time: Time;
  strength: number; // [0, 1]
  isDownbeat: boolean;
}

export interface SpeechRegion {
  start: Time;
  end: Time;
  speakerId?: string;
  confidence: number;
}

export interface AudioAnalysisResult {
  duration: Time;
  bpm: number;
  beats: BeatInfo[];
  speechRegions: SpeechRegion[];
  silenceRegions: { start: Time; end: Time }[];
  peakAmplitude: number;
}

export interface DuckingRule {
  voiceTrackId: string;
  musicTrackId: string;
  duckedVolume: number; // e.g. 0.2 (-14dB)
  normalVolume: number; // e.g. 1.0 (0dB)
  attackDuration: Time; // e.g. 0.15s
  releaseDuration: Time; // e.g. 0.3s
}

export interface SFXMetadata {
  id: string;
  name: string;
  category: "whoosh" | "impact" | "pop" | "click" | "riser" | "glitch" | "notification";
  energy: "low" | "medium" | "high";
  duration: Time;
  tags: string[];
}

export interface SyncEvent {
  id: string;
  time: Time;
  type: "text_pop" | "impact" | "camera_punch" | "sfx_trigger" | "music_duck";
  strength: number;
  source: "audio" | "motion" | "semantic";
}

export interface SyncGroup {
  id: string;
  time: Time;
  name: string;
  events: SyncEvent[];
}

export interface SoundDesignMacro {
  id: string;
  name: string;
  description: string;
  sfxCategory: SFXMetadata["category"];
  duckAmount: number;
  timingOffset: Time; // Adelanto/retraso respecto al evento visual
}
