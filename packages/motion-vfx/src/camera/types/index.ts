import { Time } from "../../core/types.js";

export interface Vec3 {
  x: number;
  y: number;
  z: number;
}

export interface Camera {
  position: Vec3;
  rotation: Vec3; // Roll (z), Pitch (x), Yaw (y) en grados
  zoom: number; // Factor de zoom (1.0 = normal, 1.2 = 20% zoom-in)
  focalLength?: number;
}

export interface CameraModifier {
  evaluate(time: Time, camera: Camera): Camera;
}

export interface CameraPreset {
  id: string;
  name: string;
  description: string;
  initialCamera: Camera;
  modifier?: CameraModifier;
}
