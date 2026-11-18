import { EditingCritique, EditingIssue, EditingPlan, EditingSuggestion } from "../types/index.js";

/**
 * Crítico heurístico de calidad y ritmo de planes de edición para IA (Fase 7).
 */
export class AICritic {
  /**
   * Evalúa el ritmo (pacing), variedad visual y presencia de elementos clave en un plan de edición.
   */
  public static critique(plan: EditingPlan): EditingCritique {
    const issues: EditingIssue[] = [];
    const suggestions: EditingSuggestion[] = [];

    // 1. Evaluar Ritmo (Pacing)
    let totalShots = 0;
    let totalShotDuration = 0;

    for (const scene of plan.scenes) {
      for (const shot of scene.shots) {
        totalShots++;
        totalShotDuration += shot.duration;
      }
    }

    const avgShotDuration = totalShots > 0 ? totalShotDuration / totalShots : 0;
    let pacingScore = 8.0;

    if (plan.brief.platform === "tiktok" || plan.brief.platform === "youtube-shorts") {
      if (avgShotDuration > 4.0) {
        pacingScore = 5.0;
        issues.push({
          severity: "warning",
          message: `Average shot duration (${avgShotDuration.toFixed(1)}s) is too slow for ${plan.brief.platform}. Target: < 3.5s.`,
        });
        suggestions.push({
          message: "Split longer shots or insert B-roll cutaways to increase visual pace.",
          action: "shorten_shots",
        });
      }
    }

    // 2. Evaluar Variedad de Encuadres (Visual Variety)
    let varietyScore = 9.0;
    const allFramings: string[] = [];
    for (const scene of plan.scenes) {
      for (const shot of scene.shots) {
        if (shot.framing) allFramings.push(shot.framing);
      }
    }

    let repeatCount = 1;
    for (let i = 1; i < allFramings.length; i++) {
      if (allFramings[i] === allFramings[i - 1]) {
        repeatCount++;
        if (repeatCount >= 3) {
          varietyScore = Math.max(3, varietyScore - 2);
          issues.push({
            severity: "info",
            message: `Framing '${allFramings[i]}' is repeated 3+ times in consecutive shots.`,
          });
          suggestions.push({
            message: "Alternate between wide, medium and close-up framings for visual dynamism.",
            action: "vary_framing",
          });
          break;
        }
      } else {
        repeatCount = 1;
      }
    }

    // 3. Evaluar presencia de CTA
    const hasCTA = plan.sections.some((s) => s.type === "cta");
    if (!hasCTA && plan.brief.targetDuration > 15) {
      issues.push({
        severity: "info",
        message: "No CTA (Call-to-Action) section found in editing plan.",
      });
      suggestions.push({
        message: "Add a final 3-5s CTA section to encourage user conversion / likes / follows.",
        action: "add_cta",
      });
    }

    const overallScore = Math.round(((pacingScore * 0.6 + varietyScore * 0.4) * 10)) / 10;

    return {
      pacingScore,
      varietyScore,
      overallScore,
      issues,
      suggestions,
    };
  }
}
