/**
 * REQ-025 §21 & §22: Mapeo de color determinista alineado a TIME Editorial Style.
 */

export const TIME_COLOR_PALETTE = {
  accentRed: "#FF1424",
  backgroundDark: "#0A0A0A",
  textPrimary: "#FFFFFF",
  textSecondary: "#A0A0A0",
  textMuted: "#666666",
  gridLine: "#262626",
  axisLine: "#404040",
  positiveBar: "#FF1424",
  negativeBar: "#8CD1BC", // Contraste editorial suave para negativos
  series: [
    "#FF1424", // Rojo Editorial
    "#FFFFFF", // Blanco Puro
    "#8CD1BC", // Mint Pastel
    "#E5A93C", // Ámbar / Oro
    "#4A90E2", // Azul Cyan
    "#D65A31", // Naranja Quemado
    "#9B51E0", // Púrpura Editorial
  ],
};

export function getColorForSeries(index: number, editorialProfile?: string): string {
  const palette = TIME_COLOR_PALETTE.series;
  const safeIndex = Math.abs(index) % palette.length;
  return palette[safeIndex];
}

export function parseHexColor(hex: string): { r: number; g: number; b: number } {
  let clean = hex.replace("#", "").trim();
  if (clean.length === 3) {
    clean = clean.split("").map((c) => c + c).join("");
  }
  const num = parseInt(clean, 16);
  return {
    r: (num >> 16) & 255,
    g: (num >> 8) & 255,
    b: num & 255,
  };
}

export function getRelativeLuminance(hex: string): number {
  const { r, g, b } = parseHexColor(hex);
  const [rs, gs, bs] = [r / 255, g / 255, b / 255].map((c) =>
    c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
  );
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

export function getContrastRatio(hex1: string, hex2: string): number {
  const l1 = getRelativeLuminance(hex1);
  const l2 = getRelativeLuminance(hex2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  const ratio = (lighter + 0.05) / (darker + 0.05);
  return Math.round(ratio * 100) / 100;
}
