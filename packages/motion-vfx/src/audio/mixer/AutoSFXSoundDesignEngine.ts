export type SFXType = "whoosh" | "impact_boom" | "ui_tick" | "camera_shutter" | "sub_drop";

export interface SFXEvent {
  id: string;
  time: number; // Tiempo en segundos
  type: SFXType;
  volumeDb: number; // default: 0dB
  duration: number; // Duración estimada en segundos
}

export interface DuckingKeyframe {
  time: number;
  gainDb: number;
}

export interface VisualTrigger {
  type: "transition" | "text_pop" | "hud_element" | "bass_drop";
  time: number;
  intensity?: number; // [0, 1]
}

/**
 * Motor de diseño de sonido automático y sincronización de efectos foley (Fase 5D / Mejoras).
 * Mapea eventos visuales a efectos de sonido (Whooshes, Booms, Ticks) y genera envolventes
 * automáticas de atenuación musical (Auto-Ducking) para mezclas cinematográficas profesionales.
 */
export class AutoSFXSoundDesignEngine {
  /**
   * Mapea una lista de disparadores visuales a eventos de sonido correspondientes.
   */
  public static mapVisualsToSFX(triggers: VisualTrigger[]): SFXEvent[] {
    const sfxEvents: SFXEvent[] = [];

    for (let i = 0; i < triggers.length; i++) {
      const tr = triggers[i];
      const id = `sfx_${tr.type}_${i + 1}`;

      if (tr.type === "transition") {
        sfxEvents.push({
          id,
          time: Number(Math.max(0, tr.time - 0.12).toFixed(3)), // Iniciar ligeramente antes del corte
          type: "whoosh",
          volumeDb: -3.0,
          duration: 0.35,
        });
      } else if (tr.type === "text_pop" || tr.type === "bass_drop") {
        sfxEvents.push({
          id,
          time: Number(tr.time.toFixed(3)),
          type: "impact_boom",
          volumeDb: -1.5,
          duration: 0.8,
        });
      } else if (tr.type === "hud_element") {
        sfxEvents.push({
          id,
          time: Number(tr.time.toFixed(3)),
          type: "ui_tick",
          volumeDb: -8.0,
          duration: 0.15,
        });
      }
    }

    return sfxEvents;
  }

  /**
   * Genera la curva de ganancia de Auto-Ducking para la música de fondo.
   */
  public static generateDuckingEnvelope(
    sfxEvents: SFXEvent[],
    compDuration: number,
    duckAmountDb = -4.0,
    recoveryTimeSec = 0.25
  ): DuckingKeyframe[] {
    const keyframes: DuckingKeyframe[] = [{ time: 0, gainDb: 0 }];

    // Filtrar solo impactos significativos
    const majorImpacts = sfxEvents.filter(
      (e) => e.type === "impact_boom" || e.type === "sub_drop" || e.type === "whoosh"
    );

    for (const impact of majorImpacts) {
      const t = impact.time;
      const duckStart = Math.max(0, t - 0.05);
      const duckEnd = Math.min(compDuration, t + impact.duration + recoveryTimeSec);

      // Bajar volumen antes del golpe
      keyframes.push({ time: Number(duckStart.toFixed(3)), gainDb: 0 });
      // Volumen mínimo en el impacto
      keyframes.push({ time: Number(t.toFixed(3)), gainDb: duckAmountDb });
      // Restaurar volumen tras el impacto
      keyframes.push({ time: Number(duckEnd.toFixed(3)), gainDb: 0 });
    }

    keyframes.push({ time: compDuration, gainDb: 0 });
    return keyframes.sort((a, b) => a.time - b.time);
  }
}
