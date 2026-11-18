import { AnimationNode } from "../../animation/AnimationNode.js";
import { BasicAnimation } from "../../animation/BasicAnimation.js";
import { ParallelAnimation } from "../../animation/ParallelAnimation.js";
import { TextElement } from "../../elements/TextElement.js";
import { TextSegmenter } from "../segmenter/TextSegmenter.js";
import { TextSelector } from "../selector/TextSelector.js";
import { TextAnimationOptions } from "../types/index.js";

/**
 * Constructor de animaciones tipográficas escalonadas sobre subtargets virtuales (Fase 4B).
 */
export function animateText(
  target: TextElement | { id: string; text?: string | { getValue(): string } },
  options: TextAnimationOptions
): ParallelAnimation {
  const elementId = target.id;
  let rawText = "";
  if ("text" in target && target.text) {
    if (typeof target.text === "string") {
      rawText = target.text;
    } else if (typeof (target.text as any).getValue === "function") {
      rawText = (target.text as any).getValue();
    }
  }

  const layout = TextSegmenter.segment(rawText);
  const selectedTargets = TextSelector.select(
    elementId,
    layout,
    {
      scope: options.scope ?? "character",
      order: options.order ?? "forward",
      range: options.range,
      seed: options.seed,
    },
    options.stagger
  );

  const baseDelay = options.delay ?? 0;
  const children: AnimationNode[] = [];

  for (const sel of selectedTargets) {
    let childAnim: AnimationNode;

    if (typeof options.animation === "function") {
      childAnim = options.animation({ id: sel.targetId });
    } else if (options.animation instanceof AnimationNode) {
      childAnim = cloneNodeWithRetarget(options.animation, sel.targetId);
    } else {
      throw new Error("Invalid animation provided to animateText.");
    }

    childAnim.delay = baseDelay + sel.delay;
    children.push(childAnim);
  }

  return new ParallelAnimation({
    id: options.id,
    delay: 0,
    priority: options.priority,
    children,
  });
}

function cloneNodeWithRetarget(node: AnimationNode, targetId: string): AnimationNode {
  if (node instanceof BasicAnimation) {
    const clonedTracks = node.tracks.map((track) => ({
      ...track,
      target: {
        elementId: targetId,
        propertyPath: track.target.propertyPath,
      },
    }));
    return new BasicAnimation({
      id: `${node.id}_${targetId}`,
      delay: node.delay,
      duration: node.duration,
      easing: node.easing,
      motion: node.motion,
      priority: node.priority,
      tracks: clonedTracks,
    });
  } else if (node instanceof ParallelAnimation) {
    const children = node.children.map((c) => cloneNodeWithRetarget(c, targetId));
    return new ParallelAnimation({
      id: `${node.id}_${targetId}`,
      delay: node.delay,
      priority: node.priority,
      children,
    });
  }
  throw new Error("Unsupported node type for retargeting.");
}
