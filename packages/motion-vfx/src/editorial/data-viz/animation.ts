import { AnimationInstruction, AnimationPlan, AnimationProperty } from "./types.js";

/**
 * REQ-025 §13: Plan de animación determinista.
 */

export class AnimationPlanBuilder {
  private instructions: AnimationInstruction[] = [];

  public add(instruction: {
    targetId: string;
    property: AnimationProperty;
    from: number;
    to: number;
    startSeconds: number;
    endSeconds: number;
    easing?: string;
  }): this {
    this.instructions.push({
      targetId: instruction.targetId,
      property: instruction.property,
      from: Math.round(instruction.from * 10000) / 10000,
      to: Math.round(instruction.to * 10000) / 10000,
      startSeconds: Math.round(instruction.startSeconds * 1000) / 1000,
      endSeconds: Math.round(instruction.endSeconds * 1000) / 1000,
      easing: instruction.easing ?? "easeOutCubic",
    });
    return this;
  }

  public addStaggeredEntrance(
    targetIds: string[],
    property: AnimationProperty,
    from: number,
    to: number,
    baseStartSec: number,
    durationSec: number,
    staggerSec = 0.08,
    easing = "easeOutCubic"
  ): this {
    for (let i = 0; i < targetIds.length; i++) {
      const start = baseStartSec + i * staggerSec;
      this.add({
        targetId: targetIds[i],
        property,
        from,
        to,
        startSeconds: start,
        endSeconds: start + durationSec,
        easing,
      });
    }
    return this;
  }

  public build(): AnimationPlan {
    // Ordenar instrucciones de forma determinista: por startSeconds y luego targetId
    const sorted = [...this.instructions].sort((a, b) => {
      if (a.startSeconds !== b.startSeconds) return a.startSeconds - b.startSeconds;
      return a.targetId.localeCompare(b.targetId);
    });

    return {
      animations: sorted,
    };
  }
}
