import { Time } from "../../core/types.js";

export interface SignalSample {
  time: Time;
  value: number;
}

/**
 * Muestreador continuo e interpolador de señales acústicas con seguidor de envolvente (Fase 5I).
 */
export class AudioSignal {
  public readonly name: string;
  private _samples: SignalSample[] = [];

  constructor(name: string, samples: SignalSample[] = []) {
    this.name = name;
    this._samples = [...samples].sort((a, b) => a.time - b.time);
  }

  public get sampleCount(): number {
    return this._samples.length;
  }

  public addSample(time: Time, value: number): this {
    this._samples.push({ time, value });
    this._samples.sort((a, b) => a.time - b.time);
    return this;
  }

  /**
   * Búsqueda binaria O(log N) para encontrar el índice de la muestra izquierda <= time.
   */
  private findSampleIndex(time: Time): number {
    let low = 0;
    let high = this._samples.length - 1;

    while (low <= high) {
      const mid = (low + high) >> 1;
      if (this._samples[mid].time === time) {
        return mid;
      }
      if (this._samples[mid].time < time) {
        low = mid + 1;
      } else {
        high = mid - 1;
      }
    }

    return Math.max(0, high);
  }

  /**
   * Evalúa el valor crudo instantáneo de la señal interpolado linealmente en O(log N).
   */
  public sample(time: Time): number {
    const samples = this._samples;
    if (samples.length === 0) return 0;
    if (time <= samples[0].time) return samples[0].value;
    if (time >= samples[samples.length - 1].time) return samples[samples.length - 1].value;

    const idx = this.findSampleIndex(time);
    const s1 = samples[idx];
    const s2 = samples[Math.min(samples.length - 1, idx + 1)];

    const duration = s2.time - s1.time;
    const t = duration > 0 ? (time - s1.time) / duration : 0;
    return s1.value + (s2.value - s1.value) * Math.max(0, Math.min(1, t));
  }

  /**
   * Evalúa la señal aplicando un filtro de envolvente con Attack / Release.
   */
  public sampleEnvelope(time: Time, attackTime = 0.05, releaseTime = 0.2): number {
    if (this._samples.length === 0) return 0;
    if (time <= 0) return this.sample(0);

    const step = 0.02; // Resolución temporal de 20ms
    let currentEnvelope = this.sample(0);

    for (let t = step; t <= time; t += step) {
      const raw = this.sample(t);
      const isAttack = raw > currentEnvelope;
      const tau = isAttack ? Math.max(0.001, attackTime) : Math.max(0.001, releaseTime);
      const alpha = 1 - Math.exp(-step / tau);
      currentEnvelope += alpha * (raw - currentEnvelope);
    }

    return currentEnvelope;
  }
}
