import { MotionMacro } from "../types/index.js";

export const BuiltinMotionMacros: Record<string, MotionMacro> = {
  "high-impact-hook": {
    id: "high-impact-hook",
    name: "High Impact Hook Opening",
    description: "Coordinated hook animation with kinetic text pop, camera punch, and impact SFX.",
    parameters: { text: "NO COMETAS ESTE ERROR", accentWord: "ERROR" },
    elements: [
      {
        type: "text",
        timing: { start: 0, duration: 2.5 },
        params: { text: "NO COMETAS ESTE ERROR", emphasized: ["ERROR"] },
      },
      {
        type: "camera",
        timing: { start: 0, duration: 0.5 },
        params: { mode: "snapZoom", intensity: 0.8 },
      },
      {
        type: "sfx",
        timing: { start: 0.05, duration: 0.5 },
        params: { type: "impact", volume: 0.9 },
      },
    ],
  },
  "statistic-pop": {
    id: "statistic-pop",
    name: "Statistic Counter & Bar Pop",
    description: "Reveals a dynamic counter statistic with progress bar and accent pop.",
    parameters: { value: "73%", label: "De incremento en retención" },
    elements: [
      {
        type: "shape",
        timing: { start: 0, duration: 1.5 },
        params: { type: "progressBar", progress: 0.73 },
      },
      {
        type: "text",
        timing: { start: 0.2, duration: 2.0 },
        params: { text: "73%", scale: 1.5, glow: true },
      },
      {
        type: "sfx",
        timing: { start: 0.2, duration: 0.3 },
        params: { type: "pop", volume: 0.7 },
      },
    ],
  },
  "subscribe-cta": {
    id: "subscribe-cta",
    name: "Celebration CTA with Confetti",
    description: "Shows CTA callout with particle confetti explosion.",
    parameters: { callToAction: "¡Suscríbete para más!" },
    elements: [
      {
        type: "text",
        timing: { start: 0, duration: 3.0 },
        params: { text: "¡Suscríbete!", scale: 1.2 },
      },
      {
        type: "particles",
        timing: { start: 0.1, duration: 1.5 },
        params: { preset: "confetti", count: 60 },
      },
    ],
  },
};

/**
 * Registro de Macros de Movimiento para gráficos avanzados (Fase 11).
 */
export class MotionMacroRegistry {
  private static macros = new Map<string, MotionMacro>(Object.entries(BuiltinMotionMacros));

  public static get(id: string): MotionMacro | undefined {
    return this.macros.get(id);
  }

  public static register(macro: MotionMacro): void {
    this.macros.set(macro.id, macro);
  }

  public static list(): MotionMacro[] {
    return Array.from(this.macros.values());
  }
}
