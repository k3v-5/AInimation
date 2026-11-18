import {
  DEFAULT_DURATIONS_SEC,
  DEFAULT_EDITORIAL_COLORS,
  DEFAULT_TIMELINE_STAGGER_SEC,
} from "./constants.js";
import { DataVizIRBuilder } from "./dataviz-ir.js";
import { LayoutEngine } from "./layout-engine.js";
import { LinearScale } from "./scale-engine.js";
import {
  ChronologyOptions,
  DataVizAnimation,
  DataVizElement,
  DataVizIR,
  DataVizScale,
  DataVizStyleProfile,
  TimelineEvent,
} from "./types.js";
import { validateTimelineEvents } from "./validators.js";

interface ParsedEvent {
  event: TimelineEvent;
  timestampSeconds: number;
}

/**
 * REQ-025 §35 to §38 & §116, §117: Chronology Timeline Generator.
 * Compiles chronological events with UTC timestamp normalization and monotonic visual ordering.
 */
export class ChronologyTimelineGenerator {
  public static compile(events: TimelineEvent[], options: ChronologyOptions = {}): DataVizIR {
    const validated = validateTimelineEvents(events);
    const orientation = options.orientation ?? "HORIZONTAL";
    const compositionPreset = options.composition ?? "LANDSCAPE_16_9";
    const layout = LayoutEngine.computeLayout(compositionPreset);

    const fps = options.fps ?? 30;
    const durationSeconds = options.durationSeconds ?? DEFAULT_DURATIONS_SEC.CHRONOLOGY;
    const staggerSeconds = options.staggerSeconds ?? DEFAULT_TIMELINE_STAGGER_SEC;

    const style: DataVizStyleProfile = {
      primaryColor: options.styleProfile?.primaryColor ?? DEFAULT_EDITORIAL_COLORS.primary,
      accentColor: options.styleProfile?.accentColor ?? DEFAULT_EDITORIAL_COLORS.accent,
      backgroundColor: options.styleProfile?.backgroundColor ?? DEFAULT_EDITORIAL_COLORS.background,
      textColor: options.styleProfile?.textColor ?? DEFAULT_EDITORIAL_COLORS.text,
      mutedColor: options.styleProfile?.mutedColor ?? DEFAULT_EDITORIAL_COLORS.muted,
      positiveColor: options.styleProfile?.positiveColor ?? DEFAULT_EDITORIAL_COLORS.positive,
      negativeColor: options.styleProfile?.negativeColor ?? DEFAULT_EDITORIAL_COLORS.negative,
      titleFontFamily: options.styleProfile?.titleFontFamily ?? "Impact",
      titleFontWeight: options.styleProfile?.titleFontWeight ?? 900,
      labelFontFamily: options.styleProfile?.labelFontFamily ?? "Arial Black",
      labelFontWeight: options.styleProfile?.labelFontWeight ?? 800,
      titleSize: options.styleProfile?.titleSize ?? 64,
      labelSize: options.styleProfile?.labelSize ?? 20,
      valueSize: options.styleProfile?.valueSize ?? 24,
      tracking: options.styleProfile?.tracking ?? 2,
      cornerRadius: options.styleProfile?.cornerRadius ?? 4,
      motionPreset: options.styleProfile?.motionPreset ?? "EDITORIAL",
    };

    // 1. Normalización temporal en UTC (§37)
    const parsedEvents: ParsedEvent[] = validated.map((ev) => {
      let t: number;
      const cleanDate = ev.date.trim();

      if (/^\d{4}$/.test(cleanDate)) {
        t = parseInt(cleanDate, 10);
      } else {
        const ms = Date.parse(cleanDate);
        t = Number.isNaN(ms) ? 0 : ms / 1000.0;
      }

      return {
        event: ev,
        timestampSeconds: t,
      };
    });

    // 2. Ordenar cronológicamente determinista (§38)
    parsedEvents.sort((a, b) => {
      if (a.timestampSeconds !== b.timestampSeconds) {
        return a.timestampSeconds - b.timestampSeconds;
      }
      return a.event.id.localeCompare(b.event.id, "en", { numeric: true });
    });

    const elements: DataVizElement[] = [];
    const animations: DataVizAnimation[] = [];
    const scales: DataVizScale[] = [];

    const count = parsedEvents.length;
    const minTime = parsedEvents[0].timestampSeconds;
    const maxTime = parsedEvents[count - 1].timestampSeconds;

    if (orientation === "HORIZONTAL") {
      const axisY = layout.contentBounds.y + layout.contentBounds.height / 2;
      const startX = layout.contentBounds.x + 60;
      const endX = layout.contentBounds.x + layout.contentBounds.width - 60;

      // Central Axis Line
      elements.push({
        id: "timeline_central_axis",
        type: "AXIS",
        position: { x: startX, y: axisY },
        bounds: { x: startX, y: axisY, width: endX - startX, height: 3 },
        properties: {
          x1: startX,
          y1: axisY,
          x2: endX,
          y2: axisY,
          color: "#444444",
          thicknessPx: 3,
        },
      });

      const timeScale = new LinearScale([minTime, maxTime === minTime ? minTime + 1 : maxTime], [startX, endX]);
      scales.push(timeScale.toIRScale("time_scale"));

      // Position events with alternating above/below labels to prevent collisions (§38)
      parsedEvents.forEach((pe, i) => {
        const nodeX = timeScale.map(pe.timestampSeconds);
        const isAbove = i % 2 === 0;
        const isPeak = pe.event.importance === "PEAK" || pe.event.importance === "HIGH";

        const nodeId = `node_${pe.event.id}`;
        const nodeRadius = isPeak ? 8 : 6;
        const nodeColor = isPeak ? style.accentColor : style.textColor;

        // 1. TIMELINE NODE element
        elements.push({
          id: nodeId,
          type: "NODE",
          position: { x: nodeX, y: axisY },
          bounds: { x: nodeX - nodeRadius, y: axisY - nodeRadius, width: nodeRadius * 2, height: nodeRadius * 2 },
          dataBinding: { datasetId: "chronology", dataPointId: pe.event.id, sourcePath: `events.${i}.date` },
          properties: {
            radius: nodeRadius,
            color: nodeColor,
            importance: pe.event.importance,
            date: pe.event.date,
          },
        });

        const delay = Number((i * staggerSeconds).toFixed(4));

        animations.push({
          id: `anim_node_${nodeId}`,
          targetId: nodeId,
          property: "SCALE",
          startSeconds: delay,
          endSeconds: Math.min(durationSeconds, delay + 0.5),
          easing: "EASE_OUT_CUBIC",
          from: 0.0,
          to: 1.0,
        });

        // 2. DATE BADGE & LABEL
        const labelId = `label_${pe.event.id}`;
        const labelY = isAbove ? axisY - 35 : axisY + 25;
        const estLabelWidth = pe.event.label.length * 10;

        elements.push({
          id: labelId,
          type: "LABEL",
          position: { x: nodeX, y: labelY },
          bounds: { x: nodeX - estLabelWidth / 2, y: labelY, width: estLabelWidth, height: 24 },
          dataBinding: { datasetId: "chronology", dataPointId: pe.event.id, sourcePath: `events.${i}.label` },
          properties: {
            text: `${pe.event.date}: ${pe.event.label}`,
            color: isPeak ? style.accentColor : style.textColor,
            fontFamily: style.labelFontFamily,
            fontSize: style.labelSize,
            align: "CENTER",
            isAbove,
          },
        });

        animations.push({
          id: `anim_label_${labelId}`,
          targetId: labelId,
          property: "OPACITY",
          startSeconds: delay + 0.2,
          endSeconds: Math.min(durationSeconds, delay + 0.6),
          easing: "LINEAR",
          from: 0.0,
          to: 1.0,
        });
      });
    } else {
      // VERTICAL
      const axisX = layout.contentBounds.x + layout.contentBounds.width / 2;
      const startY = layout.contentBounds.y + 60;
      const endY = layout.contentBounds.y + layout.contentBounds.height - 60;

      elements.push({
        id: "timeline_central_axis",
        type: "AXIS",
        position: { x: axisX, y: startY },
        bounds: { x: axisX, y: startY, width: 3, height: endY - startY },
        properties: {
          x1: axisX,
          y1: startY,
          x2: axisX,
          y2: endY,
          color: "#444444",
          thicknessPx: 3,
        },
      });

      const timeScale = new LinearScale([minTime, maxTime === minTime ? minTime + 1 : maxTime], [startY, endY]);
      scales.push(timeScale.toIRScale("time_scale"));

      parsedEvents.forEach((pe, i) => {
        const nodeY = timeScale.map(pe.timestampSeconds);
        const isLeft = i % 2 === 0;
        const isPeak = pe.event.importance === "PEAK" || pe.event.importance === "HIGH";

        const nodeId = `node_${pe.event.id}`;
        const nodeRadius = isPeak ? 8 : 6;
        const nodeColor = isPeak ? style.accentColor : style.textColor;

        elements.push({
          id: nodeId,
          type: "NODE",
          position: { x: axisX, y: nodeY },
          bounds: { x: axisX - nodeRadius, y: nodeY - nodeRadius, width: nodeRadius * 2, height: nodeRadius * 2 },
          dataBinding: { datasetId: "chronology", dataPointId: pe.event.id, sourcePath: `events.${i}.date` },
          properties: {
            radius: nodeRadius,
            color: nodeColor,
            importance: pe.event.importance,
            date: pe.event.date,
          },
        });

        const delay = Number((i * staggerSeconds).toFixed(4));

        animations.push({
          id: `anim_node_${nodeId}`,
          targetId: nodeId,
          property: "SCALE",
          startSeconds: delay,
          endSeconds: Math.min(durationSeconds, delay + 0.5),
          easing: "EASE_OUT_CUBIC",
          from: 0.0,
          to: 1.0,
        });

        const labelId = `label_${pe.event.id}`;
        const labelX = isLeft ? axisX - 30 : axisX + 30;
        const estLabelWidth = pe.event.label.length * 10;

        elements.push({
          id: labelId,
          type: "LABEL",
          position: { x: labelX, y: nodeY },
          bounds: { x: isLeft ? labelX - estLabelWidth : labelX, y: nodeY - 12, width: estLabelWidth, height: 24 },
          dataBinding: { datasetId: "chronology", dataPointId: pe.event.id, sourcePath: `events.${i}.label` },
          properties: {
            text: `${pe.event.date}: ${pe.event.label}`,
            color: isPeak ? style.accentColor : style.textColor,
            fontFamily: style.labelFontFamily,
            fontSize: style.labelSize,
            align: isLeft ? "RIGHT" : "LEFT",
          },
        });
      });
    }

    const points = parsedEvents.map((pe, i) => ({
      id: pe.event.id,
      label: pe.event.label,
      value: pe.timestampSeconds,
      normalizedValue: count > 1 ? (pe.timestampSeconds - minTime) / Math.max(1, maxTime - minTime) : 0.5,
      date: pe.event.date,
      timestampSeconds: pe.timestampSeconds,
    }));

    return DataVizIRBuilder.build({
      id: "dtv_chronology",
      type: "CHRONOLOGY",
      composition: {
        width: layout.bounds.width,
        height: layout.bounds.height,
        fps,
        durationSeconds,
      },
      dataset: {
        id: "ds_chronology",
        points,
      },
      layout,
      scales,
      elements,
      animations,
      style,
      title: "Chronology Timeline",
      editorialProfileId: options.editorialProfileId,
    });
  }
}
