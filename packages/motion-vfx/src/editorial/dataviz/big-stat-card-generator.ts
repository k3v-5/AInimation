import {
  DEFAULT_BIG_STAT_GROWTH_SEC,
  DEFAULT_DURATIONS_SEC,
  DEFAULT_EDITORIAL_COLORS,
} from "./constants.js";
import { DataVizIRBuilder } from "./dataviz-ir.js";
import { LayoutEngine } from "./layout-engine.js";
import { NumberFormatter } from "./number-formatter.js";
import {
  BigStatData,
  BigStatOptions,
  DataVizAnimation,
  DataVizElement,
  DataVizIR,
  DataVizStyleProfile,
} from "./types.js";
import { validateBigStatData } from "./validators.js";

/**
 * REQ-025 §30 to §34 & §115: Big Stat Card Generator.
 * TIME Editorial / Poster Style high-impact statistical card.
 */
export class BigStatCardGenerator {
  public static compile(data: BigStatData, options: BigStatOptions = {}): DataVizIR {
    const validated = validateBigStatData(data);
    const compositionPreset = options.composition ?? "LANDSCAPE_16_9";
    const layout = LayoutEngine.computeLayout(compositionPreset);

    const fps = options.fps ?? 30;
    const durationSeconds = options.durationSeconds ?? DEFAULT_DURATIONS_SEC.BIG_STAT;
    const showAccentLine = options.showAccentLine ?? true;
    const accentLineHeightPx = options.accentLineHeightPx ?? 4;

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
      titleSize: options.styleProfile?.titleSize ?? (compositionPreset === "VERTICAL_9_16" ? 96 : 128),
      labelSize: options.styleProfile?.labelSize ?? 28,
      valueSize: options.styleProfile?.valueSize ?? 40,
      tracking: options.styleProfile?.tracking ?? 3,
      cornerRadius: options.styleProfile?.cornerRadius ?? 4,
      motionPreset: options.styleProfile?.motionPreset ?? "EDITORIAL",
    };

    const elements: DataVizElement[] = [];
    const animations: DataVizAnimation[] = [];

    // Center layout coordinates
    const centerX = layout.contentBounds.x + layout.contentBounds.width / 2;
    const centerY = layout.contentBounds.y + layout.contentBounds.height / 2;

    const isNumeric = typeof validated.value === "number";
    let decimals = 2;
    if (isNumeric) {
      const num = validated.value as number;
      if (Math.abs(num) >= 1e6 && (num / 1e5) % 1 === 0 && (num / 1e6) % 1 !== 0) {
        decimals = 1;
      }
    }
    const displayValue = isNumeric
      ? NumberFormatter.format(validated.value as number, { unit: validated.unit, decimals })
      : String(validated.value);

    // 1. Dominant Value Element (§31)
    const valId = "stat_dominant_value";
    const valY = centerY - 50;
    const estimatedValWidth = displayValue.length * (style.titleSize * 0.55);

    elements.push({
      id: valId,
      type: isNumeric ? "COUNTER" : "CARD",
      position: { x: centerX, y: valY },
      bounds: {
        x: centerX - estimatedValWidth / 2,
        y: valY - style.titleSize / 2,
        width: estimatedValWidth,
        height: style.titleSize,
      },
      dataBinding: { datasetId: "big_stat", dataPointId: "main_value", sourcePath: "value" },
      properties: {
        rawNumericValue: isNumeric ? validated.value : undefined,
        displayValue,
        color: style.textColor,
        fontFamily: style.titleFontFamily,
        fontSize: style.titleSize,
        tracking: style.tracking,
        align: "CENTER",
      },
    });

    animations.push({
      id: `anim_scale_${valId}`,
      targetId: valId,
      property: "SCALE",
      startSeconds: 0.1,
      endSeconds: Math.min(durationSeconds, 0.1 + DEFAULT_BIG_STAT_GROWTH_SEC),
      easing: "EASE_OUT_CUBIC",
      from: 0.8,
      to: 1.0,
    });

    animations.push({
      id: `anim_opacity_${valId}`,
      targetId: valId,
      property: "OPACITY",
      startSeconds: 0.1,
      endSeconds: 0.4,
      easing: "LINEAR",
      from: 0.0,
      to: 1.0,
    });

    // 2. Vector Accent Divider Line (§34)
    if (showAccentLine) {
      const divId = "stat_accent_divider";
      const divY = centerY + 20;
      const divWidth = Math.min(layout.contentBounds.width * 0.4, Math.max(140, estimatedValWidth * 0.7));

      elements.push({
        id: divId,
        type: "DIVIDER",
        position: { x: centerX, y: divY },
        bounds: { x: centerX - divWidth / 2, y: divY, width: divWidth, height: accentLineHeightPx },
        properties: {
          x1: centerX - divWidth / 2,
          y1: divY,
          x2: centerX + divWidth / 2,
          y2: divY,
          color: style.accentColor,
          thicknessPx: accentLineHeightPx,
        },
      });

      animations.push({
        id: `anim_scale_${divId}`,
        targetId: divId,
        property: "SCALE",
        startSeconds: 0.3,
        endSeconds: 0.8,
        easing: "EASE_OUT_CUBIC",
        from: [0.0, 1.0],
        to: [1.0, 1.0],
      });
    }

    // 3. Secondary Label Element (§31)
    const labelId = "stat_secondary_label";
    const labelY = centerY + 55;
    const labelText = validated.label.toUpperCase();
    const estLabelWidth = labelText.length * 14;

    elements.push({
      id: labelId,
      type: "LABEL",
      position: { x: centerX, y: labelY },
      bounds: { x: centerX - estLabelWidth / 2, y: labelY, width: estLabelWidth, height: 30 },
      dataBinding: { datasetId: "big_stat", dataPointId: "main_label", sourcePath: "label" },
      properties: {
        text: labelText,
        color: style.mutedColor,
        fontFamily: style.labelFontFamily,
        fontSize: style.labelSize,
        tracking: 2,
        align: "CENTER",
      },
    });

    animations.push({
      id: `anim_opacity_${labelId}`,
      targetId: labelId,
      property: "OPACITY",
      startSeconds: 0.4,
      endSeconds: 0.8,
      easing: "LINEAR",
      from: 0.0,
      to: 1.0,
    });

    // 4. Optional Context Element
    if (validated.context) {
      const ctxId = "stat_context";
      const ctxY = centerY + 100;
      elements.push({
        id: ctxId,
        type: "LABEL",
        position: { x: centerX, y: ctxY },
        bounds: { x: centerX - 200, y: ctxY, width: 400, height: 24 },
        properties: {
          text: validated.context,
          color: style.mutedColor,
          fontSize: 18,
          align: "CENTER",
        },
      });
    }

    // 5. Optional Source Attribution
    if (validated.source) {
      const srcId = "stat_source";
      const srcY = layout.contentBounds.y + layout.contentBounds.height - 20;
      elements.push({
        id: srcId,
        type: "LABEL",
        position: { x: layout.contentBounds.x, y: srcY },
        bounds: { x: layout.contentBounds.x, y: srcY, width: 300, height: 16 },
        properties: {
          text: `Source: ${validated.source}`,
          color: style.mutedColor,
          fontSize: 14,
          align: "LEFT",
        },
      });
    }

    const rawValueNumber = typeof validated.value === "number" ? validated.value : 1.0;

    return DataVizIRBuilder.build({
      id: "dtv_big_stat",
      type: "BIG_STAT",
      composition: {
        width: layout.bounds.width,
        height: layout.bounds.height,
        fps,
        durationSeconds,
      },
      dataset: {
        id: "ds_big_stat",
        points: [
          {
            id: "stat_pt_0",
            label: validated.label,
            value: rawValueNumber,
            normalizedValue: 1.0,
            unit: validated.unit,
            source: validated.source,
            emphasis: validated.emphasis,
          },
        ],
      },
      layout,
      scales: [],
      elements,
      animations,
      style,
      title: validated.label,
      source: validated.source,
      editorialProfileId: options.editorialProfileId,
    });
  }
}
