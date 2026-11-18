/**
 * REQ-025 §41: Utilidades de color, blending y verificación de contraste editorial.
 */

export function validateHexColor(hex: string): boolean {
  if (typeof hex !== "string") return false;
  return /^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$/.test(hex.trim());
}

export function parseHexColor(hex: string): { r: number; g: number; b: number; a: number } {
  const clean = hex.trim().replace(/^#/, "");
  let r = 0;
  let g = 0;
  let b = 0;
  let a = 1;

  if (clean.length === 3) {
    r = parseInt(clean[0] + clean[0], 16);
    g = parseInt(clean[1] + clean[1], 16);
    b = parseInt(clean[2] + clean[2], 16);
  } else if (clean.length === 6) {
    r = parseInt(clean.substring(0, 2), 16);
    g = parseInt(clean.substring(2, 4), 16);
    b = parseInt(clean.substring(4, 6), 16);
  } else if (clean.length === 8) {
    r = parseInt(clean.substring(0, 2), 16);
    g = parseInt(clean.substring(2, 4), 16);
    b = parseInt(clean.substring(4, 6), 16);
    a = Number((parseInt(clean.substring(6, 8), 16) / 255).toFixed(3));
  } else {
    throw new Error(`Color hexadecimal inválido: '${hex}'`);
  }

  return { r, g, b, a };
}

export function blendColors(hexA: string, hexB: string, ratio: number): string {
  const clampedRatio = Math.max(0, Math.min(1, ratio));
  const cA = parseHexColor(hexA);
  const cB = parseHexColor(hexB);

  const r = Math.round(cA.r + clampedRatio * (cB.r - cA.r));
  const g = Math.round(cA.g + clampedRatio * (cB.g - cA.g));
  const b = Math.round(cA.b + clampedRatio * (cB.b - cA.b));

  const toHex = (n: number) => n.toString(16).padStart(2, "0").toUpperCase();
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

export function relativeLuminance(r: number, g: number, b: number): number {
  const sRGB = [r / 255, g / 255, b / 255].map((val) => {
    return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * sRGB[0] + 0.7152 * sRGB[1] + 0.0722 * sRGB[2];
}

export function contrastRatio(hexA: string, hexB: string): number {
  const cA = parseHexColor(hexA);
  const cB = parseHexColor(hexB);

  const lA = relativeLuminance(cA.r, cA.g, cA.b);
  const lB = relativeLuminance(cB.r, cB.g, cB.b);

  const lighter = Math.max(lA, lB);
  const darker = Math.min(lA, lB);

  const ratio = (lighter + 0.05) / (darker + 0.05);
  return Number(ratio.toFixed(2));
}
