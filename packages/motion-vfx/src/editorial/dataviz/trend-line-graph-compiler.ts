import {
  DEFAULT_DURATIONS_SEC,
  DEFAULT_EDITORIAL_COLORS,
  DEFAULT_LINE_WRITE_ON_SEC,
} from "./constants.js";
import { DataNormalizer } from "./data-normalizer.js";
import { DataVizIRBuilder } from "./dataviz-ir.js";
import { LayoutEngine } from "./layout-engine.js";
import { LinearScale } from "./scale-engine.js";
import {
  DataVizAnimation,
  DataVizElement,
  DataVizIR,
  DataVizScale,
  DataVizStyleProfile,
  DataSet,
  Point2D,
  TrendLineOptions,
} from "./types.js";

/**
 * REQ-025 §26 to §29: Trend Line Graph Compiler.
 */
export class TrendLineGraphCompiler {
  public static compile(dataset: DataSet, options: TrendLineOptions = {}): DataVizIR {
    const compositionPreset = options.composition ?? "LANDSCAPE_16_9";
    const layout = LayoutEngine.computeLayout(compositionPreset);
    const normalizedData = DataNormalizer.normalizeDataset(dataset);

    const fps = options.fps ?? 30;
    const durationSeconds = options.durationSeconds ?? DEFAULT_DURATIONS_SEC.LINE_GRAPH;
    const writeOnDuration = options.writeOnDurationSeconds ?? DEFAULT_LINE_WRITE_ON_SEC;
    const strokeWidthPx = options.strokeWidthPx ?? 4;
    const showPoints = options.showPoints ?? true;
    const showBaseline = options.showBaseline ?? true;

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
      valueSize: options.styleProfile?.valueSize ?? 28,
      tracking: options.styleProfile?.tracking ?? 2,
      cornerRadius: options.styleProfile?.cornerRadius ?? 4,
      motionPreset: options.styleProfile?.motionPreset ?? "EDITORIAL",
    };

    let points = [...normalizedData.points];
    if (options.sortByDate) {
      points.sort((a, b) => (a.timestampSeconds ?? 0) - (b.timestampSeconds ?? 0));
    }

    const count = points.length;
    const elements: DataVizElement[] = [];
    const animations: DataVizAnimation[] = [];
    const scales: DataVizScale[] = [];

    // Chart content box reserving room for padding
    const chartLeft = layout.contentBounds.x + 60;
    const chartRight = layout.contentBounds.x + layout.contentBounds.width - 40;
    const chartTop = layout.contentBounds.y + 40;
    const chartBottom = layout.contentBounds.y + layout.contentBounds.height - 40;

    // X scale: index 0 to count - 1
    const xScale = new LinearScale([0, Math.max(1, count - 1)], [chartLeft, chartRight]);
    scales.push(xScale.toIRScale("x_scale"));

    // Y scale: min to max
    const yScale = new LinearScale([normalizedData.minValue, normalizedData.maxValue], [chartBottom, chartTop]);
    scales.push(yScale.toIRScale("y_scale"));

    // Baseline axis
    if (showBaseline) {
      const baselineY = yScale.map(Math.max(0, normalizedData.minValue));
      elements.push({
        id: `axis_baseline_${dataset.id}`,
        type: "AXIS",
        position: { x: chartLeft, y: baselineY },
        bounds: { x: chartLeft, y: baselineY, width: chartRight - chartLeft, height: 2 },
        dataBinding: { datasetId: dataset.id, dataPointId: "baseline", sourcePath: "baseline" },
        properties: {
          x1: chartLeft,
          y1: baselineY,
          x2: chartRight,
          y2: baselineY,
          color: "#444444",
          thicknessPx: 2,
        },
      });
    }

    // Map vertex positions
    const vertices: Point2D[] = points.map((p, i) => ({
      x: xScale.map(i),
      y: yScale.map(p.value),
    }));

    // Calculate total Euclidean path length (§28)
    let totalPathLength = 0;
    for (let i = 0; i < vertices.length - 1; i++) {
      const dx = vertices[i + 1].x - vertices[i].x;
      const dy = vertices[i + 1].y - vertices[i].y;
      totalPathLength += Math.sqrt(dx * dx + dy * dy);
    }

    // 1. Full Line element
    const lineId = `line_${dataset.id}`;
    elements.push({
      id: lineId,
      type: "LINE",
      position: vertices[0] ?? { x: chartLeft, y: chartBottom },
      bounds: {
        x: chartLeft,
        y: chartTop,
        width: chartRight - chartLeft,
        height: chartBottom - chartTop,
      },
      dataBinding: { datasetId: dataset.id, dataPointId: "all", sourcePath: "points" },
      properties: {
        vertices,
        pathLengthPx: Number(totalPathLength.toFixed(4)),
        color: style.accentColor,
        strokeWidthPx,
      },
    });

    // Stroke write-on animation (§28)
    animations.push({
      id: `anim_write_on_${lineId}`,
      targetId: lineId,
      property: "PATH_PROGRESS",
      startSeconds: 0.2,
      endSeconds: Math.min(durationSeconds, 0.2 + writeOnDuration),
      easing: "EASE_OUT_CUBIC",
      from: 0.0,
      to: 1.0,
    });

    // 2. Vertex Points & Key Points Highlight (§29)
    if (showPoints) {
      // Identify key points: first, last, min, max, primary
      let minPt = points[0];
      let maxPt = points[0];
      for (const pt of points) {
        if (pt.value < minPt.value) minPt = pt;
        if (pt.value > maxPt.value) maxPt = pt;
      }

      points.forEach((pt, i) => {
        const v = vertices[i];
        const isFirst = i === 0;
        const isLast = i === count - 1;
        const isMin = pt.id === minPt.id;
        const isMax = pt.id === maxPt.id;
        const isPrimary = pt.emphasis === "PRIMARY";
        const isKeyPoint = isFirst || isLast || isMin || isMax || isPrimary;

        const ptId = `point_${dataset.id}_${pt.id}`;
        const radius = isKeyPoint ? 6 : 4;
        const color = isPrimary || isMax ? style.accentColor : "#FFFFFF";

        elements.push({
          id: ptId,
          type: "POINT",
          position: v,
          bounds: { x: v.x - radius, y: v.y - radius, width: radius * 2, height: radius * 2 },
          dataBinding: { datasetId: dataset.id, dataPointId: pt.id, sourcePath: `points.${i}.value` },
          properties: {
            radius,
            color,
            isKeyPoint,
            value: pt.value,
          },
        });

        // Appears as write-on reaches the point
        const pointAppearRatio = count > 1 ? i / (count - 1) : 0;
        const pointStartTime = Number((0.2 + writeOnDuration * pointAppearRatio).toFixed(4));

        animations.push({
          id: `anim_appear_${ptId}`,
          targetId: ptId,
          property: "OPACITY",
          startSeconds: Math.min(durationSeconds - 0.1, pointStartTime),
          endSeconds: Math.min(durationSeconds, pointStartTime + 0.2),
          easing: "EASE_OUT_CUBIC",
          from: 0.0,
          to: 1.0,
        });

        // Key point value label
        if (isKeyPoint) {
          const labelId = `label_kp_${dataset.id}_${pt.id}`;
          const labelY = v.y - 18;

          elements.push({
            id: labelId,
            type: "LABEL",
            position: { x: v.x, y: labelY },
            bounds: { x: v.x - 40, y: labelY, width: 80, height: 16 },
            dataBinding: { datasetId: dataset.id, dataPointId: pt.id, sourcePath: `points.${i}.label` },
            properties: {
              text: `${pt.label}: ${pt.value}`,
              color: style.textColor,
              fontSize: style.labelSize,
              fontFamily: style.labelFontFamily,
              emphasis: pt.emphasis,
            },
          });
        }
      });
    }

    return DataVizIRBuilder.build({
      id: `dtv_line_${dataset.id}`,
      type: "LINE_GRAPH",
      composition: {
        width: layout.bounds.width,
        height: layout.bounds.height,
        fps,
        durationSeconds,
      },
      dataset: {
        id: dataset.id,
        points,
      },
      layout,
      scales,
      elements,
      animations,
      style,
      title: dataset.title,
      source: dataset.source,
      editorialProfileId: options.editorialProfileId,
    });
  }
}
