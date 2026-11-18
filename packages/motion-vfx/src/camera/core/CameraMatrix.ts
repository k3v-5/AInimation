import { Matrix2D } from "../../transform/Matrix2D.js";
import { Camera } from "../types/index.js";

/**
 * Calculador de matrices de vista y proyección de cámara 2D / 2.5D (Fase 5H).
 */
export class CameraMatrix {
  /**
   * Genera la matriz de transformación de cámara 2D hacia coordenadas de pantalla.
   */
  public static calculateViewMatrix(
    camera: Camera,
    screenWidth: number,
    screenHeight: number
  ): Matrix2D {
    const cx = screenWidth / 2;
    const cy = screenHeight / 2;

    // 1. Trasladar al centro de pantalla
    let mat = Matrix2D.translation(cx, cy);

    // 2. Aplicar zoom y rotación de roll
    mat = Matrix2D.multiply(mat, Matrix2D.scale(camera.zoom, camera.zoom));
    mat = Matrix2D.multiply(mat, Matrix2D.rotation(camera.rotation.z));

    // 3. Trasladar la posición inversa de la cámara y restaurar pivote central
    mat = Matrix2D.multiply(
      mat,
      Matrix2D.translation(-camera.position.x - cx, -camera.position.y - cy)
    );

    return mat;
  }

  /**
   * Proyecta un punto en el espacio de mundo a coordenadas de pantalla de cámara.
   */
  public static projectPoint(
    point: { x: number; y: number },
    camera: Camera,
    screenWidth: number,
    screenHeight: number
  ): { x: number; y: number } {
    const viewMatrix = this.calculateViewMatrix(camera, screenWidth, screenHeight);
    return Matrix2D.transformPoint(viewMatrix, point);
  }
}
