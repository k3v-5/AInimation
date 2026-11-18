import { AnimationNode } from "../AnimationNode.js";
import { ParallelAnimation } from "../ParallelAnimation.js";
import { StaggerOptions } from "./types.js";

/**
 * Distribuye de forma escalonada (stagger) la ejecución de animaciones sobre una lista de elementos.
 */
export function stagger<T>(
  items: T[],
  factory: (item: T, index: number) => AnimationNode,
  options: StaggerOptions
): ParallelAnimation {
  const count = items.length;
  const staggerDelay = options.delay;
  const mode = options.mode ?? "forward";

  const children: AnimationNode[] = [];

  for (let i = 0; i < count; i++) {
    const item = items[i];
    const node = factory(item, i);

    let calculatedDelay = 0;
    if (mode === "reverse") {
      calculatedDelay = (count - 1 - i) * staggerDelay;
    } else {
      calculatedDelay = i * staggerDelay;
    }

    node.delay += calculatedDelay;
    children.push(node);
  }

  return new ParallelAnimation({ children });
}
