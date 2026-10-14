import { create } from 'zustand';
import type {
  AudioAnalysis,
  CameraPreset,
  LightingPreset,
  PixelStreamingStatus,
  ProductionPlan,
  TelemetryEvent,
} from '../types';

export interface UIState {
  audioPath: string | null;
  imagePath: string | null;
  videoPath: string | null;
  activePlan: ProductionPlan | null;
  audioAnalysis: AudioAnalysis | null;
  telemetryEvents: TelemetryEvent[];
  viewportMode: 'webgl' | 'pixel_streaming';
  isProcessing: boolean;

  // Playback & Timeline
  currentTime: number;
  isPlaying: boolean;
  duration: number;

  // Visual Scene Controls
  lightingPreset: LightingPreset;
  cameraPreset: CameraPreset;

  // WebRTC Pixel Streaming
  signalingUrl: string;
  pixelStreamingStatus: PixelStreamingStatus;

  // Action Setters
  setAudioPath: (path: string | null) => void;
  setImagePath: (path: string | null) => void;
  setVideoPath: (path: string | null) => void;
  setActivePlan: (plan: ProductionPlan | null) => void;
  setAudioAnalysis: (analysis: AudioAnalysis | null) => void;
  addTelemetryEvent: (event: TelemetryEvent) => void;
  setViewportMode: (mode: 'webgl' | 'pixel_streaming') => void;
  setIsProcessing: (processing: boolean) => void;
  setCurrentTime: (time: number) => void;
  setIsPlaying: (playing: boolean) => void;
  setDuration: (duration: number) => void;
  setLightingPreset: (preset: LightingPreset) => void;
  setCameraPreset: (preset: CameraPreset) => void;
  setSignalingUrl: (url: string) => void;
  setPixelStreamingStatus: (status: PixelStreamingStatus) => void;

  // Copilot Approval Gates
  approveStep: (stepId: string) => void;
  rejectStep: (stepId: string) => void;
}

export const useUIStore = create<UIState>((set) => ({
  audioPath: null,
  imagePath: null,
  videoPath: null,
  activePlan: null,
  audioAnalysis: null,
  telemetryEvents: [],
  viewportMode: 'webgl',
  isProcessing: false,

  currentTime: 0.0,
  isPlaying: false,
  duration: 10.0,

  lightingPreset: 'cyberpunk_neon',
  cameraPreset: 'dramatic_orbit',

  signalingUrl: 'ws://127.0.0.1:8888',
  pixelStreamingStatus: 'disconnected',

  setAudioPath: (path) => set({ audioPath: path }),
  setImagePath: (path) => set({ imagePath: path }),
  setVideoPath: (path) => set({ videoPath: path }),
  setActivePlan: (plan) => set({ activePlan: plan }),
  setAudioAnalysis: (analysis) =>
    set({
      audioAnalysis: analysis,
      duration: analysis?.duration_seconds || 10.0,
    }),
  addTelemetryEvent: (event) =>
    set((state) => ({ telemetryEvents: [...state.telemetryEvents, event] })),
  setViewportMode: (mode) => set({ viewportMode: mode }),
  setIsProcessing: (processing) => set({ isProcessing: processing }),

  setCurrentTime: (time) => set({ currentTime: Math.max(0, time) }),
  setIsPlaying: (playing) => set({ isPlaying: playing }),
  setDuration: (duration) => set({ duration: Math.max(0.1, duration) }),

  setLightingPreset: (preset) => set({ lightingPreset: preset }),
  setCameraPreset: (preset) => set({ cameraPreset: preset }),

  setSignalingUrl: (url) => set({ signalingUrl: url }),
  setPixelStreamingStatus: (status) => set({ pixelStreamingStatus: status }),

  approveStep: (stepId) =>
    set((state) => {
      if (!state.activePlan) return state;
      const updatedSteps = state.activePlan.steps.map((s) =>
        s.step_id === stepId ? { ...s, status: 'approved' as const } : s
      );
      return {
        activePlan: {
          ...state.activePlan,
          steps: updatedSteps,
        },
      };
    }),

  rejectStep: (stepId) =>
    set((state) => {
      if (!state.activePlan) return state;
      const updatedSteps = state.activePlan.steps.map((s) =>
        s.step_id === stepId ? { ...s, status: 'rejected' as const } : s
      );
      return {
        activePlan: {
          ...state.activePlan,
          status: 'rejected' as const,
          steps: updatedSteps,
        },
      };
    }),
}));
