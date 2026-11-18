import { DEFAULT_EDITORIAL_COLORS } from "./constants.js";
import { DataVizIssue } from "./errors.js";
import { DataVizStyleProfile } from "./types.js";

export class ColorResolver {
  public static resolveColors(overrides?: Partial<DataVizStyleProfile>): {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    text: string;
    muted: string;
    positive: string;
    negative: string;
  } {
    return {
      primary: overrides?.primaryColor ?? DEFAULT_EDITORIAL_COLORS.primary,
      secondary: DEFAULT_EDITORIAL_COLORS.secondary,
      accent: overrides?.accentColor ?? DEFAULT_EDITORIAL_COLORS.accent,
      background: overrides?.backgroundColor ?? DEFAULT_EDITORIAL_COLORS.background,
      text: overrides?.textColor ?? DEFAULT_EDITORIAL_COLORS.text,
      muted: overrides?.mutedColor ?? DEFAULT_EDITORIAL_COLORS.muted,
      positive: overrides?.positiveColor ?? DEFAULT_EDITORIAL_COLORS.positive,
      negative: overrides?.negativeColor ?? DEFAULT_EDITORIAL_COLORS.negative,
    };
  }

  /**
   * REQ-025 §43: Calculate relative luminance and contrast ratio (WCAG 2.1).
   */
  public static calculateContrastRatio(hex1: string, hex2: string): number {
    const l1 = this.getRelativeLuminance(hex1);
    const l2 = this.getRelativeLuminance(hex2);
    const lighter = Math.max(l1, l2);
    const darker = Math.min(l1, l2);
    return Number(((lighter + 0.05) / (darker + 0.05)).toFixed(2));
  }

  public static checkContrast(foreground: string, background: string, path = "style"): DataVizIssue | undefined {
    const ratio = this.calculateContrastRatio(foreground, background);
    if (ratio < 3.0) {
      return {
        code: "LOW_COLOR_CONTRAST",
        path,
        message: `Color contrast ratio between ${foreground} and ${background} is ${ratio} (minimum recommended 3.0:1)`,
        severity: ratio < 2.0 ? "BLOCKING" : "WARNING",
      };
    }
    return undefined;
  }

  private static parseHex(hex: string): [number, number, number] {
    let clean = hex.replace("#", "").trim();
    if (clean.length === 3) {
      clean = clean[0] + clean[0] + clean[1] + clean[1] + clean[2] + clean[2];
    }
    const num = parseInt(clean, 16);
    return [(num >> 16) & 255, (num >> 8) & 255, num & 255];
  }

  private static getRelativeLuminance(hex: string): number {
    const [r, g, b] = this.parseHex(hex).map((c) => {
      const s = c / 255.0;
      return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }
}
