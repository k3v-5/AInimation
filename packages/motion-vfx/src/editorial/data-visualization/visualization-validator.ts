import { VisualizationIR, BaseVisualizationSpec } from "./types.js";
import { DataVisualizationError } from "./errors.js";
import { resolveSafeArea, isWithinSafeZone } from "./layout-engine.js";

/**
 * REQ-025 §42, §46, §78: Validador de invariantes de VisualizationIR.
 */

export function validateVisualizationIR(
  ir: VisualizationIR,
  spec?: BaseVisualizationSpec
): DataVisualizationError[] {
  const errors: DataVisualizationError[] = [];

  if (ir.width <= 0 || !Number.isFinite(ir.width)) {
    errors.push({
      code: "CANVAS_WIDTH_INVALID",
      message: `Ancho de canvas no positivo o no finito: ${ir.width}`,
      severity: "BLOCKING",
      field: "width",
    });
  }

  if (ir.height <= 0 || !Number.isFinite(ir.height)) {
    errors.push({
      code: "CANVAS_HEIGHT_INVALID",
      message: `Alto de canvas no positivo o no finito: ${ir.height}`,
      severity: "BLOCKING",
      field: "height",
    });
  }

  if (ir.durationSeconds <= 0 || !Number.isFinite(ir.durationSeconds)) {
    errors.push({
      code: "DURATION_NOT_POSITIVE",
      message: `Duración no positiva o no finita: ${ir.durationSeconds}`,
      severity: "BLOCKING",
      field: "durationSeconds",
    });
  }

  if (spec) {
    const totalAnim =
      spec.animation.entranceDurationSeconds + spec.animation.exitDurationSeconds;
    if (totalAnim > spec.durationSeconds + 1e-4) {
      errors.push({
        code: "ANIMATION_DURATION_EXCEEDED",
        message: `La suma de entrada (${spec.animation.entranceDurationSeconds}s) y salida (${spec.animation.exitDurationSeconds}s) excede la duración total (${spec.durationSeconds}s).`,
        severity: "BLOCKING",
      });
    }
  }

  // Safe zone check si spec está presente
  let safeArea: any = null;
  if (spec?.safeZone) {
    try {
      safeArea = resolveSafeArea(ir.width, ir.height, spec.safeZone);
    } catch (err: any) {
      errors.push({
        code: "SAFE_ZONE_RESOLUTION_FAILED",
        message: err.message,
        severity: "BLOCKING",
      });
    }
  }

  for (let l = 0; l < ir.layers.length; l++) {
    const layer = ir.layers[l];

    if (layer.opacity < 0 || layer.opacity > 1 || !Number.isFinite(layer.opacity)) {
      errors.push({
        code: "OPACITY_OUT_OF_BOUNDS",
        message: `Opacidad fuera del rango [0, 1] en capa '${layer.id}': ${layer.opacity}`,
        severity: "BLOCKING",
        field: "opacity",
      });
    }

    const { position, scale, rotation } = layer.transform;
    if (!Number.isFinite(position.x) || !Number.isFinite(position.y)) {
      errors.push({
        code: "COORDINATES_NOT_FINITE",
        message: `Posición no finita en capa '${layer.id}': (${position.x}, ${position.y})`,
        severity: "BLOCKING",
        field: "transform.position",
      });
    }

    if (scale.x < 0 || scale.y < 0 || !Number.isFinite(scale.x) || !Number.isFinite(scale.y)) {
      errors.push({
        code: "SCALE_INVALID",
        message: `Escala negativa o no finita en capa '${layer.id}': (${scale.x}, ${scale.y})`,
        severity: "BLOCKING",
        field: "transform.scale",
      });
    }

    if (!Number.isFinite(rotation)) {
      errors.push({
        code: "ROTATION_NOT_FINITE",
        message: `Rotación no finita en capa '${layer.id}': ${rotation}`,
        severity: "BLOCKING",
        field: "transform.rotation",
      });
    }

    // Keyframes
    if (layer.animation?.properties) {
      for (const prop of layer.animation.properties) {
        let prevTime = -1;
        for (const kf of prop.keyframes) {
          if (kf.timeSeconds < 0 || kf.timeSeconds > ir.durationSeconds + 1e-4) {
            errors.push({
              code: "KEYFRAME_TIME_OUT_OF_BOUNDS",
              message: `Keyframe en tiempo t=${kf.timeSeconds}s fuera del rango [0, ${ir.durationSeconds}] en capa '${layer.id}'.`,
              severity: "BLOCKING",
            });
          }
          if (kf.timeSeconds < prevTime) {
            errors.push({
              code: "KEYFRAME_TIME_NON_MONOTONIC",
              message: `Keyframes no monótonos en propiedad '${prop.property}' de capa '${layer.id}'.`,
              severity: "BLOCKING",
            });
          }
          prevTime = kf.timeSeconds;
        }
      }
    }
  }

  return errors;
}
