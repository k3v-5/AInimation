import { Time } from "../../core/types.js";
import { Beat, BeatGrid, MusicalBar, SnapMode } from "../types/index.js";

/**
 * Cuantizador y alineador temporal rítmico a cuadrículas de compás y beats (Fase 5I).
 */
export class Quantizer {
  /**
   * Ajusta un timestamp al punto más cercano según el BeatGrid y modo de cuantización.
   */
  public static snap(time: Time, grid: BeatGrid, mode: SnapMode = "beat"): Time {
    if (mode === "none" || grid.bpm <= 0) {
      return time;
    }

    const secondsPerBeat = 60.0 / grid.bpm;
    let step = secondsPerBeat;

    if (mode === "subdivision") {
      const sub = Math.max(1, grid.subdivision);
      step = secondsPerBeat / sub;
    } else if (mode === "bar") {
      step = secondsPerBeat * 4; // Asumiendo 4/4
    }

    const relativeTime = time - grid.offset;
    const roundedSteps = Math.round(relativeTime / step);
    return Math.max(0, grid.offset + roundedSteps * step);
  }

  /**
   * Agrupa beats detectados en compases musicales de 4 tiempos.
   */
  public static createMusicalBars(beats: Beat[], beatsPerBar = 4): MusicalBar[] {
    const bars: MusicalBar[] = [];
    if (beats.length === 0) return bars;

    const sorted = [...beats].sort((a, b) => a.time - b.time);
    let barIndex = 0;

    for (let i = 0; i < sorted.length; i += beatsPerBar) {
      const barBeats = sorted.slice(i, i + beatsPerBar);
      const start = barBeats[0].time;
      const end =
        i + beatsPerBar < sorted.length
          ? sorted[i + beatsPerBar].time
          : barBeats[barBeats.length - 1].time + (60.0 / 120.0); // fallback duración de un beat

      bars.push({
        barIndex,
        start,
        end,
        beats: barBeats,
      });
      barIndex++;
    }

    return bars;
  }
}
