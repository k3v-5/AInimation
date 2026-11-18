import { ContentModel, EnrichedSegment, HookCandidate } from "../types/index.js";

/**
 * Constructor del modelo de contenido y detector de hooks narrativos (Fase 14).
 */
export class ContentModelBuilder {
  /**
   * Construye el ContentModel enriqueciendo segmentos y detectando candidatos a gancho inicial (*Hook*).
   */
  public static buildContentModel(
    rawSegments: { start: number; end: number; text: string }[],
    primaryTopic = "General"
  ): ContentModel {
    const segments: EnrichedSegment[] = rawSegments.map((raw, idx) => {
      const words = raw.text.split(/\s+/).map((w, wIdx) => {
        const step = (raw.end - raw.start) / Math.max(1, raw.text.split(/\s+/).length);
        return {
          word: w,
          start: Math.round((raw.start + wIdx * step) * 100) / 100,
          end: Math.round((raw.start + (wIdx + 1) * step) * 100) / 100,
        };
      });

      // Cálculo heurístico de importancia
      let importance = 0.5;
      const lower = raw.text.toLowerCase();
      if (lower.includes("error") || lower.includes("secreto") || lower.includes("cambió") || lower.includes("increíble")) {
        importance = 0.95;
      } else if (lower.includes("bueno") || lower.includes("este video") || lower.includes("hola")) {
        importance = 0.25;
      } else if (lower.includes("porque") || lower.includes("entonces") || lower.includes("ejemplo")) {
        importance = 0.75;
      }

      return {
        id: `seg_${idx}`,
        start: raw.start,
        end: raw.end,
        text: raw.text,
        words,
        semanticTags: [primaryTopic.toLowerCase()],
        importance,
      };
    });

    const hooks: HookCandidate[] = [];
    for (const seg of segments) {
      const lower = seg.text.toLowerCase();
      let hookScore = 0;
      let hookType: HookCandidate["type"] = "statement";

      if (lower.includes("?") || lower.startsWith("¿")) {
        hookScore = 0.9;
        hookType = "question";
      } else if (lower.includes("no cometas") || lower.includes("el mayor error") || lower.includes("nunca hagas")) {
        hookScore = 0.95;
        hookType = "curiosity";
      } else if (seg.importance >= 0.8) {
        hookScore = 0.8;
        hookType = "promise";
      }

      if (hookScore > 0) {
        hooks.push({
          start: seg.start,
          end: seg.end,
          score: hookScore,
          type: hookType,
          text: seg.text,
          explanation: `High hook potential detected with pattern '${hookType}' (score: ${hookScore})`,
        });
      }
    }

    hooks.sort((a, b) => b.score - a.score);

    const totalDuration = segments.length > 0 ? segments[segments.length - 1].end : 0;

    return {
      segments,
      hooks,
      totalDuration,
      primaryTopic,
    };
  }
}
