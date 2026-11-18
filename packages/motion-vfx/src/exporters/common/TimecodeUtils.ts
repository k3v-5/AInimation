export interface RationalFrameRate {
  numerator: number;
  denominator: number;
  dropFrame: boolean;
}

export const StandardFrameRates: Record<string, RationalFrameRate> = {
  "24": { numerator: 24, denominator: 1, dropFrame: false },
  "25": { numerator: 25, denominator: 1, dropFrame: false },
  "29.97ndf": { numerator: 30000, denominator: 1001, dropFrame: false },
  "29.97df": { numerator: 30000, denominator: 1001, dropFrame: true },
  "30": { numerator: 30, denominator: 1, dropFrame: false },
  "50": { numerator: 50, denominator: 1, dropFrame: false },
  "59.94ndf": { numerator: 60000, denominator: 1001, dropFrame: false },
  "59.94df": { numerator: 60000, denominator: 1001, dropFrame: true },
  "60": { numerator: 60, denominator: 1, dropFrame: false },
};

/**
 * Utilidades matemáticas deterministas de conversión de Timecode (Fase 17).
 */
export class TimecodeUtils {
  /**
   * Resuelve una tasa de cuadros racional a partir de un número o identificador estándar.
   */
  public static resolveFrameRate(fps: number | string, dropFrame = false): RationalFrameRate {
    if (typeof fps === "string") {
      const match = StandardFrameRates[fps.toLowerCase()];
      if (match) return match;
      const parsed = parseFloat(fps);
      if (!isNaN(parsed) && isFinite(parsed) && parsed > 0) {
        return this.resolveFrameRate(parsed, dropFrame);
      }
    }

    if (typeof fps === "number") {
      if (Math.abs(fps - 29.97) < 0.01) {
        return { numerator: 30000, denominator: 1001, dropFrame };
      }
      if (Math.abs(fps - 23.976) < 0.01 || Math.abs(fps - 23.98) < 0.01) {
        return { numerator: 24000, denominator: 1001, dropFrame: false };
      }
      if (Math.abs(fps - 59.94) < 0.01) {
        return { numerator: 60000, denominator: 1001, dropFrame };
      }
      return { numerator: Math.round(fps), denominator: 1, dropFrame };
    }

    return StandardFrameRates["30"];
  }

  /**
   * Convierte segundos continuos a número absoluto de fotograma.
   */
  public static secondsToFrame(seconds: number, rate: RationalFrameRate): number {
    if (!isFinite(seconds) || seconds < 0) return 0;
    const realFps = rate.numerator / rate.denominator;
    return Math.round(seconds * realFps);
  }

  /**
   * Convierte número absoluto de fotograma a segundos continuos.
   */
  public static frameToSeconds(frame: number, rate: RationalFrameRate): number {
    if (!isFinite(frame) || frame < 0) return 0;
    const realFps = rate.numerator / rate.denominator;
    return Number((frame / realFps).toFixed(6));
  }

  /**
   * Convierte fotograma absoluto a representación Timecode estándar HH:MM:SS:FF (o HH:MM:SS;FF para DF).
   */
  public static frameToTimecode(frame: number, rate: RationalFrameRate): string {
    if (!isFinite(frame) || frame < 0) {
      return rate.dropFrame ? "00:00:00;00" : "00:00:00:00";
    }

    const nominalFps = Math.round(rate.numerator / rate.denominator);
    const separator = rate.dropFrame ? ";" : ":";

    if (!rate.dropFrame) {
      const totalSeconds = Math.floor(frame / nominalFps);
      const ff = frame % nominalFps;
      const ss = totalSeconds % 60;
      const mm = Math.floor(totalSeconds / 60) % 60;
      const hh = Math.floor(totalSeconds / 3600);

      return `${this.pad2(hh)}:${this.pad2(mm)}:${this.pad2(ss)}${separator}${this.pad2(ff)}`;
    }

    // Algoritmo canónico SMPTE 12M para 29.97 Drop-Frame
    const framesPer10Minutes = 17982; // 1800 + 9 * 1798

    const D = Math.floor(frame / framesPer10Minutes);
    const m = frame % framesPer10Minutes;

    let totalMinutes = D * 10;
    let ss = 0;
    let ff = 0;

    if (m >= 1800) {
      const minutesPast0 = Math.floor((m - 1800) / 1798) + 1;
      totalMinutes += minutesPast0;
      const framesInMinute = (m - 1800) % 1798;
      const frameInMinWithDrops = framesInMinute + 2;
      ss = Math.floor(frameInMinWithDrops / 30);
      ff = frameInMinWithDrops % 30;
    } else {
      ss = Math.floor(m / 30);
      ff = m % 30;
    }

    const hh = Math.floor(totalMinutes / 60);
    const mm = totalMinutes % 60;

    return `${this.pad2(hh)}:${this.pad2(mm)}:${this.pad2(ss)}${separator}${this.pad2(ff)}`;
  }

  /**
   * Convierte Timecode (HH:MM:SS:FF o HH:MM:SS;FF) a número absoluto de fotograma.
   */
  public static timecodeToFrame(timecode: string, rate: RationalFrameRate): number {
    const match = timecode.trim().match(/^(\d{1,2}):(\d{2}):(\d{2})[:;](\d{2})$/);
    if (!match) return 0;

    const hh = parseInt(match[1], 10);
    const mm = parseInt(match[2], 10);
    const ss = parseInt(match[3], 10);
    const ff = parseInt(match[4], 10);
    const nominalFps = Math.round(rate.numerator / rate.denominator);

    if (!rate.dropFrame) {
      return (hh * 3600 + mm * 60 + ss) * nominalFps + ff;
    }

    // Inverso canónico SMPTE Drop-Frame
    const totalMinutes = hh * 60 + mm;
    const nominalTotalFrames = (totalMinutes * 60 + ss) * nominalFps + ff;
    const dropFrameCount = 2 * (totalMinutes - Math.floor(totalMinutes / 10));
    return nominalTotalFrames - dropFrameCount;
  }

  /**
   * Convierte segundos a Timecode directamente.
   */
  public static secondsToTimecode(seconds: number, rate: RationalFrameRate): string {
    const frame = this.secondsToFrame(seconds, rate);
    return this.frameToTimecode(frame, rate);
  }

  /**
   * Convierte Timecode a segundos directamente.
   */
  public static timecodeToSeconds(timecode: string, rate: RationalFrameRate): number {
    const frame = this.timecodeToFrame(timecode, rate);
    return this.frameToSeconds(frame, rate);
  }

  private static pad2(n: number): string {
    return String(n).padStart(2, "0");
  }
}
