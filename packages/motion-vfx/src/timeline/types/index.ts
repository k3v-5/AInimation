import { Time } from "../../core/types.js";

export type TrackType = "video" | "audio" | "graphics";

export interface TimeBase {
  fps: number;
}

export interface TimeRangeData {
  start: Time;
  end: Time;
}

export interface Marker {
  id: string;
  time: Time;
  label?: string;
  color?: string;
}

export interface ClipSerialization {
  id: string;
  name?: string;
  elementId: string;
  timelineRange: TimeRangeData;
  sourceRange?: TimeRangeData;
  speed?: number;
  trackId?: string;
}

export interface TrackSerialization {
  id: string;
  name: string;
  type: TrackType;
  order: number;
  enabled: boolean;
  muted: boolean;
  locked: boolean;
  solo: boolean;
  opacity: number;
  clips: ClipSerialization[];
}

export interface TimelineSerialization {
  duration: Time;
  timeBase: TimeBase;
  tracks: TrackSerialization[];
  markers: Marker[];
}

export interface EvaluatedClip {
  clipId: string;
  name?: string;
  elementId: string;
  trackId: string;
  trackType: TrackType;
  localTime: Time;
  sourceTime?: Time;
  speed: number;
  opacity: number;
}

export interface TimelineState {
  time: Time;
  frame: number;
  activeClips: EvaluatedClip[];
}
