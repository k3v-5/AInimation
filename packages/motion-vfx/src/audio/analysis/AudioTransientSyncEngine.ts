import { AudioBuffer } from "../core/AudioBuffer.js";
import { AudioMath } from "../core/AudioMath.js";

export interface AudioTransient {
  time: number; // Tiempo en segundos
  energy: number; // Fuerza del transiente normalizada [0, 1]
  band: "sub" | "low" | "mid" | "high" | "full";
  confidence: number;
}

export interface TransientSyncOptions {
  windowSizeMs?: number; // Tamaño de ventana en ms (default: 20ms)
  hopSizeMs?: number; // Salto de ventana en ms (default: 10ms)
  minPeakDistanceMs?: number; // Distancia mínima entre picos consecutivos (default: 80ms)
  sensitivity?: number; // Sensibilidad [0.1, 1.0] (default: 0.5)
  targetBands?: Array<"sub" | "low" | "mid" | "high" | "full">;
}

export interface AlignedClipTiming {
  clipIndex: number;
  originalInTime: number;
  alignedInTime: number;
  alignedOutTime: number;
  duration: number;
  snappedTransient?: AudioTransient;
}

/**
 * Motor de análisis acústico de alta precisión para detección de transientes y sincronización rítmica (Fase 5D / Mejoras).
 * Implementa algoritmos de Spectral Flux, derivada de energía de primer orden y alineación automática de timelines.
 */
export class AudioTransientSyncEngine {
  /**
   * Detecta todos los transientes acústicos (kicks, snares, drops) en un AudioBuffer.
   */
  public static detectTransients(
    buffer: AudioBuffer,
    options: TransientSyncOptions = {}
  ): AudioTransient[] {
    if (buffer.frames === 0) return [];

    const windowSizeMs = options.windowSizeMs ?? 25;
    const hopSizeMs = options.hopSizeMs ?? 10;
    const minPeakDistanceMs = options.minPeakDistanceMs ?? 100;
    const sensitivity = Math.max(0.1, Math.min(1.0, options.sensitivity ?? 0.5));

    const sampleRate = buffer.sampleRate;
    const windowFrames = Math.max(16, Math.round((windowSizeMs / 1000) * sampleRate));
    const hopFrames = Math.max(8, Math.round((hopSizeMs / 1000) * sampleRate));
    const minPeakDistanceFrames = Math.round((minPeakDistanceMs / 1000) * sampleRate);

    // 1. Extraer canal mono promedio
    const mono = new Float32Array(buffer.frames);
    const numChannels = buffer.channels;
    for (let i = 0; i < buffer.frames; i++) {
      let sum = 0;
      for (let c = 0; c < numChannels; c++) {
        sum += buffer.data[c][i];
      }
      mono[i] = sum / numChannels;
    }

    // 2. Calcular envolvente de energía por ventanas (RMS y derivativa de energía)
    const numWindows = Math.floor((buffer.frames - windowFrames) / hopFrames);
    if (numWindows <= 1) return [];

    const energies = new Float32Array(numWindows);
    const subEnergies = new Float32Array(numWindows);

    for (let w = 0; w < numWindows; w++) {
      const start = w * hopFrames;
      let sumSq = 0;
      let subSumSq = 0;

      // Filtro pasa-bajos simple para energía sub-bass (diferencia de muestras adyacentes)
      for (let n = 0; n < windowFrames; n++) {
        const val = mono[start + n];
        sumSq += val * val;

        // Promedio móvil para aislar frecuencias graves (Sub-Bass)
        if (n >= 4) {
          const lowPass = (mono[start + n] + mono[start + n - 1] + mono[start + n - 2] + mono[start + n - 3]) / 4;
          subSumSq += lowPass * lowPass;
        }
      }

      energies[w] = Math.sqrt(sumSq / windowFrames);
      subEnergies[w] = Math.sqrt(subSumSq / windowFrames);
    }

    // 3. Calcular función de detección de onsets (Half-Wave Rectified Spectral Flux)
    const onsetCurve = new Float32Array(numWindows);
    let maxOnset = 0;

    for (let w = 1; w < numWindows; w++) {
      const diff = energies[w] - energies[w - 1];
      const subDiff = subEnergies[w] - subEnergies[w - 1];
      
      // Combinar energía general con energía de graves
      const flux = Math.max(0, diff) * 0.6 + Math.max(0, subDiff) * 0.4;
      onsetCurve[w] = flux;
      if (flux > maxOnset) maxOnset = flux;
    }

    if (maxOnset <= 0) return [];

    // Normalizar curva de onsets
    for (let w = 0; w < numWindows; w++) {
      onsetCurve[w] /= maxOnset;
    }

    // 4. Detección adaptativa de picos locales
    const threshold = (1.0 - sensitivity) * 0.35 + 0.05;
    const transients: AudioTransient[] = [];
    let lastTransientFrame = -minPeakDistanceFrames;

    for (let w = 1; w < numWindows - 1; w++) {
      const val = onsetCurve[w];
      const currentFrame = w * hopFrames;

      if (
        val >= threshold &&
        val > onsetCurve[w - 1] &&
        val >= onsetCurve[w + 1] &&
        currentFrame - lastTransientFrame >= minPeakDistanceFrames
      ) {
        const timeSec = Number((currentFrame / sampleRate).toFixed(4));
        const isSubDominant = subEnergies[w] > energies[w] * 0.6;

        transients.push({
          time: timeSec,
          energy: Number(val.toFixed(4)),
          band: isSubDominant ? "sub" : "full",
          confidence: Number(Math.min(1.0, val * 1.5).toFixed(4)),
        });

        lastTransientFrame = currentFrame;
      }
    }

    return transients;
  }

  /**
   * Alinea los puntos de corte de una secuencia de clips a los transientes de audio más cercanos.
   */
  public static alignTimelineToTransients(
    clipDurations: number[],
    transients: AudioTransient[],
    options: { maxSnapToleranceSec?: number; totalDuration?: number } = {}
  ): AlignedClipTiming[] {
    const tolerance = options.maxSnapToleranceSec ?? 0.35;
    const totalDuration = options.totalDuration ?? clipDurations.reduce((a, b) => a + b, 0);

    const aligned: AlignedClipTiming[] = [];
    let currentInTime = 0;

    for (let i = 0; i < clipDurations.length; i++) {
      const targetDuration = clipDurations[i];
      const expectedOutTime = currentInTime + targetDuration;

      // Buscar transiente más cercano a expectedOutTime dentro de la tolerancia
      let closestTransient: AudioTransient | undefined;
      let minDelta = Infinity;

      for (const t of transients) {
        const delta = Math.abs(t.time - expectedOutTime);
        if (delta <= tolerance && delta < minDelta && t.time > currentInTime + 0.5) {
          minDelta = delta;
          closestTransient = t;
        }
      }

      let actualOutTime = expectedOutTime;
      if (closestTransient && i < clipDurations.length - 1) {
        actualOutTime = closestTransient.time;
      }

      actualOutTime = Math.min(actualOutTime, totalDuration);

      aligned.push({
        clipIndex: i,
        originalInTime: Number(currentInTime.toFixed(3)),
        alignedInTime: Number(currentInTime.toFixed(3)),
        alignedOutTime: Number(actualOutTime.toFixed(3)),
        duration: Number((actualOutTime - currentInTime).toFixed(3)),
        snappedTransient: closestTransient,
      });

      currentInTime = actualOutTime;
      if (currentInTime >= totalDuration) break;
    }

    // Ajustar el último clip para que cubra exactamente el total
    if (aligned.length > 0) {
      aligned[aligned.length - 1].alignedOutTime = totalDuration;
      aligned[aligned.length - 1].duration = Number(
        (totalDuration - aligned[aligned.length - 1].alignedInTime).toFixed(3)
      );
    }

    return aligned;
  }

  /**
   * Extrae marcas de tiempo óptimas para Bass Punches (drops de bajo/kicks principales).
   */
  public static extractBassPunchTimestamps(
    transients: AudioTransient[],
    minConfidence = 0.4
  ): number[] {
    return transients
      .filter((t) => (t.band === "sub" || t.energy >= 0.5) && t.confidence >= minConfidence)
      .map((t) => t.time);
  }
}
