import crypto from "crypto";
import { EditorialQAFinding, EditorialSeverity } from "../qa/editorial-qa-finding.js";

export interface StyleBibleConfig {
  bibleId: string;
  name: string;
  version: string;
  typography: {
    primaryFont: string; // ej. "Impact", "Arial Black"
    allowedFonts: string[];
    maxCharactersPerLine: number;
    condensedScaleY: number; // 120% a 150%
  };
  colors: {
    primaryAccentHex: string; // "#FF1424" (TIME Red)
    backgroundHex: string; // "#0F1115"
    textPrimaryHex: string; // "#FFFFFF"
    allowedColorHexes: string[];
  };
  transitions: {
    defaultCutType: "HARD_CUT" | "DISSOLVE" | "J_CUT" | "L_CUT";
    forbiddenTransitionTypes: string[];
    maxDissolveDurationSeconds: number;
  };
  audio: {
    targetLufs: number;
    maxTruePeakDb: number;
    allowDigitalSilence: boolean; // false
  };
}

/**
 * REQ-071: Master Style Bible Engine
 * Define y audita el cumplimiento formal de la gramática visual, tipográfica y cromática del proyecto.
 */
export class StyleBible {
  public readonly config: StyleBibleConfig;
  public readonly canonicalHash: string;

  constructor(config?: Partial<StyleBibleConfig>) {
    this.config = {
      bibleId: config?.bibleId || "sb_time_insignia_v1",
      name: config?.name || "TIME Editorial Style Bible",
      version: config?.version || "1.0.0",
      typography: {
        primaryFont: "Impact",
        allowedFonts: ["Impact", "Arial Black", "Anton"],
        maxCharactersPerLine: 45,
        condensedScaleY: 130,
        ...config?.typography,
      },
      colors: {
        primaryAccentHex: "#FF1424",
        backgroundHex: "#0F1115",
        textPrimaryHex: "#FFFFFF",
        allowedColorHexes: ["#FF1424", "#0F1115", "#FFFFFF", "#1E222D", "#E1E4EA"],
        ...config?.colors,
      },
      transitions: {
        defaultCutType: "HARD_CUT",
        forbiddenTransitionTypes: ["STAR_WIPE", "PAGE_CURL", "BARN_DOOR"],
        maxDissolveDurationSeconds: 1.5,
        ...config?.transitions,
      },
      audio: {
        targetLufs: -16.0,
        maxTruePeakDb: -1.0,
        allowDigitalSilence: false,
        ...config?.audio,
      },
    };

    this.canonicalHash = crypto
      .createHash("sha256")
      .update(JSON.stringify(this.config), "utf8")
      .digest("hex");
  }

  /**
   * Audita una IR o conjunto de nodos para detectar STYLE_VIOLATION
   */
  public auditEditorialStyle(params: {
    usedFonts?: string[];
    usedColors?: string[];
    usedTransitions?: string[];
  }): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];

    // 1. Auditoría Tipográfica
    for (const font of params.usedFonts || []) {
      if (!this.config.typography.allowedFonts.includes(font)) {
        const id = `sb_font_${crypto.createHash("sha256").update(font).digest("hex").slice(0, 8)}`;
        findings.push({
          id,
          ruleId: "STYLE_VIOLATION_FONT",
          severity: "BLOCKING",
          category: "VISUAL",
          title: "Disallowed Font Family Used",
          message: `La fuente '${font}' viola la Style Bible. Permitidas: ${this.config.typography.allowedFonts.join(", ")}.`,
          confidence: 1.0,
          timestampSeconds: 0,
          affectedNodeIds: [font],
          affectedEntityIds: [font],
          evidence: [],
          fingerprint: id,
          autoFixable: false,
          requiresHumanReview: true,
        });
      }
    }

    // 2. Auditoría de Transiciones Prohibidas
    for (const trans of params.usedTransitions || []) {
      if (this.config.transitions.forbiddenTransitionTypes.includes(trans)) {
        const id = `sb_trans_${crypto.createHash("sha256").update(trans).digest("hex").slice(0, 8)}`;
        findings.push({
          id,
          ruleId: "STYLE_VIOLATION_TRANSITION",
          severity: "WARNING",
          category: "STRUCTURAL",
          title: "Forbidden Kitsch Transition",
          message: `La transición '${trans}' está prohibida por la Style Bible institucional.`,
          confidence: 0.95,
          timestampSeconds: 0,
          affectedNodeIds: [trans],
          affectedEntityIds: [trans],
          evidence: [],
          fingerprint: id,
          autoFixable: true,
          requiresHumanReview: false,
        });
      }
    }

    return findings;
  }
}
