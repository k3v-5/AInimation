import { MusicalSubdivision } from "./rhythm-types.js";

/**
 * Motor de cálculos de rejilla musical y cuantización temporal a fotogramas de video.
 */
export class MusicalGrid {
  /**
   * Duración en segundos de un pulso de negra (quarter note): 60 / BPM.
   */
  public static getBeatDurationSeconds(bpm: number): number {
    if (bpm <= 0) throw new Error("BPM debe ser estrictamente positivo");
    return 60.0 / bpm;
  }

  /**
   * Duración en segundos de un compás de 4/4 (bar).
   */
  public static getBarDurationSeconds(bpm: number): number {
    return this.getBeatDurationSeconds(bpm) * 4.0;
  }

  /**
   * Calcula la duración en segundos de cualquier subdivisión métrica estándar.
   */
  public static getSubdivisionDurationSeconds(subdivision: MusicalSubdivision, bpm: number): number {
    const beat = this.getBeatDurationSeconds(bpm);
    switch (subdivision) {
      case "WHOLE":
        return beat * 4.0;
      case "HALF":
        return beat * 2.0;
      case "QUARTER":
        return beat;
      case "EIGHTH":
        return beat / 2.0;
      case "SIXTEENTH":
        return beat / 4.0;
      case "THIRTY_SECOND":
        return beat / 8.0;
      case "QUARTER_TRIPLET":
        return (beat * 2.0) / 3.0;
      case "EIGHTH_TRIPLET":
        return beat / 3.0;
      case "SIXTEENTH_TRIPLET":
        return (beat / 2.0) / 3.0;
      default:
        return beat;
    }
  }

  /**
   * Cuantiza un tiempo en segundos al fotograma más cercano de la rejilla de video (FPS).
   * t_snapped = round(t * fps) / fps
   */
  public static snapToFrame(timeSeconds: number, fps: number): number {
    if (fps <= 0) throw new Error("FPS debe ser estrictamente positivo");
    const frameNumber = Math.round(timeSeconds * fps);
    return Number((frameNumber / fps).toFixed(6));
  }

  /**
   * Convierte una duración en segundos a una cantidad entera exacta de fotogramas.
   */
  public static durationToFrames(durationSeconds: number, fps: number): number {
    return Math.max(1, Math.round(durationSeconds * fps));
  }

  /**
   * Genera una secuencia de marcas temporales cuantizadas a fotogramas para un intervalo dado.
   */
  public static generateSubdivisionGrid(
    startTimeSeconds: number,
    durationSeconds: number,
    subdivision: MusicalSubdivision,
    bpm: number,
    fps: number
  ): number[] {
    const step = this.getSubdivisionDurationSeconds(subdivision, bpm);
    const endTime = startTimeSeconds + durationSeconds;
    const timestamps: number[] = [];

    let current = startTimeSeconds;
    while (current < endTime - 1e-5) {
      timestamps.push(this.snapToFrame(current, fps));
      current += step;
    }

    return timestamps;
  }
}
