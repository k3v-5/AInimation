import { Time } from "../../core/types.js";
import { TrackingData, TrackingSample, TransformSample } from "../types/index.js";

/**
 * Contenedor y evaluador continuo de datos de tracking (Fase 5G).
 */
export class Tracker {
  public readonly id: string;
  private _data: TrackingData;

  constructor(id: string, initialData?: TrackingData) {
    this.id = id;
    this._data = {
      samples: initialData ? [...initialData.samples].sort((a, b) => a.time - b.time) : [],
    };
  }

  public get data(): TrackingData {
    return {
      samples: this._data.samples.map((s) => ({
        ...s,
        transform: {
          position: { ...s.transform.position },
          scale: { ...s.transform.scale },
          rotation: s.transform.rotation,
        },
      })),
    };
  }

  public addSample(sample: TrackingSample): this {
    this._data.samples.push({
      ...sample,
      transform: {
        position: { ...sample.transform.position },
        scale: { ...sample.transform.scale },
        rotation: sample.transform.rotation,
      },
    });
    this._data.samples.sort((a, b) => a.time - b.time);
    return this;
  }

  public evaluateAt(time: Time): TransformSample {
    const samples = this._data.samples;
    if (samples.length === 0) {
      return {
        position: { x: 0, y: 0 },
        scale: { x: 1, y: 1 },
        rotation: 0,
      };
    }

    if (time <= samples[0].time) {
      return { ...samples[0].transform };
    }
    if (time >= samples[samples.length - 1].time) {
      return { ...samples[samples.length - 1].transform };
    }

    // Buscar intervalo de muestras [s1, s2]
    let s1 = samples[0];
    let s2 = samples[1];
    for (let i = 0; i < samples.length - 1; i++) {
      if (time >= samples[i].time && time <= samples[i + 1].time) {
        s1 = samples[i];
        s2 = samples[i + 1];
        break;
      }
    }

    const duration = s2.time - s1.time;
    const progress = duration > 0 ? (time - s1.time) / duration : 0;
    const t = Math.max(0, Math.min(1, progress));

    return {
      position: {
        x: s1.transform.position.x + (s2.transform.position.x - s1.transform.position.x) * t,
        y: s1.transform.position.y + (s2.transform.position.y - s1.transform.position.y) * t,
      },
      scale: {
        x: s1.transform.scale.x + (s2.transform.scale.x - s1.transform.scale.x) * t,
        y: s1.transform.scale.y + (s2.transform.scale.y - s1.transform.scale.y) * t,
      },
      rotation: s1.transform.rotation + (s2.transform.rotation - s1.transform.rotation) * t,
    };
  }
}
