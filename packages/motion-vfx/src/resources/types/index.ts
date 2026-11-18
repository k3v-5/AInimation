import { Time } from "../../core/types.js";

export type PixelFormat = "rgba8" | "bgra8" | "rgb8" | "yuv420p";

/**
 * Representación inmutable y abstracta de un fotograma decodificado (Fase 5A).
 */
export interface Frame {
  width: number;
  height: number;
  format: PixelFormat;
  timestamp: Time;
  data?: unknown;
}

/**
 * Interfaz para proveedores y decodificadores de fotogramas de video o imagen.
 */
export interface FrameProvider {
  getFrame(assetId: string, time: Time): Frame;
}
