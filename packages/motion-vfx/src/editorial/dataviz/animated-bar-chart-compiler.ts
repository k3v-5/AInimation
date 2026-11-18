import {
  DEFAULT_BAR_GROWTH_SEC,
  DEFAULT_BAR_STAGGER_SEC,
  DEFAULT_BAR_WIDTH_RATIO,
  DEFAULT_DURATIONS_SEC,
  DEFAULT_EDITORIAL_COLORS,
} from "./constants.js";
import { DataNormalizer } from "./data-normalizer.js";
import { DataVizIRBuilder } from "./dataviz-ir.js";
import { LayoutEngine } from "./layout-engine.js";
import { NumberFormatter } from "./number-formatter.js";
import { LinearScale, ScaleEngine } from "./scale-engine.js";
import {
  BarChartOptions,
  DataVizAnimation,
  DataVizElement,
  DataVizIR,
  DataVizScale,
  DataVizStyleProfile,
  DataSet,
} from "./types.js";

/**
 * REQ-025 §17 to §23: Animated Bar Chart Compiler.
 */
export class AnimatedBarChartCompiler {
  public static compile(dataset: DataSet, options: BarChartOptions = {}): DataVizIR {
    const orientation = options.orientation ?? "VERTICAL";
    const compositionPreset = options.composition ?? "LANDSCAPE_16_9";
    const layout = LayoutEngine.computeLayout(compositionPreset);
    const normalizedData = DataNormalizer.normalizeDataset(dataset);

    const fps = options.fps ?? 30;
    const durationSeconds = options.durationSeconds ?? DEFAULT_DURATIONS_SEC.BAR_CHART;
    const staggerSeconds = options.staggerSeconds ?? DEFAULT_BAR_STAGGER_SEC;
    const barWidthRatio = options.barWidthRatio ?? DEFAULT_BAR_WIDTH_RATIO;
    const showBaseline = options.showBaseline ?? true;
    const showValues = options.showValues ?? true;
    const showLabels = options.showLabels ?? true;

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
      labelSize: options.styleProfile?.labelSize ?? 24,
      valueSize: options.styleProfile?.valueSize ?? 32,
      tracking: options.styleProfile?.tracking ?? 2,
      cornerRadius: options.styleProfile?.cornerRadius ?? 4,
      motionPreset: options.styleProfile?.motionPreset ?? "EDITORIAL",
    };

    const elements: DataVizElement[] = [];
    const animations: DataVizAnimation[] = [];
    const scales: DataVizScale[] = [];

    const points = normalizedData.points;
    const count = points.length;

    // Determine domain bounds: must include 0 for true baseline (§19)
    const domainMin = Math.min(0, normalizedData.minValue);
    const domainMax = Math.max(0, normalizedData.maxValue);

    if (orientation === "VERTICAL") {
      // Available dimensions
      const availableWidth = layout.contentBounds.width;
      const slotWidth = availableWidth / Math.max(1, count);
      const barWidth = Math.max(4, Number((slotWidth * barWidthRatio).toFixed(4)));
      const horizontalMargin = (slotWidth - barWidth) / 2.0;

      // Reserve vertical room for top values and bottom labels
      const topReservePx = showValues ? 40 : 10;
      const bottomReservePx = showLabels ? 40 : 10;
      const chartTopY = layout.contentBounds.y + topReservePx;
      const chartBottomY = layout.contentBounds.y + layout.contentBounds.height - bottomReservePx;

      // Y Scale: domainMin -> chartBottomY, domainMax -> chartTopY
      const yScale = new LinearScale([domainMin, domainMax], [chartBottomY, chartTopY]);
      scales.push(yScale.toIRScale("y_scale"));

      const baselineY = yScale.map(0); // REQ-025 §19

      // Baseline Axis
      if (showBaseline) {
        elements.push({
          id: `axis_baseline_${dataset.id}`,
          type: "AXIS",
          position: { x: layout.contentBounds.x, y: baselineY },
          bounds: { x: layout.contentBounds.x, y: baselineY, width: availableWidth, height: 2 },
          dataBinding: { datasetId: dataset.id, dataPointId: "baseline", sourcePath: "baseline" },
          properties: {
            x1: layout.contentBounds.x,
            y1: baselineY,
            x2: layout.contentBounds.x + availableWidth,
            y2: baselineY,
            color: "#333333",
            thicknessPx: 2,
          },
        });
      }

      points.forEach((pt, i) => {
        const slotX = layout.contentBounds.x + i * slotWidth;
        const barX = Number((slotX + horizontalMargin).toFixed(4));
        const valY = yScale.map(pt.value);

        let barY: number;
        let barHeight: number;

        if (pt.value >= 0) {
          barY = valY;
          barHeight = Math.max(2, baselineY - valY);
        } else {
          barY = baselineY;
          barHeight = Math.max(2, valY - baselineY);
        }

        const barId = `bar_${dataset.id}_${pt.id}`;
        const delay = Number((i * staggerSeconds).toFixed(4));
        const animEnd = Math.min(durationSeconds, delay + DEFAULT_BAR_GROWTH_SEC);

        // Color selection
        const barColor =
          pt.emphasis === "PRIMARY"
            ? style.accentColor
            : pt.value < 0
            ? style.negativeColor
            : style.primaryColor;

        // 1. BAR element
        elements.push({
          id: barId,
          type: "BAR",
          position: { x: barX, y: barY },
          bounds: { x: barX, y: barY, width: barWidth, height: barHeight },
          dataBinding: { datasetId: dataset.id, dataPointId: pt.id, sourcePath: `points.${i}.value` },
          properties: {
            width: barWidth,
            height: barHeight,
            value: pt.value,
            color: barColor,
            cornerRadius: style.cornerRadius,
          },
        });

        // Bar Growth Animation (§22)
        animations.push({
          id: `anim_growth_${barId}`,
          targetId: barId,
          property: "SCALE",
          startSeconds: delay,
          endSeconds: animEnd,
          easing: "EASE_OUT_CUBIC",
          from: [1.0, 0.0],
          to: [1.0, 1.0],
        });

        // 2. COUNTER element (§23)
        if (showValues) {
          const counterId = `val_${dataset.id}_${pt.id}`;
          const counterY = pt.value >= 0 ? barY - 24 : barY + barHeight + 8;
          const displayStr = NumberFormatter.format(pt.value, { unit: pt.unit ?? dataset.unit });

          elements.push({
            id: counterId,
            type: "COUNTER",
            position: { x: barX + barWidth / 2, y: counterY },
            bounds: { x: barX, y: counterY, width: barWidth, height: 20 },
            dataBinding: { datasetId: dataset.id, dataPointId: pt.id, sourcePath: `points.${i}.value` },
            properties: {
              rawNumericValue: pt.value,
              displayValue: displayStr,
              color: style.textColor,
              fontSize: style.valueSize,
              fontFamily: style.labelFontFamily,
              align: "CENTER",
            },
          });

          animations.push({
            id: `anim_counter_${counterId}`,
            targetId: counterId,
            property: "NUMERIC_VALUE",
            startSeconds: delay,
            endSeconds: animEnd,
            easing: "EASE_OUT_CUBIC",
            from: 0,
            to: pt.value,
          });
        }

        // 3. LABEL element
        if (showLabels) {
          const labelId = `label_${dataset.id}_${pt.id}`;
          const labelY = layout.contentBounds.y + layout.contentBounds.height - 24;

          elements.push({
            id: labelId,
            type: "LABEL",
            position: { x: barX + barWidth / 2, y: labelY },
            bounds: { x: slotX, y: labelY, width: slotWidth, height: 20 },
            dataBinding: { datasetId: dataset.id, dataPointId: pt.id, sourcePath: `points.${i}.label` },
            properties: {
              text: pt.label,
              color: style.mutedColor,
              fontSize: style.labelSize,
              fontFamily: style.labelFontFamily,
              align: "CENTER",
              emphasis: pt.emphasis,
            },
          });
        }
      });
    } else {
      // HORIZONTAL
      const availableHeight = layout.contentBounds.height;
      const slotHeight = availableHeight / Math.max(1, count);
      const barHeight = Math.max(4, Number((slotHeight * barWidthRatio).toFixed(4)));
      const verticalMargin = (slotHeight - barHeight) / 2.0;

      const leftReservePx = showLabels ? 140 : 10;
      const rightReservePx = showValues ? 100 : 10;
      const chartLeftX = layout.contentBounds.x + leftReservePx;
      const chartRightX = layout.contentBounds.x + layout.contentBounds.width - rightReservePx;

      const xScale = new LinearScale([domainMin, domainMax], [chartLeftX, chartRightX]);
      scales.push(xScale.toIRScale("x_scale"));

      const baselineX = xScale.map(0);

      if (showBaseline) {
        elements.push({
          id: `axis_baseline_${dataset.id}`,
          type: "AXIS",
          position: { x: baselineX, y: layout.contentBounds.y },
          bounds: { x: baselineX, y: layout.contentBounds.y, width: 2, height: availableHeight },
          dataBinding: { datasetId: dataset.id, dataPointId: "baseline", sourcePath: "baseline" },
          properties: {
            x1: baselineX,
            y1: layout.contentBounds.y,
            x2: baselineX,
            y2: layout.contentBounds.y + availableHeight,
            color: "#333333",
            thicknessPx: 2,
          },
        });
      }

      points.forEach((pt, i) => {
        const slotY = layout.contentBounds.y + i * slotHeight;
        const barY = Number((slotY + verticalMargin).toFixed(4));
        const valX = xScale.map(pt.value);

        let barX: number;
        let barWidth: number;

        if (pt.value >= 0) {
          barX = baselineX;
          barWidth = Math.max(2, valX - baselineX);
        } else {
          barX = valX;
          barWidth = Math.max(2, baselineX - valX);
        }

        const barId = `bar_${dataset.id}_${pt.id}`;
        const delay = Number((i * staggerSeconds).toFixed(4));
        const animEnd = Math.min(durationSeconds, delay + DEFAULT_BAR_GROWTH_SEC);

        const barColor =
          pt.emphasis === "PRIMARY"
            ? style.accentColor
            : pt.value < 0
            ? style.negativeColor
            : style.primaryColor;

        elements.push({
          id: barId,
          type: "BAR",
          position: { x: barX, y: barY },
          bounds: { x: barX, y: barY, width: barWidth, height: barHeight },
          dataBinding: { datasetId: dataset.id, dataPointId: pt.id, sourcePath: `points.${i}.value` },
          properties: {
            width: barWidth,
            height: barHeight,
            value: pt.value,
            color: barColor,
            cornerRadius: style.cornerRadius,
          },
        });

        animations.push({
          id: `anim_growth_${barId}`,
          targetId: barId,
          property: "SCALE",
          startSeconds: delay,
          endSeconds: animEnd,
          easing: "EASE_OUT_CUBIC",
          from: [0.0, 1.0],
          to: [1.0, 1.0],
        });

        if (showValues) {
          const counterId = `val_${dataset.id}_${pt.id}`;
          const counterX = pt.value >= 0 ? barX + barWidth + 12 : barX - 12;
          const displayStr = NumberFormatter.format(pt.value, { unit: pt.unit ?? dataset.unit });

          elements.push({
            id: counterId,
            type: "COUNTER",
            position: { x: counterX, y: barY + barHeight / 2 },
            bounds: { x: counterX, y: barY, width: rightReservePx, height: barHeight },
            dataBinding: { datasetId: dataset.id, dataPointId: pt.id, sourcePath: `points.${i}.value` },
            properties: {
              rawNumericValue: pt.value,
              displayValue: displayStr,
              color: style.textColor,
              fontSize: style.valueSize,
              fontFamily: style.labelFontFamily,
              align: pt.value >= 0 ? "LEFT" : "RIGHT",
            },
          });
        }

        if (showLabels) {
          const labelId = `label_${dataset.id}_${pt.id}`;
          const labelX = layout.contentBounds.x;

          elements.push({
            id: labelId,
            type: "LABEL",
            position: { x: labelX, y: barY + barHeight / 2 },
            bounds: { x: labelX, y: barY, width: leftReservePx - 10, height: barHeight },
            dataBinding: { datasetId: dataset.id, dataPointId: pt.id, sourcePath: `points.${i}.label` },
            properties: {
              text: pt.label,
              color: style.mutedColor,
              fontSize: style.labelSize,
              fontFamily: style.labelFontFamily,
              align: "RIGHT",
              emphasis: pt.emphasis,
            },
          });
        }
      });
    }

    return DataVizIRBuilder.build({
      id: `dtv_bar_${dataset.id}`,
      type: "BAR_CHART",
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
