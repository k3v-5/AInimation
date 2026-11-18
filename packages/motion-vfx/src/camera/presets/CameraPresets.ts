import { ValidationError } from "../../errors/index.js";
import { CameraModifier, CameraPreset } from "../types/index.js";
import { CameraShakeModifier, PunchInModifier } from "../modifiers/CameraModifiers.js";

/**
 * Registro de presets de cámara cinemática para IA (Fase 5H).
 */
export class CameraPresetRegistry {
  private static presets = new Map<string, CameraPreset>();

  public static register(preset: CameraPreset): void {
    if (!preset || !preset.id) {
      throw new ValidationError("Camera preset requires a valid 'id'.");
    }
    if (this.presets.has(preset.id)) {
      throw new ValidationError(`DUPLICATE_CAMERA_PRESET: Preset '${preset.id}' already exists.`);
    }
    this.presets.set(preset.id, preset);
  }

  public static get(id: string): CameraPreset {
    const p = this.presets.get(id);
    if (!p) {
      throw new ValidationError(`CAMERA_PRESET_NOT_FOUND: Camera preset '${id}' is not registered.`);
    }
    return p;
  }

  public static has(id: string): boolean {
    return this.presets.has(id);
  }

  public static list(): CameraPreset[] {
    return Array.from(this.presets.values());
  }

  public static clear(): void {
    this.presets.clear();
  }
}

export const BuiltinCameraPresets: CameraPreset[] = [
  {
    id: "handheld-shake",
    name: "Handheld Camera Shake",
    description: "Natural organic camera shake simulating handheld footage.",
    initialCamera: {
      position: { x: 0, y: 0, z: 0 },
      rotation: { x: 0, y: 0, z: 0 },
      zoom: 1.05, // Ligero zoom de compensación de bordes
    },
    modifier: new CameraShakeModifier(12.0, 3.5, 42),
  },
  {
    id: "punch-in",
    name: "Dramatic Punch-In",
    description: "Fast zoom punch-in to emphasize important speech moments.",
    initialCamera: {
      position: { x: 0, y: 0, z: 0 },
      rotation: { x: 0, y: 0, z: 0 },
      zoom: 1.0,
    },
    modifier: new PunchInModifier(1.3, 0.25),
  },
];

for (const p of BuiltinCameraPresets) {
  if (!CameraPresetRegistry.has(p.id)) {
    CameraPresetRegistry.register(p);
  }
}
