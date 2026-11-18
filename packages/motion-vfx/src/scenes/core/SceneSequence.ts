import { Time } from "../../core/types.js";
import { TimeRange } from "../../timeline/core/TimeRange.js";
import { TransitionRegistry } from "../../transitions/core/TransitionRegistry.js";
import { TransitionResult, TransitionSerialization } from "../../transitions/types/index.js";
import { Scene } from "./Scene.js";

export interface SceneEntry {
  scene: Scene;
  transitionToNext?: TransitionSerialization;
}

export interface EvaluatedSequenceState {
  globalTime: Time;
  activeScenes: {
    scene: Scene;
    localTime: Time;
    index: number;
  }[];
  transition?: {
    type: string;
    progress: number;
    rawProgress: number;
    result: TransitionResult;
    fromSceneIndex: number;
    toSceneIndex: number;
  };
}

/**
 * Orquestador secuencial de escenas con regiones de solapamiento y transiciones compositivas (Fase 5C).
 */
export class SceneSequence {
  private entries: SceneEntry[] = [];

  public addScene(scene: Scene, transitionToNext?: TransitionSerialization): this {
    this.entries.push({
      scene,
      transitionToNext,
    });
    return this;
  }

  public get size(): number {
    return this.entries.length;
  }

  public getScenes(): Scene[] {
    return this.entries.map((e) => e.scene);
  }

  /**
   * Calcula los intervalos temporales globales [start, end) de cada escena considerando las duraciones de transición.
   */
  public calculateTimelineRanges(): TimeRange[] {
    const ranges: TimeRange[] = [];
    let currentStart = 0;

    for (let i = 0; i < this.entries.length; i++) {
      const entry = this.entries[i];
      const duration = entry.scene.duration;
      const end = currentStart + duration;
      ranges.push(new TimeRange(currentStart, end));

      // Si hay transición hacia la siguiente escena, la siguiente inicia antes para crear solapamiento
      const transDuration = entry.transitionToNext?.duration ?? 0;
      currentStart = end - transDuration;
    }

    return ranges;
  }

  /**
   * Retorna la duración total acumulada de la secuencia de escenas.
   */
  public getTotalDuration(): Time {
    const ranges = this.calculateTimelineRanges();
    if (ranges.length === 0) return 0;
    return ranges[ranges.length - 1].end;
  }

  /**
   * Evalúa la secuencia de escenas en el tiempo global indicado, calculando si existe una transición activa.
   */
  public evaluate(globalTime: Time): EvaluatedSequenceState {
    const ranges = this.calculateTimelineRanges();
    const activeScenes: { scene: Scene; localTime: Time; index: number }[] = [];

    for (let i = 0; i < this.entries.length; i++) {
      const range = ranges[i];
      if (range.contains(globalTime)) {
        const localTime = globalTime - range.start;
        activeScenes.push({
          scene: this.entries[i].scene,
          localTime,
          index: i,
        });
      }
    }

    // Comprobar si nos encontramos en la región de transición entre dos escenas activas
    let activeTransition: EvaluatedSequenceState["transition"];

    if (activeScenes.length === 2 && activeScenes[0].index + 1 === activeScenes[1].index) {
      const fromIdx = activeScenes[0].index;
      const toIdx = activeScenes[1].index;
      const trans = this.entries[fromIdx].transitionToNext;

      if (trans && trans.duration > 0) {
        const transStart = ranges[toIdx].start;
        const elapsed = globalTime - transStart;
        const rawProgress = Math.max(0, Math.min(1, elapsed / trans.duration));

        const result = TransitionRegistry.evaluate(
          trans.type,
          rawProgress,
          elapsed,
          trans.duration,
          trans.params,
          trans.easing
        );

        activeTransition = {
          type: trans.type,
          progress: rawProgress,
          rawProgress,
          result,
          fromSceneIndex: fromIdx,
          toSceneIndex: toIdx,
        };
      }
    }

    return {
      globalTime,
      activeScenes,
      transition: activeTransition,
    };
  }
}
