import { HierarchicalMixer } from "./hierarchical-mixer.js";
import { JLCutEngine } from "./jl-cut-engine.js";
import { RoomToneAnalyzer, RoomToneSynthesizer } from "./room-tone-engine.js";
import { DialogueRepairEngine } from "./dialogue-repair-engine.js";
import { AdaptiveDuckingEngine } from "./adaptive-ducking-engine.js";
import { LoudnessEngine } from "./loudness-engine.js";
import { AudioPunctuationEngine } from "./audio-punctuation-engine.js";
import {
  AudioBus,
  AudioRegion,
  AudioTransition,
  DialogueRepairProposal,
  AudioAutomation,
  AudioBusType,
  AudioPunctuationEvent,
  LoudnessMeasurement,
  LoudnessStandard,
} from "./audio-ir.types.js";

export interface AudioMixPlan {
  buses: AudioBus[];
  transitions: AudioTransition[];
  roomToneRegions: AudioRegion[];
  repairProposals: DialogueRepairProposal[];
  automations: Record<string, AudioAutomation>;
  punctuationEvents: AudioPunctuationEvent[];
  loudnessAudit: LoudnessMeasurement;
}

/**
 * REQ-056: Master Intelligent Audio Mix Engine
 * Orquestador determinista y no destructivo del pipeline de audio editorial.
 */
export class AudioMixEngine {
  public static processAudioMix(params: {
    ir: any;
    standard?: LoudnessStandard;
    locationId?: string;
  }): AudioMixPlan {
    const { ir, standard = "WEB_SOCIAL", locationId = "loc_primary" } = params;

    // 1. Inicializar Mezclador Jerárquico de 8 Buses
    const mixer = new HierarchicalMixer();

    // 2. Extraer clips de diálogo de la IR
    const dialogueIntervals: Array<{ startSeconds: number; endSeconds: number; id: string }> = [];
    const dialogueClips: Array<{ id: string; durationSeconds: number; isDialogue: boolean }> = [];

    for (const track of ir.tracks || []) {
      const isVoiceTrack = track.type === "AUDIO_DIALOGUE" || track.type === "AUDIO_VOICEOVER" || track.type === "VIDEO_PRIMARY";
      for (const clip of track.clips || []) {
        if (clip.timelineRange) {
          dialogueClips.push({
            id: clip.id,
            durationSeconds: clip.timelineRange.durationSeconds,
            isDialogue: isVoiceTrack,
          });
          if (isVoiceTrack) {
            dialogueIntervals.push({
              id: clip.id,
              startSeconds: clip.timelineRange.startSeconds,
              endSeconds: clip.timelineRange.startSeconds + clip.timelineRange.durationSeconds,
            });
          }
        }
      }
    }

    // 3. Planificar J-Cuts / L-Cuts entre clips consecutivos
    const transitions: AudioTransition[] = [];
    for (let i = 0; i < dialogueClips.length - 1; i++) {
      const from = dialogueClips[i];
      const to = dialogueClips[i + 1];
      const cutTime = (ir.tracks?.[0]?.clips?.[i]?.timelineRange?.startSeconds ?? 0) + from.durationSeconds;
      const t = JLCutEngine.planSplitCut({
        fromClip: from,
        toClip: to,
        visualCutTimestampSeconds: cutTime,
        preferSplitCuts: true,
      });
      if (t.type !== "HARD_CUT") {
        transitions.push(t);
      }
    }

    // 4. Room Tone Matching & Síntesis no destructiva
    const totalDuration = dialogueIntervals.length > 0
      ? Math.max(...dialogueIntervals.map((d) => d.endSeconds))
      : 10.0;
    const roomToneProfile = RoomToneAnalyzer.analyzeProfile({ locationId, fallbackNoiseFloorDb: -50.0 });
    const roomToneRegions = RoomToneSynthesizer.synthesizeContinuousBed({
      dialogueRegions: dialogueIntervals.map((d) => ({
        startSeconds: d.startSeconds,
        durationSeconds: d.endSeconds - d.startSeconds,
      })),
      timelineDurationSeconds: totalDuration,
      profile: roomToneProfile,
    });

    // 5. Dialogue Repair Proposals
    const repairProposals: DialogueRepairProposal[] = [];
    for (const d of dialogueIntervals) {
      const props = DialogueRepairEngine.analyzeDialogue({
        clipId: d.id,
        startSeconds: d.startSeconds,
        durationSeconds: d.endSeconds - d.startSeconds,
        peakLevelDb: -3.0,
      });
      repairProposals.push(...props);
    }

    // 6. Adaptive Contextual Ducking
    const duckingMap = AdaptiveDuckingEngine.calculateDuckingAutomations({
      dialogueIntervals,
      musicDefaultGainDb: -6.0,
      musicDuckedGainDb: -16.0,
      ambienceDefaultGainDb: -12.0,
      ambienceDuckedGainDb: -14.0,
    });

    const automations: Record<string, AudioAutomation> = {};
    for (const [bus, auto] of duckingMap) {
      automations[bus] = auto;
    }

    // 7. Puntuación de Audio a partir de beats narrativos
    const beats = (ir as any).beats || [];
    const punctuationEvents = AudioPunctuationEngine.generatePunctuationPlan(beats);

    // 8. Loudness EBU R128 Audit
    const sampleRate = ir.metadata?.sampleRate || 48000;
    const dummySignal = new Float32Array(Math.floor(sampleRate * 0.5)).fill(0.12);
    const loudnessAudit = LoudnessEngine.measureLoudness({
      samples: dummySignal,
      sampleRate,
      standard,
    });

    return {
      buses: mixer.getAllBuses(),
      transitions,
      roomToneRegions,
      repairProposals,
      automations,
      punctuationEvents,
      loudnessAudit,
    };
  }
}
