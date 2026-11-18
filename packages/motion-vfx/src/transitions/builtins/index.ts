import { TransitionDefinition, TransitionRegistry } from "../core/TransitionRegistry.js";

/**
 * Catálogo de transiciones estándar built-in (Fase 5C).
 */

export const CutTransition: TransitionDefinition = {
  type: "cut",
  name: "Cut",
  description: "Instant cut transition between scenes without temporal overlap.",
  parameters: [],
  evaluate: (ctx) => ({
    fromOpacity: ctx.progress < 1 ? 1 : 0,
    toOpacity: ctx.progress >= 1 ? 1 : 0,
  }),
};

export const CrossfadeTransition: TransitionDefinition = {
  type: "crossfade",
  name: "Crossfade",
  description: "Smooth linear/eased alpha crossfade blending outgoing and incoming scenes.",
  parameters: [],
  evaluate: (ctx) => ({
    fromOpacity: 1 - ctx.progress,
    toOpacity: ctx.progress,
  }),
};

export const DipToColorTransition: TransitionDefinition = {
  type: "dipToColor",
  name: "Dip to Color",
  description: "Dips from Scene A into a solid color (e.g. black or white) and rises into Scene B.",
  parameters: [
    { name: "color", type: "color", default: { r: 0, g: 0, b: 0 }, description: "Color to dip into." },
  ],
  evaluate: (ctx) => {
    const p = ctx.progress;
    const color = (ctx.params.color as any) ?? { r: 0, g: 0, b: 0 };

    if (p < 0.5) {
      const subProg = p * 2; // 0 -> 1
      return {
        fromOpacity: 1 - subProg,
        toOpacity: 0,
        colorOverlay: { color, opacity: subProg },
      };
    } else {
      const subProg = (p - 0.5) * 2; // 0 -> 1
      return {
        fromOpacity: 0,
        toOpacity: subProg,
        colorOverlay: { color, opacity: 1 - subProg },
      };
    }
  },
};

export const ZoomTransition: TransitionDefinition = {
  type: "zoom",
  name: "Zoom Transition",
  description: "Zooms in dynamically on Scene A and scales Scene B into focus with midpoint motion blur.",
  parameters: [
    { name: "amount", type: "number", default: 0.3, min: 0.0, max: 2.0, description: "Zoom scaling factor." },
    { name: "blur", type: "number", default: 15, min: 0, max: 100, description: "Midpoint blur intensity." },
  ],
  evaluate: (ctx) => {
    const p = ctx.progress;
    const amount = Number(ctx.params.amount ?? 0.3);
    const maxBlur = Number(ctx.params.blur ?? 15);
    const midBlur = Math.sin(p * Math.PI) * maxBlur;

    return {
      fromOpacity: p < 0.5 ? 1 : 1 - (p - 0.5) * 2,
      toOpacity: p >= 0.5 ? 1 : p * 2,
      fromTransform: {
        scale: 1.0 + p * amount,
      },
      toTransform: {
        scale: 1.0 - amount + p * amount,
      },
      fromBlur: midBlur,
      toBlur: midBlur,
    };
  },
};

export const SlideTransition: TransitionDefinition = {
  type: "slide",
  name: "Slide Transition",
  description: "Translates Scene A out and slides Scene B in from a chosen direction.",
  parameters: [
    { name: "direction", type: "enum", default: "left", values: ["left", "right", "up", "down"], description: "Slide direction." },
    { name: "distance", type: "number", default: 1920, min: 100, max: 8000, description: "Slide pixel distance." },
  ],
  evaluate: (ctx) => {
    const p = ctx.progress;
    const dir = String(ctx.params.direction ?? "left");
    const dist = Number(ctx.params.distance ?? 1920);

    let fromX = 0, fromY = 0, toX = 0, toY = 0;
    if (dir === "left") {
      fromX = -p * dist;
      toX = (1 - p) * dist;
    } else if (dir === "right") {
      fromX = p * dist;
      toX = -(1 - p) * dist;
    } else if (dir === "up") {
      fromY = -p * dist;
      toY = (1 - p) * dist;
    } else if (dir === "down") {
      fromY = p * dist;
      toY = -(1 - p) * dist;
    }

    return {
      fromOpacity: 1,
      toOpacity: 1,
      fromTransform: { translateX: fromX, translateY: fromY },
      toTransform: { translateX: toX, translateY: toY },
    };
  },
};

export const WhipTransition: TransitionDefinition = {
  type: "whip",
  name: "Whip Pan Transition",
  description: "High-speed whip pan translation with directional motion blur.",
  parameters: [
    { name: "direction", type: "enum", default: "left", values: ["left", "right", "up", "down"], description: "Whip direction." },
    { name: "blur", type: "number", default: 30, min: 0, max: 100, description: "Motion blur intensity." },
  ],
  evaluate: (ctx) => {
    const p = ctx.progress;
    const dir = String(ctx.params.direction ?? "left");
    const dist = 1920;
    const maxBlur = Number(ctx.params.blur ?? 30);
    const blurAmount = Math.sin(p * Math.PI) * maxBlur;

    const fromX = dir === "left" ? -p * dist : p * dist;
    const toX = dir === "left" ? (1 - p) * dist : -(1 - p) * dist;

    return {
      fromOpacity: 1 - p * 0.2,
      toOpacity: 0.8 + p * 0.2,
      fromTransform: { translateX: fromX },
      toTransform: { translateX: toX },
      fromBlur: blurAmount,
      toBlur: blurAmount,
    };
  },
};

export const BlurTransition: TransitionDefinition = {
  type: "blur",
  name: "Blur Transition",
  description: "Progressively blurs Scene A to maximum and focuses Scene B from blur to sharpness.",
  parameters: [
    { name: "amount", type: "number", default: 40, min: 0, max: 200, description: "Max blur radius in pixels." },
  ],
  evaluate: (ctx) => {
    const p = ctx.progress;
    const maxBlur = Number(ctx.params.amount ?? 40);

    return {
      fromOpacity: 1 - p,
      toOpacity: p,
      fromBlur: p * maxBlur,
      toBlur: (1 - p) * maxBlur,
    };
  },
};

export const FlashTransition: TransitionDefinition = {
  type: "flash",
  name: "White Flash Transition",
  description: "Additive white flash illuminating the midpoint transition between scenes.",
  parameters: [
    { name: "intensity", type: "number", default: 1.0, min: 0, max: 2.0, description: "Flash intensity multiplier." },
  ],
  evaluate: (ctx) => {
    const p = ctx.progress;
    const intensity = Number(ctx.params.intensity ?? 1.0);
    const flashOpacity = Math.sin(p * Math.PI) * Math.min(1.0, intensity);

    return {
      fromOpacity: p < 0.5 ? 1 : 1 - (p - 0.5) * 2,
      toOpacity: p >= 0.5 ? 1 : p * 2,
      colorOverlay: {
        color: { r: 1, g: 1, b: 1 },
        opacity: flashOpacity,
      },
    };
  },
};

export function registerBuiltinTransitions(): void {
  const defs = [
    CutTransition,
    CrossfadeTransition,
    DipToColorTransition,
    ZoomTransition,
    SlideTransition,
    WhipTransition,
    BlurTransition,
    FlashTransition,
  ];

  for (const def of defs) {
    if (!TransitionRegistry.has(def.type)) {
      TransitionRegistry.register(def);
    }
  }
}

// Auto-registro en tiempo de carga
registerBuiltinTransitions();
