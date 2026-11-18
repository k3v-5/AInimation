import { ValidationError } from "../../errors/index.js";
import { Transform } from "../../transform/Transform.js";
import { GraphicElement, GraphicPreset } from "../types/index.js";

/**
 * Registro de presets de componentes gráficos semánticos para IA (Fase 5J).
 */
export class GraphicPresetRegistry {
  private static presets = new Map<string, GraphicPreset>();

  public static register(preset: GraphicPreset): void {
    if (!preset || !preset.id) {
      throw new ValidationError("Graphic preset requires a valid 'id'.");
    }
    if (this.presets.has(preset.id)) {
      throw new ValidationError(`DUPLICATE_GRAPHIC_PRESET: Preset '${preset.id}' already exists.`);
    }
    this.presets.set(preset.id, preset);
  }

  public static get(id: string): GraphicPreset {
    const p = this.presets.get(id);
    if (!p) {
      throw new ValidationError(`GRAPHIC_PRESET_NOT_FOUND: Preset '${id}' is not registered.`);
    }
    return p;
  }

  public static has(id: string): boolean {
    return this.presets.has(id);
  }

  public static list(): GraphicPreset[] {
    return Array.from(this.presets.values());
  }

  public static clear(): void {
    this.presets.clear();
  }
}

export const BuiltinGraphicPresets: GraphicPreset[] = [
  {
    id: "modern-card",
    name: "Modern UI Card",
    category: "information",
    description: "Rounded glassmorphism card for titles, explanations and UI popups.",
    parameters: { width: 600, height: 250, radius: 24 },
    createElements: (params) => {
      const w = params.width ?? 600;
      const h = params.height ?? 250;
      const r = params.radius ?? 24;
      return [
        {
          id: "card_bg",
          geometry: { type: "rounded-rectangle", width: w, height: h, radius: r },
          style: {
            fill: { type: "solid", color: { r: 0.1, g: 0.1, b: 0.15, a: 0.9 } },
            stroke: { color: { r: 0.3, g: 0.3, b: 0.5, a: 0.6 }, width: 2, opacity: 1 },
            opacity: 1.0,
          },
          transform: new Transform(),
        },
      ];
    },
  },
  {
    id: "highlight-circle",
    name: "Animated Highlight Circle",
    category: "attention",
    description: "Animated circular stroke for drawing attention to subjects or objects.",
    parameters: { radius: 80, strokeWidth: 6 },
    createElements: (params) => {
      const rad = params.radius ?? 80;
      const sw = params.strokeWidth ?? 6;
      return [
        {
          id: "circle_highlight",
          geometry: { type: "ellipse", width: rad * 2, height: rad * 2 },
          style: {
            stroke: { color: { r: 1.0, g: 0.2, b: 0.2, a: 1.0 }, width: sw, opacity: 1 },
            opacity: 1.0,
          },
          transform: new Transform(),
          trimPaths: { start: 0, end: 1, offset: 0 },
        },
      ];
    },
  },
  {
    id: "warning-badge",
    name: "Alert / Warning Badge",
    category: "warning",
    description: "Bright warning pill badge for notifications or caution points.",
    parameters: { width: 180, height: 48 },
    createElements: (params) => {
      const w = params.width ?? 180;
      const h = params.height ?? 48;
      return [
        {
          id: "badge_bg",
          geometry: { type: "rounded-rectangle", width: w, height: h, radius: h / 2 },
          style: {
            fill: { type: "solid", color: { r: 1.0, g: 0.3, b: 0.0, a: 1.0 } },
            opacity: 1.0,
          },
          transform: new Transform(),
        },
      ];
    },
  },
];

for (const p of BuiltinGraphicPresets) {
  if (!GraphicPresetRegistry.has(p.id)) {
    GraphicPresetRegistry.register(p);
  }
}
