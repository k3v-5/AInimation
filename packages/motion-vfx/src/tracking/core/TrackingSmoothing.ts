import { SmoothingSettings, TrackingData, TrackingSample } from "../types/index.js";

/**
 * Filtro de reducción de ruido y suavizado temporal de tracking (Fase 5G).
 */
export class TrackingSmoothing {
  public static smooth(data: TrackingData, settings: SmoothingSettings): TrackingData {
    const samples = data.samples;
    if (samples.length <= 1 || settings.mode === "none") {
      return {
        samples: samples.map((s) => ({
          ...s,
          transform: {
            position: { ...s.transform.position },
            scale: { ...s.transform.scale },
            rotation: s.transform.rotation,
          },
        })),
      };
    }

    if (settings.mode === "moving-average") {
      const window = Math.max(1, settings.windowSize ?? 5);
      const half = Math.floor(window / 2);
      const smoothedSamples: TrackingSample[] = [];

      for (let i = 0; i < samples.length; i++) {
        const start = Math.max(0, i - half);
        const end = Math.min(samples.length - 1, i + half);
        const count = end - start + 1;

        let posX = 0,
          posY = 0,
          scaleX = 0,
          scaleY = 0,
          rot = 0,
          conf = 0;

        for (let j = start; j <= end; j++) {
          const s = samples[j];
          posX += s.transform.position.x;
          posY += s.transform.position.y;
          scaleX += s.transform.scale.x;
          scaleY += s.transform.scale.y;
          rot += s.transform.rotation;
          conf += s.confidence ?? 1.0;
        }

        smoothedSamples.push({
          time: samples[i].time,
          transform: {
            position: { x: posX / count, y: posY / count },
            scale: { x: scaleX / count, y: scaleY / count },
            rotation: rot / count,
          },
          confidence: conf / count,
        });
      }

      return { samples: smoothedSamples };
    }

    if (settings.mode === "exponential") {
      const alpha = Math.max(0.01, Math.min(1.0, settings.alpha ?? 0.3));
      const smoothedSamples: TrackingSample[] = [];

      let prev = samples[0];
      smoothedSamples.push({
        time: prev.time,
        transform: {
          position: { ...prev.transform.position },
          scale: { ...prev.transform.scale },
          rotation: prev.transform.rotation,
        },
        confidence: prev.confidence,
      });

      for (let i = 1; i < samples.length; i++) {
        const cur = samples[i];
        const newPosX = alpha * cur.transform.position.x + (1 - alpha) * prev.transform.position.x;
        const newPosY = alpha * cur.transform.position.y + (1 - alpha) * prev.transform.position.y;
        const newScaleX = alpha * cur.transform.scale.x + (1 - alpha) * prev.transform.scale.x;
        const newScaleY = alpha * cur.transform.scale.y + (1 - alpha) * prev.transform.scale.y;
        const newRot = alpha * cur.transform.rotation + (1 - alpha) * prev.transform.rotation;

        const smoothedSample: TrackingSample = {
          time: cur.time,
          transform: {
            position: { x: newPosX, y: newPosY },
            scale: { x: newScaleX, y: newScaleY },
            rotation: newRot,
          },
          confidence: cur.confidence,
        };

        smoothedSamples.push(smoothedSample);
        prev = smoothedSample;
      }

      return { samples: smoothedSamples };
    }

    return { samples: [...samples] };
  }
}
