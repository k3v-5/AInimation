import { SafeZoneConfig, BarGeometry } from "./types.js";
import { SafeZoneViolationError } from "./errors.js";

/**
 * REQ-025 §8, §14, §42: Motor de Layout y Geometría de Visualizaciones.
 */

export interface SafeAreaRect {
  left: number;
  top: number;
  right: number;
  bottom: number;
  width: number;
  height: number;
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export function resolveSafeArea(
  canvasWidth: number,
  canvasHeight: number,
  safeZone: SafeZoneConfig
): SafeAreaRect {
  let left = safeZone.left;
  let top = safeZone.top;
  let right = safeZone.right;
  let bottom = safeZone.bottom;

  if (safeZone.unit === "PERCENT") {
    left = (canvasWidth * safeZone.left) / 100;
    right = (canvasWidth * safeZone.right) / 100;
    top = (canvasHeight * safeZone.top) / 100;
    bottom = (canvasHeight * safeZone.bottom) / 100;
  }

  const width = canvasWidth - (left + right);
  const height = canvasHeight - (top + bottom);

  if (width <= 0 || height <= 0) {
    throw new SafeZoneViolationError(
      `Safe Zone imposible: ancho útil (${width}px) o alto útil (${height}px) no es positivo para canvas ${canvasWidth}x${canvasHeight}.`
    );
  }

  return {
    left: Number(left.toFixed(2)),
    top: Number(top.toFixed(2)),
    right: Number((canvasWidth - right).toFixed(2)),
    bottom: Number((canvasHeight - bottom).toFixed(2)),
    width: Number(width.toFixed(2)),
    height: Number(height.toFixed(2)),
  };
}

export function isWithinSafeZone(bounds: BoundingBox, safeArea: SafeAreaRect): boolean {
  return (
    bounds.x >= safeArea.left - 1e-4 &&
    bounds.y >= safeArea.top - 1e-4 &&
    bounds.x + bounds.width <= safeArea.right + 1e-4 &&
    bounds.y + bounds.height <= safeArea.bottom + 1e-4
  );
}

export function computeBarLayout(params: {
  canvasWidth: number;
  canvasHeight: number;
  safeZone: SafeZoneConfig;
  bars: Array<{ id: string; category: string; value: number; normalizedValue: number }>;
  orientation: "VERTICAL" | "HORIZONTAL";
  gapRatio?: number; // e.g. 0.25 (25% gap)
}): BarGeometry[] {
  const safeArea = resolveSafeArea(params.canvasWidth, params.canvasHeight, params.safeZone);
  const barCount = params.bars.length;
  if (barCount === 0) return [];

  const gapRatio = params.gapRatio ?? 0.25;
  const geometries: BarGeometry[] = [];

  if (params.orientation === "VERTICAL") {
    const totalSlots = barCount + (barCount - 1) * gapRatio;
    const barWidth = safeArea.width / totalSlots;
    const gap = barWidth * gapRatio;
    const maxBarHeight = safeArea.height * 0.85; // Deja margen para labels y valores

    for (let i = 0; i < barCount; i++) {
      const b = params.bars[i];
      const x = safeArea.left + i * (barWidth + gap);
      const height = Math.max(2, b.normalizedValue * maxBarHeight);
      const y = safeArea.bottom - height;

      geometries.push({
        id: b.id,
        category: b.category,
        value: b.value,
        x: Number(x.toFixed(2)),
        y: Number(y.toFixed(2)),
        width: Number(barWidth.toFixed(2)),
        height: Number(height.toFixed(2)),
        normalizedValue: b.normalizedValue,
      });
    }
  } else {
    // HORIZONTAL
    const totalSlots = barCount + (barCount - 1) * gapRatio;
    const barHeight = safeArea.height / totalSlots;
    const gap = barHeight * gapRatio;
    const maxBarWidth = safeArea.width * 0.75; // Margen para títulos/valores

    for (let i = 0; i < barCount; i++) {
      const b = params.bars[i];
      const y = safeArea.top + i * (barHeight + gap);
      const width = Math.max(2, b.normalizedValue * maxBarWidth);
      const x = safeArea.left + safeArea.width * 0.20; // 20% para labels de categoría

      geometries.push({
        id: b.id,
        category: b.category,
        value: b.value,
        x: Number(x.toFixed(2)),
        y: Number(y.toFixed(2)),
        width: Number(width.toFixed(2)),
        height: Number(barHeight.toFixed(2)),
        normalizedValue: b.normalizedValue,
      });
    }
  }

  return geometries;
}
