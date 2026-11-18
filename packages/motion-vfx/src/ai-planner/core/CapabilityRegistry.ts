import { ValidationError } from "../../errors/index.js";
import { EngineCapability } from "../types/index.js";

/**
 * Registro y catálogo de capacidades del motor audiovisual para la IA (Fase 7).
 */
export class CapabilityRegistry {
  private static capabilities = new Map<string, EngineCapability>();

  public static register(capability: EngineCapability): void {
    if (!capability || !capability.id) {
      throw new ValidationError("Capability requires a valid 'id'.");
    }
    if (this.capabilities.has(capability.id)) {
      throw new ValidationError(`DUPLICATE_CAPABILITY: '${capability.id}' is already registered.`);
    }
    this.capabilities.set(capability.id, capability);
  }

  public static get(id: string): EngineCapability | undefined {
    return this.capabilities.get(id);
  }

  public static has(id: string): boolean {
    return this.capabilities.has(id);
  }

  public static list(): EngineCapability[] {
    return Array.from(this.capabilities.values());
  }

  public static clear(): void {
    this.capabilities.clear();
  }
}

export const BuiltinCapabilities: EngineCapability[] = [
  {
    id: "graphics.callout",
    category: "graphics",
    description: "Draws an animated callout with pointer arrow pointing to a subject.",
    parameters: { text: "string", target: "Vec2 | string" },
  },
  {
    id: "graphics.progress-bar",
    category: "graphics",
    description: "Renders an animated progress bar indicating time or metric progress.",
    parameters: { value: "number", min: "number", max: "number" },
  },
  {
    id: "camera.push-in",
    category: "camera",
    description: "Performs a punch-in or slow push-in zoom camera effect.",
    parameters: { zoomFactor: "number", duration: "number" },
  },
  {
    id: "caption.word-pop",
    category: "caption",
    description: "Viral kinetic caption style scaling up each word as spoken.",
    parameters: { scaleMultiplier: "number" },
  },
  {
    id: "audio.ducking",
    category: "audio",
    description: "Automatically attenuates background music when voice is active.",
    parameters: { attenuationDb: "number", attackMs: "number", releaseMs: "number" },
  },
  {
    id: "tracking.object",
    category: "tracking",
    description: "Binds graphic element or camera focus to a tracked object bounding box.",
    parameters: { targetLabel: "string" },
  },
];

for (const cap of BuiltinCapabilities) {
  if (!CapabilityRegistry.has(cap.id)) {
    CapabilityRegistry.register(cap);
  }
}
