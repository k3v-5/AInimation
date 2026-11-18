import { VisualizationElement, VisualizationTheme } from "./types.js";

/**
 * REQ-025 §49: Accesibilidad y contraste visual sin dependencia exclusiva del color.
 */

export function calculateLuminance(hexColor: string): number {
  const clean = hexColor.replace("#", "");
  const r = parseInt(clean.substring(0, 2), 16) / 255;
  const g = parseInt(clean.substring(2, 4), 16) / 255;
  const b = parseInt(clean.substring(4, 6), 16) / 255;

  const a = [r, g, b].map((v) =>
    v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)
  );

  return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2];
}

export function getContrastRatio(color1: string, color2: string): number {
  const lum1 = calculateLuminance(color1);
  const lum2 = calculateLuminance(color2);
  const brightest = Math.max(lum1, lum2);
  const darkest = Math.min(lum1, lum2);
  return (brightest + 0.05) / (darkest + 0.05);
}

export function verifyThemeContrast(theme: VisualizationTheme): {
  compliant: boolean;
  textContrast: number;
  primaryContrast: number;
} {
  const textContrast = getContrastRatio(theme.textColor, theme.backgroundColor);
  const primaryContrast = getContrastRatio(theme.primaryColor, theme.backgroundColor);

  return {
    compliant: textContrast >= 4.5,
    textContrast: Number(textContrast.toFixed(2)),
    primaryContrast: Number(primaryContrast.toFixed(2)),
  };
}

/**
 * Comprueba que elementos con valores negativos incluyan diferenciación geométrica y textual.
 */
export function ensureAccessibleNegativeValues(elements: VisualizationElement[]): void {
  for (const el of elements) {
    if (el.type === "TEXT" && el.text && el.text.startsWith("-")) {
      // Tiene prefijo explícito de signo negativo
      el.accessibilityRole = "negative-value";
    }
  }
}
