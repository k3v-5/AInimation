export interface CoverCandidateFrame {
  clipId: string;
  timestamp: number;
  aestheticScore: number; // [0, 100]
  hasLightingContrast: boolean;
  subjectCentered: boolean;
}

export interface HookCoverDesign {
  title: string;
  subtitle?: string;
  badge?: string;
  heroTimestamp: number;
  primaryColor?: [number, number, number];
  glowColor?: [number, number, number];
}

/**
 * Generador automático de portadas, miniaturas y ganchos visuales virales (Fase 10 / Mejoras).
 * Analiza fotogramas candidatos, selecciona el momento de mayor impacto cinemático y
 * genera una composición de portada 9:16 con tipografía 3D, resplandor óptico y badges editoriales.
 */
export class AIHookCoverGenerator {
  /**
   * Selecciona el mejor fotograma candidato calculando un score ponderado de impacto visual.
   */
  public static selectHeroFrame(candidates: CoverCandidateFrame[]): CoverCandidateFrame {
    if (candidates.length === 0) {
      return {
        clipId: "default_hero",
        timestamp: 0.0,
        aestheticScore: 75.0,
        hasLightingContrast: true,
        subjectCentered: true,
      };
    }

    let best = candidates[0];
    let maxScore = -1;

    for (const c of candidates) {
      let score = c.aestheticScore;
      if (c.hasLightingContrast) score += 15;
      if (c.subjectCentered) score += 10;

      if (score > maxScore) {
        maxScore = score;
        best = c;
      }
    }

    return best;
  }

  /**
   * Genera el fragmento ExtendScript para construir la portada en 9:16 en After Effects.
   */
  public static generateHookCoverComp(
    projectVar: string,
    compName: string,
    heroFootageVar: string,
    design: HookCoverDesign
  ): string {
    const mainCol = design.primaryColor ?? [1.0, 0.08, 0.14]; // Crimson
    const glowCol = design.glowColor ?? [1.0, 0.78, 0.10]; // Gold
    const badge = design.badge ?? "GUADALAJARA // 2023";

    return [
      `// === VIRAL HOOK COVER COMPOSITION (9:16) ===`,
      `var coverComp = ${projectVar}.items.addComp("${compName}", 1080, 1920, 1.0, 5.0, 60);`,
      `coverComp.bgColor = [0.03, 0.03, 0.04];`,
      `// 1. Capa de Video de Fondo Congelada en el Momento Hero`,
      `var bgLayer = coverComp.layers.add(${heroFootageVar});`,
      `bgLayer.name = "Hero_Background";`,
      `bgLayer.timeRemapEnabled = true;`,
      `bgLayer.timeRemap.setValueAtTime(0, ${design.heroTimestamp});`,
      `var coverScale = Math.max((1080 / ${heroFootageVar}.width) * 100, (1920 / ${heroFootageVar}.height) * 100) * 1.05;`,
      `bgLayer.transform.scale.setValue([coverScale, coverScale]);`,
      `bgLayer.transform.position.setValue([540, 960]);`,
      `// 2. Badge Editorial Superior`,
      `var badgeLayer = coverComp.layers.addText("${badge}");`,
      `badgeLayer.name = "Cover_Badge";`,
      `var bDoc = badgeLayer.property("Source Text").value;`,
      `bDoc.fontSize = 24;`,
      `bDoc.fillColor = [${glowCol[0]}, ${glowCol[1]}, ${glowCol[2]}];`,
      `bDoc.tracking = 25;`,
      `badgeLayer.property("Source Text").setValue(bDoc);`,
      `badgeLayer.transform.position.setValue([540, 420]);`,
      `// 3. Título 3D Gigante`,
      `var titleLayer = coverComp.layers.addText("${design.title}");`,
      `titleLayer.name = "Cover_Title_Main";`,
      `var tDoc = titleLayer.property("Source Text").value;`,
      `tDoc.fontSize = 175;`,
      `tDoc.fillColor = [${mainCol[0]}, ${mainCol[1]}, ${mainCol[2]}];`,
      `tDoc.justification = ParagraphJustification.CENTER_JUSTIFY;`,
      `tDoc.tracking = -15;`,
      `try { tDoc.font = "Impact"; } catch(e) {}`,
      `titleLayer.property("Source Text").setValue(tDoc);`,
      `titleLayer.transform.position.setValue([540, 680]);`,
      `// 4. Resplandor Óptico (Glow)`,
      `try {`,
      `  var glow = titleLayer.property("Effects").addProperty("ADBE Glo2");`,
      `  if (glow) { glow.property("Glow Radius").setValue(45); glow.property("Glow Intensity").setValue(1.8); }`,
      `} catch(ge) {}`,
      `coverComp.openInViewer();`,
    ].join("\n");
  }
}
