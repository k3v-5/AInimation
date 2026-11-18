import {
  Dataset,
  ValidationResult,
  NormalizedVisualizationData,
  VisualizationCompileContext,
  DataVisualizationCompiler,
  TimelineEvent,
} from "./contracts.js";
import { TimelineNode } from "./visualization-base.js";
import { ProvenanceTracker } from "./provenance.js";
import { ChronologyTimelineGenerator as InternalGenerator } from "./chronology-timeline-generator.js";

export interface ChronologyTimelineConfig {
  orientation?: "HORIZONTAL" | "VERTICAL";
  animationDurationSeconds?: number;
  unsortedPolicy?: "ALLOW_SORT" | "WARNING" | "BLOCKING";
  showDescriptions?: boolean;
}

/**
 * REQ-025 §17, §18 & §19: ChronologyTimelineGenerator
 * Generador procedural de líneas de tiempo cronológicas.
 */
export class ChronologyTimelineGenerator implements DataVisualizationCompiler<Dataset | { events: TimelineEvent[] } | any, TimelineNode> {
  public readonly type = "CHRONOLOGY" as const;

  public validate(input: any): ValidationResult {
    const events: TimelineEvent[] = input?.events ?? input?.values ?? [];
    const errors: any[] = [];

    if (!events || events.length === 0) {
      return {
        valid: false,
        errors: [{ code: "DATASET_EMPTY", severity: "BLOCKING", field: "events", message: "La cronología requiere al menos un evento." }],
      };
    }

    // Validación temporal §18: event[n].timestamp <= event[n+1].timestamp
    for (let i = 0; i < events.length - 1; i++) {
      if (events[i].timestamp > events[i + 1].timestamp) {
        errors.push({
          code: "UNSORTED_EVENTS",
          severity: "BLOCKING",
          field: `events[${i}]`,
          message: `Evento desordenado: '${events[i].label}' (${events[i].timestamp}) ocurre después de '${events[i + 1].label}' (${events[i + 1].timestamp}).`,
        });
      }
    }

    return {
      valid: errors.filter((e) => e.severity === "BLOCKING").length === 0,
      errors,
    };
  }

  public normalize(input: any): NormalizedVisualizationData {
    const events: TimelineEvent[] = input?.events ?? input?.values ?? [];
    const timestamps = events.map((e) => e.timestamp);
    const min = timestamps.length ? Math.min(...timestamps) : 0;
    const max = timestamps.length ? Math.max(...timestamps) : 1;
    const range = max === min ? 1 : max - min;

    return {
      minValue: min,
      maxValue: max,
      range,
      isConstant: min === max,
      normalizedPoints: events.map((e) => ({
        original: { label: e.label, value: e.timestamp, timestamp: e.timestamp },
        normalizedValue: range === 0 ? 0.5 : (e.timestamp - min) / range,
        normalizedTime: range === 0 ? 0.5 : (e.timestamp - min) / range,
      })),
    };
  }

  public compile(
    input: any,
    context: VisualizationCompileContext | any = {}
  ): any {
    if (input && (input.spec || (input.dataset && input.spec))) {
      return InternalGenerator.compile(input);
    }

    const events: TimelineEvent[] = input?.events ?? input?.values ?? [];
    const config: ChronologyTimelineConfig = context.config ?? context ?? {};
    const orientation = config.orientation ?? "HORIZONTAL";
    const width = context.width ?? 1920;
    const height = context.height ?? 1080;

    // Validación temporal estricta (§18)
    const valResult = this.validate(input);
    const unsortedPolicy = config.unsortedPolicy ?? "BLOCKING";
    if (!valResult.valid && unsortedPolicy === "BLOCKING") {
      const err = valResult.errors[0];
      throw new Error(`[DATA_VALIDATION_ERROR] ${err.code}: ${err.message}`);
    }

    // Si permite ordenar
    const sortedEvents = [...events].sort((a, b) => a.timestamp - b.timestamp);
    const timestamps = sortedEvents.map((e) => e.timestamp);
    const minT = timestamps[0] ?? 0;
    const maxT = timestamps[timestamps.length - 1] ?? 1;
    const rangeT = maxT === minT ? 1 : maxT - minT;

    const bounds = { x: 150, y: 150, width: width - 300, height: height - 300 };
    const axisY = bounds.y + bounds.height / 2;
    const axis = {
      x1: bounds.x,
      y1: axisY,
      x2: bounds.x + bounds.width,
      y2: axisY,
    };

    const nodeEvents = sortedEvents.map((ev) => {
      const progress = rangeT === 0 ? 0.5 : (ev.timestamp - minT) / rangeT;
      const x = bounds.x + progress * bounds.width;
      const y = axisY;
      return {
        event: ev,
        normalizedProgress: progress,
        x,
        y,
      };
    });

    const node: TimelineNode = {
      id: `timeline_${input.id ?? "events"}`,
      type: "CHRONOLOGY",
      startTimeSeconds: context.startTimeSeconds ?? 0,
      durationSeconds: config.animationDurationSeconds ?? 8.0,
      bounds,
      orientation,
      axis,
      events: nodeEvents,
      style: {
        primaryColor: "#000000",
        accentColor: "#FF1424",
        backgroundColor: "#FFFFFF",
        fontFamily: "Impact",
        fontWeight: 900,
        labelSize: 22,
        valueSize: 28,
      },
      provenance: ProvenanceTracker.createProvenance(input.id ?? "events"),
    };

    return node;
  }

  // Compatibilidad estática
  public static compile(params: any): any {
    const inst = new ChronologyTimelineGenerator();
    if (params.spec || (params.dataset && params.spec)) {
      return InternalGenerator.compile(params);
    }
    return inst.compile(params.dataset ?? params, params);
  }
}
