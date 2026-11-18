/**
 * REQ-025 §23 & §24: Motor de layout y safe zones deterministas multiformato.
 */

export interface CanvasDimensions {
  width: number;
  height: number;
  aspectRatio: "16:9" | "9:16" | "1:1";
}

export interface SafeZoneBox {
  left: number;
  top: number;
  right: number;
  bottom: number;
  width: number;
  height: number;
}

export interface PlotArea {
  x: number;
  y: number;
  width: number;
  height: number;
  left: number;
  right: number;
  top: number;
  bottom: number;
}

export function resolveCanvasDimensions(
  width = 1920,
  height = 1080
): CanvasDimensions {
  let aspectRatio: "16:9" | "9:16" | "1:1" = "16:9";
  if (width === 1080 && height === 1920) {
    aspectRatio = "9:16";
  } else if (width === height) {
    aspectRatio = "1:1";
  }
  return { width, height, aspectRatio };
}

export function computeSafeZone(dims: CanvasDimensions): SafeZoneBox {
  let marginX = dims.width * 0.1;
  let marginY = dims.height * 0.12;

  // En 9:16 aumentamos márgenes para evitar botones e interfaz de TikTok/Shorts
  if (dims.aspectRatio === "9:16") {
    marginX = dims.width * 0.08;
    marginY = dims.height * 0.15;
  }

  const left = Math.round(marginX);
  const top = Math.round(marginY);
  const right = Math.round(dims.width - marginX);
  const bottom = Math.round(dims.height - marginY);

  return {
    left,
    top,
    right,
    bottom,
    width: right - left,
    height: bottom - top,
  };
}

export function computePlotArea(
  safeZone: SafeZoneBox,
  hasTitle = true,
  hasSource = true
): PlotArea {
  const titleHeight = hasTitle ? Math.round(safeZone.height * 0.14) : 0;
  const sourceHeight = hasSource ? Math.round(safeZone.height * 0.08) : 0;

  const y = safeZone.top + titleHeight;
  const height = safeZone.height - titleHeight - sourceHeight;

  return {
    x: safeZone.left,
    y,
    width: safeZone.width,
    height,
    left: safeZone.left,
    right: safeZone.right,
    top: y,
    bottom: y + height,
  };
}

export function isWithinSafeZone(
  x: number,
  y: number,
  width: number,
  height: number,
  safeZone: SafeZoneBox
): boolean {
  return (
    x >= safeZone.left &&
    x + width <= safeZone.right &&
    y >= safeZone.top &&
    y + height <= safeZone.bottom
  );
}
