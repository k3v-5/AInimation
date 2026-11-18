export type HookStrategy = "controversial_question" | "visual_punch" | "stat_drop" | "curiosity_gap";
export type SegmentPurpose = "hook" | "setup" | "build_up" | "climax_drop" | "resolution_cta";

export interface NarrativeSegment {
  id: string;
  purpose: SegmentPurpose;
  startTime: number;
  endTime: number;
  duration: number;
  energyLevel: number; // [1, 10]
  brollDensity: "low" | "medium" | "high";
  suggestedTransition: "cut" | "whip" | "zoom" | "flash";
  captionEmphasis: boolean;
}

export interface CreativeNarrativePlan {
  title: string;
  hookStrategy: HookStrategy;
  totalDuration: number;
  segments: NarrativeSegment[];
  pacingCurve: Array<{ time: number; energy: number }>;
}

/**
 * Planificador Creativo y Director Narrativo Audiovisual (Autonomous MCP v2 / REQ-035).
 * Estructura la narrativa en bloques editoriales con propósito (Hook -> Setup -> Build-Up -> Climax -> CTA).
 */
export class CreativePlanner {
  /**
   * Genera el plan narrativo estructurado a partir del brief y la duración deseada.
   */
  public static createNarrativePlan(
    title: string,
    totalDuration = 45.0,
    strategy: HookStrategy = "controversial_question"
  ): CreativeNarrativePlan {
    const hookDur = Math.min(3.0, Number((totalDuration * 0.08).toFixed(2)));
    const setupDur = Number((totalDuration * 0.22).toFixed(2));
    const buildUpDur = Number((totalDuration * 0.30).toFixed(2));
    const climaxDur = Number((totalDuration * 0.28).toFixed(2));
    const ctaDur = Number((totalDuration - (hookDur + setupDur + buildUpDur + climaxDur)).toFixed(2));

    let t = 0.0;
    const segments: NarrativeSegment[] = [];

    // 1. Hook
    segments.push({
      id: "seg_hook",
      purpose: "hook",
      startTime: t,
      endTime: Number((t + hookDur).toFixed(2)),
      duration: hookDur,
      energyLevel: 9,
      brollDensity: "high",
      suggestedTransition: "whip",
      captionEmphasis: true,
    });
    t += hookDur;

    // 2. Setup
    segments.push({
      id: "seg_setup",
      purpose: "setup",
      startTime: t,
      endTime: Number((t + setupDur).toFixed(2)),
      duration: setupDur,
      energyLevel: 5,
      brollDensity: "medium",
      suggestedTransition: "cut",
      captionEmphasis: false,
    });
    t += setupDur;

    // 3. Build-Up
    segments.push({
      id: "seg_buildup",
      purpose: "build_up",
      startTime: t,
      endTime: Number((t + buildUpDur).toFixed(2)),
      duration: buildUpDur,
      energyLevel: 8,
      brollDensity: "high",
      suggestedTransition: "zoom",
      captionEmphasis: true,
    });
    t += buildUpDur;

    // 4. Climax Drop
    segments.push({
      id: "seg_climax",
      purpose: "climax_drop",
      startTime: t,
      endTime: Number((t + climaxDur).toFixed(2)),
      duration: climaxDur,
      energyLevel: 10,
      brollDensity: "high",
      suggestedTransition: "flash",
      captionEmphasis: true,
    });
    t += climaxDur;

    // 5. CTA
    segments.push({
      id: "seg_cta",
      purpose: "resolution_cta",
      startTime: t,
      endTime: totalDuration,
      duration: Math.max(1.0, ctaDur),
      energyLevel: 6,
      brollDensity: "low",
      suggestedTransition: "cut",
      captionEmphasis: true,
    });

    const pacingCurve = segments.map((s) => ({
      time: s.startTime,
      energy: s.energyLevel,
    }));

    return {
      title,
      hookStrategy: strategy,
      totalDuration,
      segments,
      pacingCurve,
    };
  }
}
