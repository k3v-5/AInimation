import {
  BigStatCardConfig,
  VisualizationContext,
  VisualizationIR,
  VisualizationElement,
  VisualizationAnimation,
  BigStatSpec,
  DataSet,
  VisualizationCompilationResult,
} from "./types.js";
import { DEFAULT_VISUALIZATION_VIEWPORT, DEFAULT_VISUALIZATION_THEME } from "./constants.js";
import { computePlotArea } from "./geometry.js";
import { formatVisualizationNumber } from "./labels.js";
import { computeVisualizationChecksum } from "./checksum.js";
import { resolveSafeArea } from "./layout-engine.js";
import {
  formatNumberDeterministic,
  createCounterAnimation as legacyCreateCounterAnimation,
} from "./animation-utils.js";
import { computeVisualizationChecksum as legacyComputeChecksum } from "./visualization-hash.js";

/**
 * REQ-025 §19-§20: Generador determinista de tarjetas estadísticas de alto impacto (Big Stat Card).
 */
export function generateBigStatCard(
  configOrSpec: BigStatCardConfig | BigStatSpec | any,
  contextOrDataset?: VisualizationContext | DataSet | null
): VisualizationIR & VisualizationCompilationResult {
  // 1. Detección de especificación legacy BigStatSpec
  const isLegacySpec =
    configOrSpec &&
    (configOrSpec.type === "BIG_STAT_CARD" ||
      configOrSpec.safeZone !== undefined ||
      configOrSpec.style !== undefined);

  if (!isLegacySpec && typeof configOrSpec.value === "number" && typeof configOrSpec.label === "string") {
    const config: BigStatCardConfig = {
      value: configOrSpec.value,
      label: configOrSpec.label,
      unit: configOrSpec.unit,
      prefix: configOrSpec.prefix,
      suffix: configOrSpec.suffix,
      animationDurationSeconds: configOrSpec.animationDurationSeconds || 1.8,
      showDivider: configOrSpec.showDivider !== false,
    };

    const context: VisualizationContext = (contextOrDataset && !("rows" in contextOrDataset)) ? contextOrDataset : {};
    const viewport = { ...DEFAULT_VISUALIZATION_VIEWPORT, ...context.viewport };
    const theme = { ...DEFAULT_VISUALIZATION_THEME, ...context.theme };
    const plot = computePlotArea(viewport);

    const centerX = Number((plot.x + plot.width / 2).toFixed(2));
    const centerY = Number((plot.y + plot.height / 2).toFixed(2));

    const elements: VisualizationElement[] = [];
    const animations: VisualizationAnimation[] = [];

    // Fondo
    elements.push({
      id: "chart-bg",
      type: "RECT",
      x: 0,
      y: 0,
      width: viewport.width,
      height: viewport.height,
      fill: theme.backgroundColor,
      opacity: 1,
    });

    const formattedValue = formatVisualizationNumber(config.value, {
      prefix: config.prefix,
      suffix: config.suffix,
      unit: config.unit,
      useGrouping: true,
    });

    // 1. Valor estadístico gigante
    elements.push({
      id: "big-stat-value",
      type: "COUNTER",
      x: centerX,
      y: centerY - 40,
      text: formattedValue,
      fill: theme.primaryColor,
      strokeWidth: 0,
      opacity: 1,
    });

    animations.push({
      id: "anim-scale-big-stat-val",
      elementId: "big-stat-value",
      property: "scale",
      easing: "EASE_OUT",
      keyframes: [
        { timeSeconds: 0, value: 0.8 },
        { timeSeconds: Number(config.animationDurationSeconds.toFixed(4)), value: 1.0 },
      ],
    });

    // 2. Divisor editorial
    if (config.showDivider) {
      const dividerWidth = Math.min(300, plot.width * 0.4);
      elements.push({
        id: "big-stat-divider",
        type: "LINE_SEGMENT",
        x: centerX - dividerWidth / 2,
        y: centerY + 30,
        width: dividerWidth,
        height: 0,
        stroke: theme.primaryColor,
        strokeWidth: 4,
        opacity: 1,
      });
    }

    // 3. Etiqueta / descripción
    elements.push({
      id: "big-stat-label",
      type: "LABEL",
      x: centerX,
      y: centerY + 70,
      text: config.label.toUpperCase(),
      fill: theme.textColor,
      opacity: 1,
    });

    animations.push({
      id: "anim-fade-big-stat-lbl",
      elementId: "big-stat-label",
      property: "opacity",
      easing: "EASE_OUT",
      keyframes: [
        { timeSeconds: 0.2, value: 0 },
        { timeSeconds: Number((0.2 + config.animationDurationSeconds * 0.6).toFixed(4)), value: 1 },
      ],
    });

    const ir: any = {
      id: "vis-big-stat-card",
      type: "BIG_STAT",
      viewport,
      theme,
      elements,
      animations,
      layers: [],
      metadata: {
        engineVersion: "4.0.0",
        requirementId: "REQ-025",
        datasetId: "stat-card",
        profileId: context.editorialProfile ?? "TIME_EDITORIAL",
        sourceCount: 1,
      },
      cognitiveMetadata: {
        activeElements: elements.length,
        textElements: 2,
        numericElements: 1,
        animationCount: animations.length,
      },
      pacingMetadata: {
        visualDurationSeconds: Number((config.animationDurationSeconds + 2.0).toFixed(2)),
        animationDurationSeconds: Number(config.animationDurationSeconds.toFixed(2)),
      },
      editorialIntensity: "PEAK",
      checksumSha256: "",
      success: true,
      errors: [],
      warnings: [],
    };

    ir.checksumSha256 = computeVisualizationChecksum(ir);
    ir.ir = ir;
    return ir;
  }

  // 2. Ruta legacy para BigStatSpec
  const spec: BigStatSpec = configOrSpec;
  const safeArea = resolveSafeArea(spec.width, spec.height, spec.safeZone);
  const layers: any[] = [];
  let zIndex = 1;

  if (spec.style.backgroundColor) {
    layers.push({
      id: `${spec.id}_bg`,
      name: "DV::BACKGROUND",
      type: "SHAPE",
      zIndex: zIndex++,
      transform: {
        position: { x: 0, y: 0 },
        scale: { x: 1, y: 1 },
        rotation: 0,
        anchor: { x: 0, y: 0 },
      },
      opacity: 1,
      geometry: {
        kind: "RECT",
        x: 0,
        y: 0,
        width: spec.width,
        height: spec.height,
        fillColor: spec.style.backgroundColor,
      },
    });
  }

  const centerX = safeArea.left + safeArea.width / 2;
  const centerY = safeArea.top + safeArea.height / 2;

  let displayValue = String(spec.value);
  if (typeof spec.value === "number") {
    displayValue = formatNumberDeterministic(
      spec.value,
      spec.format,
      (spec as any).decimals !== undefined ? (spec as any).decimals : (spec.format === "CURRENCY" ? 0 : 1),
      spec.prefix || "",
      spec.suffix || ""
    );
  }

  const counterAnim = legacyCreateCounterAnimation(
    Number(spec.value) || 0,
    spec.startTimeSeconds,
    spec.animation.entranceDurationSeconds,
    spec.animation.easing
  );

  layers.push({
    id: `${spec.id}_val`,
    name: "DV::STAT::VALUE",
    type: "TEXT",
    zIndex: zIndex++,
    transform: {
      position: { x: centerX, y: centerY - 40 },
      scale: { x: 1, y: 1 },
      rotation: 0,
      anchor: { x: 0.5, y: 0.5 },
    },
    opacity: 1,
    text: {
      content: displayValue,
      fontFamily: spec.style.fontFamily,
      fontSize: spec.style.valueFontSize * 2.2,
      fontWeight: spec.style.fontWeight,
      fillColor: spec.style.primaryColor,
      tracking: spec.style.tracking,
      justification: "CENTER",
    },
    animation: { properties: [counterAnim] },
    animations: [counterAnim],
  });

  layers.push({
    id: `${spec.id}_lbl`,
    name: "DV::STAT::LABEL",
    type: "TEXT",
    zIndex: zIndex++,
    transform: {
      position: { x: centerX, y: centerY + 60 },
      scale: { x: 1, y: 1 },
      rotation: 0,
      anchor: { x: 0.5, y: 0.5 },
    },
    opacity: 1,
    text: {
      content: spec.label.toUpperCase(),
      fontFamily: spec.style.fontFamily,
      fontSize: spec.style.labelFontSize * 1.2,
      fontWeight: 700,
      fillColor: spec.style.textColor,
      tracking: 20,
      justification: "CENTER",
    },
  });

  if (spec.secondaryText) {
    layers.push({
      id: `${spec.id}_sec`,
      name: "DV::STAT::SECONDARY",
      type: "TEXT",
      zIndex: zIndex++,
      transform: {
        position: { x: centerX, y: centerY + 110 },
        scale: { x: 1, y: 1 },
        rotation: 0,
        anchor: { x: 0.5, y: 0.5 },
      },
      opacity: 0.8,
      text: {
        content: spec.secondaryText,
        fontFamily: spec.style.fontFamily,
        fontSize: spec.style.labelFontSize * 0.8,
        fontWeight: 400,
        fillColor: spec.style.textColor,
        tracking: 0,
        justification: "CENTER",
      },
    });
  }

  layers.push({
    id: `${spec.id}_line`,
    name: "DV::STAT::ACCENT_LINE",
    type: "LINE",
    zIndex: zIndex++,
    transform: {
      position: { x: centerX - 60, y: centerY + 20 },
      scale: { x: 1, y: 1 },
      rotation: 0,
      anchor: { x: 0, y: 0 },
    },
    opacity: 1,
    line: {
      x1: 0,
      y1: 0,
      x2: 120,
      y2: 0,
      strokeColor: spec.style.primaryColor,
      strokeWidth: 4,
    },
  });


  const legacyIR: any = {
    id: spec.id,
    type: "BIG_STAT_CARD",
    datasetId: (spec as any).datasetId || "isolated",
    durationSeconds: spec.durationSeconds,
    startTimeSeconds: spec.startTimeSeconds,
    width: spec.width,
    height: spec.height,
    viewport: {
      width: spec.width,
      height: spec.height,
      safeMarginTop: spec.safeZone.top,
      safeMarginRight: spec.safeZone.right,
      safeMarginBottom: spec.safeZone.bottom,
      safeMarginLeft: spec.safeZone.left,
    },
    theme: {
      backgroundColor: spec.style.backgroundColor,
      primaryColor: spec.style.primaryColor,
      secondaryColor: spec.style.secondaryColor,
      accentColor: spec.style.accentColor,
      textColor: spec.style.textColor,
      mutedTextColor: "#888888",
      gridColor: "#333333",
      negativeColor: "#FF4444",
      fontFamily: spec.style.fontFamily,
      fontWeight: spec.style.fontWeight,
    },
    elements: layers.map((l) => ({
      id: l.id,
      type: l.type === "TEXT" ? "TEXT" : "RECT",
      x: l.transform.position.x,
      y: l.transform.position.y,
      width: 100,
      height: 40,
      text: l.text ? l.text.content : undefined,
    })),
    layers,
    animations: [],
    metadata: {
      engineVersion: "4.0.0",
      requirementId: "REQ-025",
      datasetId: spec.id,
      profileId: "TIME_EDITORIAL",
      sourceCount: 1,
    },
    checksumSha256: "",
  };

  legacyIR.checksumSha256 = legacyComputeChecksum(legacyIR);

  return {
    success: true,
    ir: legacyIR,
    errors: [],
    warnings: [],
    metrics: {
      totalBars: 0,
      visibleBars: 0,
      clippedBars: 0,
    },
    ...legacyIR,
  };
}

export class BigStatCardGenerator {
  public static compile(specOrOptions: any, dataset?: any): VisualizationIR & VisualizationCompilationResult {
    if (specOrOptions && typeof specOrOptions === "object" && specOrOptions.card) {
      const card = specOrOptions.card;
      const asp = specOrOptions.aspectRatio;
      const vp = asp === "9:16" ? { width: 1080, height: 1920 } : asp === "1:1" ? { width: 1080, height: 1080 } : { width: 1920, height: 1080 };
      return generateBigStatCard(
        {
          value: card.value,
          label: card.label,
          unit: card.unit,
          prefix: card.prefix,
          suffix: card.suffix,
          animationDurationSeconds: specOrOptions.durationSeconds ?? 2.0,
          showDivider: card.divider !== undefined,
        },
        { viewport: vp }
      );
    }
    return generateBigStatCard(specOrOptions, dataset);
  }
}

