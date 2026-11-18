import { Time } from "../core/types.js";
import { AnimationNode } from "./AnimationNode.js";
import { AnimationResult } from "./AnimationResult.js";
import { ParallelAnimationOptions } from "./types.js";

/**
 * Nodo de animación concurrente que ejecuta múltiples subanimaciones simultáneamente.
 */
export class ParallelAnimation extends AnimationNode {
  public children: AnimationNode[] = [];

  constructor(options: ParallelAnimationOptions = {}) {
    super(options);
    if (options.children) {
      this.children = [...options.children];
    }
  }

  public add(child: AnimationNode): this {
    this.children.push(child);
    return this;
  }

  public get duration(): Time {
    if (this.children.length === 0) {
      return 0;
    }
    return Math.max(...this.children.map((c) => c.totalDuration));
  }

  public evaluate(time: Time): AnimationResult {
    const result = new AnimationResult();
    const localTime = time - this.delay;

    for (const child of this.children) {
      const childResult = child.evaluate(localTime);
      result.merge(childResult);
    }

    return result;
  }
}
