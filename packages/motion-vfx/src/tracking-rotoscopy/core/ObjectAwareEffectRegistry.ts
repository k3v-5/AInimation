import { ObjectEffectConfig } from "../types/index.js";

export const BuiltinObjectEffects: Record<string, ObjectEffectConfig> = {
  "background-blur": {
    id: "background-blur",
    type: "background-blur",
    targetClass: "person",
    parameters: { blurRadius: 25, feather: 10, keepSubjectSharp: true },
  },
  "object-blur": {
    id: "object-blur",
    type: "object-blur",
    targetClass: "license_plate",
    parameters: { blurRadius: 20, feather: 5 },
  },
  "subject-pop": {
    id: "subject-pop",
    type: "subject-pop",
    targetClass: "person",
    parameters: {
      outlineColor: "#ffeb3b",
      outlineWidth: 4,
      glow: true,
      scaleBoost: 1.05,
      backgroundDim: 0.3,
    },
  },
  "highlight-outline": {
    id: "highlight-outline",
    type: "highlight-outline",
    targetClass: "object",
    parameters: { outlineColor: "#00e5ff", outlineWidth: 3, glow: true },
  },
};

/**
 * Registro de efectos inteligentes basados en objetos y segmentación (Fase 12).
 */
export class ObjectAwareEffectRegistry {
  private static effects = new Map<string, ObjectEffectConfig>(
    Object.entries(BuiltinObjectEffects)
  );

  public static get(id: string): ObjectEffectConfig | undefined {
    return this.effects.get(id);
  }

  public static register(effect: ObjectEffectConfig): void {
    this.effects.set(effect.id, effect);
  }

  public static list(): ObjectEffectConfig[] {
    return Array.from(this.effects.values());
  }
}
