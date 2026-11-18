import { Time } from "../core/types.js";
import { AnimationNode } from "./AnimationNode.js";
import { BasicAnimation } from "./BasicAnimation.js";
import { DelayNode } from "./composition/DelayNode.js";
import { HoldNode } from "./composition/HoldNode.js";
import { OffsetNode } from "./composition/OffsetNode.js";
import { RepeatNode } from "./composition/RepeatNode.js";
import { ParallelAnimation } from "./ParallelAnimation.js";
import { SequenceAnimation } from "./SequenceAnimation.js";
import { BasicAnimationOptions } from "./types.js";

/**
 * Funciones de conveniencia y fábricas fluidas para construir árboles de animación (Fase 3D).
 */
export function basic<T = unknown>(options: BasicAnimationOptions<T>): BasicAnimation {
  return new BasicAnimation(options);
}

export function parallel(...children: AnimationNode[]): ParallelAnimation {
  return new ParallelAnimation({ children });
}

export function sequence(...children: AnimationNode[]): SequenceAnimation {
  return new SequenceAnimation({ children });
}

export function delay(duration: Time): DelayNode {
  return new DelayNode({ duration });
}

export function hold(duration: Time): HoldNode {
  return new HoldNode({ duration });
}

export function repeat(child: AnimationNode, count: number): RepeatNode {
  return new RepeatNode({ child, count });
}

export function offset(child: AnimationNode, offsetTime: Time): OffsetNode {
  return new OffsetNode({ child, offsetTime });
}
