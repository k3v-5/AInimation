import { Time } from "../core/types.js";
import { AnimationNode } from "./AnimationNode.js";
import { AnimationResult } from "./AnimationResult.js";
import { SequenceAnimationOptions } from "./types.js";

/**
 * Nodo de animación secuencial que ejecuta una serie de subanimaciones en orden cronológico.
 */
export class SequenceAnimation extends AnimationNode {
  public children: AnimationNode[] = [];

  constructor(options: SequenceAnimationOptions = {}) {
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
    return this.children.reduce((acc, c) => acc + c.totalDuration, 0);
  }

  public evaluate(time: Time): AnimationResult {
    const result = new AnimationResult();
    const localTime = time - this.delay;

    // Pase 1: Pre-poblar valores 'from' de pasos futuros aún no iniciados
    let cumulativeTime = 0;
    for (const child of this.children) {
      const childTotal = child.totalDuration;
      const childRelativeTime = localTime - cumulativeTime;

      if (childRelativeTime < 0) {
        const futureInitialResult = child.evaluate(0);
        result.merge(futureInitialResult);
      }

      cumulativeTime += childTotal;
    }

    // Pase 2: Evaluar y fusionar pasos activos y completados en orden cronológico (toman precedencia)
    cumulativeTime = 0;
    for (const child of this.children) {
      const childTotal = child.totalDuration;
      const childRelativeTime = localTime - cumulativeTime;

      if (childRelativeTime >= 0) {
        let childEvalTime = 0;
        if (childRelativeTime >= childTotal) {
          childEvalTime = childTotal;
        } else {
          childEvalTime = childRelativeTime;
        }

        const childResult = child.evaluate(childEvalTime);
        result.merge(childResult);
      }

      cumulativeTime += childTotal;
    }

    return result;
  }
}
