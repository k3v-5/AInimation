import crypto from "crypto";
import {
  AudioTransient,
  AudioTransientSchema,
  BeatGridSpec,
  BeatGridSpecSchema,
  BeatMarker,
  BeatMarkerSchema,
  BeatSyncCutDecision,
  BeatSyncCutDecisionSchema,
  BeatSyncMode,
  BeatSyncPlan,
  BeatSyncPlanSchema,
  ScalePulseKeyframe,
} from "./beat-sync-types.js";

export interface CandidateClip {
  id: string;
  assetId: string;
  availableDurationSeconds: number;
  label?: string;
}

export interface AlignCutsOptions {
  clips: CandidateClip[];
  beatGrid: AudioTransient[];
  mode?: BeatSyncMode;
  minCutDurationSeconds?: number;
  maxTotalDurationSeconds?: number;
  pulseStrengthPercent?: number; // ej. 105% (5% pulse)
}

/**
 * Motor de Sincronización Rítmica por Transientes de Audio y Cuadrícula Musical (v4.1.0).
 */
export class BeatSyncEngine {
  /**
   * Genera una cuadrícula de beats y compases musicales determinista a partir de un BPM.
   */
  public static generateBeatGrid(specInput: BeatGridSpec): {
    beats: AudioTransient[];
    markers: BeatMarker[];
  } {
    const spec = BeatGridSpecSchema.parse(specInput);
    const beatsPerMeasure = spec.timeSignature === "3/4" ? 3 : spec.timeSignature === "6/8" ? 6 : 4;
    const secondsPerBeat = 60.0 / spec.bpm;
    const subInterval = secondsPerBeat / spec.subdivision;

    const beats: AudioTransient[] = [];
    const markers: BeatMarker[] = [];

    let currentSeconds = spec.offsetSeconds;
    let stepIndex = 0;

    while (currentSeconds <= spec.totalDurationSeconds) {
      const isSubdivision = spec.subdivision > 1 && stepIndex % spec.subdivision !== 0;
      const beatIndex = Math.floor(stepIndex / spec.subdivision);
      const beatInMeasure = (beatIndex % beatsPerMeasure) + 1;
      const measureNumber = Math.floor(beatIndex / beatsPerMeasure) + 1;
      const isDownbeat = !isSubdivision && beatInMeasure === 1;

      const strength = isDownbeat ? 1.0 : !isSubdivision && beatInMeasure === 3 ? 0.8 : 0.5;

      const transientId = `transient_${stepIndex.toString().padStart(4, "0")}`;
      const transient = AudioTransientSchema.parse({
        id: transientId,
        timestampSeconds: Number(currentSeconds.toFixed(6)),
        strength,
        isDownbeat,
        frequencyBand: isDownbeat ? "LOW" : "MID",
        confidence: 1.0,
      });

      beats.push(transient);

      if (!isSubdivision) {
        markers.push(
          BeatMarkerSchema.parse({
            timeSeconds: Number(currentSeconds.toFixed(6)),
            name: isDownbeat ? `BAR ${measureNumber} (DOWNBEAT)` : `Beat ${measureNumber}.${beatInMeasure}`,
            isDownbeat,
            measureNumber,
            beatInMeasure,
          })
        );
      }

      currentSeconds += subInterval;
      stepIndex++;
    }

    return { beats, markers };
  }

  /**
   * Detecta transientes a partir de una serie temporal de muestras de energía RMS.
   * Utiliza umbralización adaptativa local y periodo refractario para evitar rebotes.
   */
  public static detectTransientsFromEnergy(
    samples: { time: number; energy: number }[],
    options: {
      sensitivityK?: number;
      refractorySeconds?: number;
      windowSize?: number;
      minAbsoluteEnergy?: number;
    } = {}
  ): AudioTransient[] {
    if (!samples || samples.length === 0) return [];

    const k = options.sensitivityK ?? 1.2;
    const refractory = options.refractorySeconds ?? 0.12;
    const windowSize = options.windowSize ?? 10;
    const minEnergy = options.minAbsoluteEnergy ?? 0.2;

    const sorted = [...samples].sort((a, b) => a.time - b.time);
    const transients: AudioTransient[] = [];
    let lastTransientTime = -refractory;

    for (let i = 1; i < sorted.length - 1; i++) {
      const current = sorted[i];

      // Ventana móvil de contexto centrada
      const startIdx = Math.max(0, i - windowSize);
      const endIdx = Math.min(sorted.length - 1, i + windowSize);
      const window = sorted.slice(startIdx, endIdx + 1);

      const mean = window.reduce((sum, s) => sum + s.energy, 0) / window.length;
      const variance = window.reduce((sum, s) => sum + Math.pow(s.energy - mean, 2), 0) / window.length;
      const stdDev = Math.sqrt(variance);

      const threshold = mean + k * stdDev;

      // Pico local: mayor que umbral absoluto, mayor que umbral dinámico y mayor o igual que sus vecinos contiguos
      const isPeak =
        current.energy >= minEnergy &&
        current.energy > threshold &&
        current.energy >= sorted[i - 1].energy &&
        current.energy >= sorted[i + 1].energy;

      if (isPeak && current.time - lastTransientTime >= refractory) {
        const strength = Math.min(1.0, (current.energy - mean) / (stdDev > 1e-6 ? stdDev * 3 : 1));
        const isDownbeat = strength >= 0.8;

        transients.push(
          AudioTransientSchema.parse({
            id: `tr_${transients.length + 1}`,
            timestampSeconds: Number(current.time.toFixed(6)),
            strength: Number(Math.max(0.1, strength).toFixed(4)),
            isDownbeat,
            frequencyBand: isDownbeat ? "LOW" : "FULL_SPECTRUM",
            confidence: 0.95,
          })
        );
        lastTransientTime = current.time;
      }
    }

    return transients;
  }

  /**
   * Alinea el montaje de una lista de clips de vídeo a los beats de la música.
   * Garantiza continuidad temporal sin huecos (zero gap) y duraciones mínimas.
   */
  public static alignCutsToBeat(options: AlignCutsOptions): BeatSyncPlan {
    const {
      clips,
      beatGrid,
      mode = "EVERY_BEAT",
      minCutDurationSeconds = 0.5,
      maxTotalDurationSeconds,
      pulseStrengthPercent = 106.0,
    } = options;

    if (clips.length === 0) {
      throw new Error("BeatSyncEngine: Se requiere al menos un clip candidato.");
    }
    if (beatGrid.length === 0) {
      throw new Error("BeatSyncEngine: La cuadrícula de beats no contiene transientes.");
    }

    // 1. Filtrar puntos de corte objetivo según el modo
    let targetBeats: AudioTransient[] = [];
    switch (mode) {
      case "DOWNBEAT_ONLY":
        targetBeats = beatGrid.filter((b) => b.isDownbeat);
        break;
      case "HALF_BAR":
        targetBeats = beatGrid.filter((b) => b.isDownbeat || b.strength >= 0.8);
        break;
      case "DYNAMIC_ENERGY":
        targetBeats = beatGrid.filter((b) => b.strength >= 0.6);
        break;
      case "EVERY_BEAT":
      case "SUBDIVISION_8TH":
      default:
        targetBeats = [...beatGrid];
        break;
    }

    if (targetBeats.length === 0) {
      targetBeats = [...beatGrid];
    }

    // 2. Asignación elástica de cortes
    const cuts: BeatSyncCutDecision[] = [];
    const pulses: ScalePulseKeyframe[] = [];
    let timelineCursor = 0.0;
    let clipIndex = 0;

    for (let i = 0; i < targetBeats.length; i++) {
      const beat = targetBeats[i];
      if (beat.timestampSeconds <= timelineCursor) continue;

      const proposedDuration = beat.timestampSeconds - timelineCursor;
      if (proposedDuration < minCutDurationSeconds) continue;

      const clip = clips[clipIndex % clips.length];
      const cutDuration = proposedDuration;

      // Respetar metraje disponible
      const sourceStart = 0.0;
      const sourceEnd = Math.min(cutDuration, clip.availableDurationSeconds);

      const decision: BeatSyncCutDecision = BeatSyncCutDecisionSchema.parse({
        id: `cut_${cuts.length + 1}`,
        clipId: clip.id,
        assetId: clip.assetId,
        timelineStart: Number(timelineCursor.toFixed(6)),
        timelineEnd: Number(beat.timestampSeconds.toFixed(6)),
        durationSeconds: Number(cutDuration.toFixed(6)),
        sourceStart: Number(sourceStart.toFixed(6)),
        sourceEnd: Number(sourceEnd.toFixed(6)),
        snappedBeatTime: Number(beat.timestampSeconds.toFixed(6)),
        driftSeconds: 0.0,
        isDownbeat: beat.isDownbeat,
        pulseScale: beat.isDownbeat ? pulseStrengthPercent : 100.0,
      });

      cuts.push(decision);

      // Generar pulsos visuales de escala al downbeat
      if (beat.isDownbeat) {
        pulses.push({ timeSeconds: Number(timelineCursor.toFixed(6)), scalePercent: pulseStrengthPercent });
        pulses.push({ timeSeconds: Number((timelineCursor + 0.12).toFixed(6)), scalePercent: 100.0 });
      }

      timelineCursor = beat.timestampSeconds;
      clipIndex++;

      if (maxTotalDurationSeconds && timelineCursor >= maxTotalDurationSeconds) {
        break;
      }
    }

    const totalDurationSeconds = timelineCursor;

    // 3. Checksum determinista SHA-256
    const contentToHash = JSON.stringify({
      mode,
      totalDurationSeconds,
      cutsCount: cuts.length,
      cuts: cuts.map((c) => ({ id: c.id, tS: c.timelineStart, tE: c.timelineEnd })),
    });
    const checksumSha256 = crypto.createHash("sha256").update(contentToHash).digest("hex");

    const markers: BeatMarker[] = targetBeats
      .filter((b) => b.timestampSeconds <= totalDurationSeconds)
      .map((b, idx) => ({
        timeSeconds: b.timestampSeconds,
        name: b.isDownbeat ? `BAR BEAT (DOWNBEAT)` : `BEAT ${idx + 1}`,
        isDownbeat: b.isDownbeat,
        measureNumber: Math.floor(idx / 4) + 1,
        beatInMeasure: (idx % 4) + 1,
      }));

    return BeatSyncPlanSchema.parse({
      id: `beat_plan_${Date.now()}`,
      bpm: 120, // Default o heredado
      timeSignature: "4/4",
      totalDurationSeconds: Number(totalDurationSeconds.toFixed(6)),
      totalCuts: cuts.length,
      cuts,
      markers,
      scalePulses: pulses,
      checksumSha256,
    });
  }

  /**
   * Genera código ExtendScript JSX para insertar marcadores rítmicos en la composición de AE.
   */
  public static exportToExtendScript(
    plan: BeatSyncPlan,
    options: { compVarName?: string; layerVarName?: string } = {}
  ): string[] {
    const comp = options.compVarName ?? "comp";
    const lines: string[] = [];

    lines.push("// --- RHYTHMIC BEAT SYNC MARKERS & PULSES ---");
    for (const m of plan.markers) {
      const comment = m.isDownbeat ? "DOWNBEAT" : "BEAT";
      lines.push(
        `  if (${comp} && ${comp}.markerProperty) { var mv = new MarkerValue('${comment}'); ${comp}.markerProperty.setValueAtTime(${m.timeSeconds.toFixed(3)}, mv); }`
      );
    }

    return lines;
  }
}
