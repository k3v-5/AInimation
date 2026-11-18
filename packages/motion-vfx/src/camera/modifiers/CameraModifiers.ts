import { Time } from "../../core/types.js";
import { Camera, CameraModifier } from "../types/index.js";

/**
 * Modificador procedural de vibración y cámara en mano (Handheld Shake) determinista (Fase 5H).
 */
export class CameraShakeModifier implements CameraModifier {
  constructor(
    public amplitude = 15.0, // Desplazamiento máximo en px
    public frequency = 4.0, // Frecuencia de vibración en Hz
    public seed = 42
  ) {}

  public evaluate(time: Time, camera: Camera): Camera {
    // Generador determinista armónico multifrecuencia
    const s1 = Math.sin(time * this.frequency * 2 * Math.PI + this.seed);
    const s2 = Math.sin(time * this.frequency * 1.414 * Math.PI + this.seed * 2);
    const s3 = Math.cos(time * this.frequency * 0.707 * Math.PI + this.seed * 3);

    const offsetX = (s1 + s2 * 0.5) * (this.amplitude * 0.6);
    const offsetY = (s2 + s3 * 0.5) * (this.amplitude * 0.6);
    const rotZ = s3 * (this.amplitude * 0.05);

    return {
      position: {
        x: camera.position.x + offsetX,
        y: camera.position.y + offsetY,
        z: camera.position.z,
      },
      rotation: {
        x: camera.rotation.x,
        y: camera.rotation.y,
        z: camera.rotation.z + rotZ,
      },
      zoom: camera.zoom,
      focalLength: camera.focalLength,
    };
  }
}

/**
 * Modificador de punch-in zoom dinámico.
 */
export class PunchInModifier implements CameraModifier {
  constructor(
    public targetZoom = 1.25,
    public duration = 0.3
  ) {}

  public evaluate(time: Time, camera: Camera): Camera {
    const progress = Math.min(1.0, time / this.duration);
    const currentZoom = camera.zoom + (this.targetZoom - camera.zoom) * progress;

    return {
      ...camera,
      zoom: currentZoom,
    };
  }
}
