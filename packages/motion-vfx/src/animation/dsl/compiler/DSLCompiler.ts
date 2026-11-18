import { AnimationNode } from "../../AnimationNode.js";
import { BasicAnimation } from "../../BasicAnimation.js";
import { DelayNode } from "../../composition/DelayNode.js";
import { HoldNode } from "../../composition/HoldNode.js";
import { OffsetNode } from "../../composition/OffsetNode.js";
import { RepeatNode } from "../../composition/RepeatNode.js";
import { ParallelAnimation } from "../../ParallelAnimation.js";
import { SequenceAnimation } from "../../SequenceAnimation.js";
import { MotionRegistry } from "../../motion/MotionRegistry.js";
import { MotionFunction } from "../../motion/types.js";
import { fadeIn, fadeOut } from "../../primitives/fade.js";
import { rotateIn, rotateOut } from "../../primitives/rotate.js";
import { scaleIn, scaleOut } from "../../primitives/scale.js";
import { slideIn, slideOut } from "../../primitives/slide.js";
import { PresetResolver } from "../../../presets/index.js";
import { animateText } from "../../../text/index.js";
import { DSLParser } from "../parser/DSLParser.js";
import {
  AnimationIR,
  DSLBasicAnimationNode,
  DSLCompositionNode,
  DSLDocument,
  DSLMotionConfig,
  DSLNode,
} from "../types/index.js";
import { DSLValidator } from "../validator/DSLValidator.js";

/**
 * Compilador del Animation DSL hacia la Representación Intermedia (AnimationIR) y árboles AnimationNode.
 */
export class DSLCompiler {
  /**
   * Compila un documento DSL (objeto o JSON string) hacia AnimationIR verificado.
   */
  public static compile(input: string | Record<string, unknown> | DSLDocument): AnimationIR {
    const doc: DSLDocument = DSLParser.parse(input as any);

    // Validación formal con errores de diagnóstico de ruta
    DSLValidator.assertValid(doc);

    const rootNodes = (doc.animations ?? []).map((node: DSLNode) => this.compileNode(node));

    // Extraer metadatos agregados de la IR
    const targets = new Set<string>();
    let totalDuration = 0;

    for (const node of rootNodes) {
      if (node.totalDuration > totalDuration) {
        totalDuration = node.totalDuration;
      }
      this.collectTargets(node, targets);
    }

    return {
      version: 1,
      rootNodes,
      metadata: {
        nodeCount: rootNodes.length,
        totalDuration,
        targets: Array.from(targets),
      },
    };
  }

  private static compileMotion(motion: string | DSLMotionConfig | undefined): MotionFunction | undefined {
    if (!motion) return undefined;
    if (typeof motion === "string") {
      return MotionRegistry.fromJSON({ type: motion });
    }
    return MotionRegistry.fromJSON(motion);
  }

  private static compileNode(node: DSLNode): AnimationNode {
    switch (node.type) {
      // 1. Primitivas de movimiento
      case "fadeIn":
      case "fadeOut":
      case "slideIn":
      case "slideOut":
      case "scaleIn":
      case "scaleOut":
      case "rotateIn":
      case "rotateOut":
        return this.compilePrimitiveNode(node as DSLBasicAnimationNode);

      // 2. Combinadores y composición
      case "parallel": {
        const comp = node as DSLCompositionNode;
        const children = (comp.children ?? []).map((c) => this.compileNode(c));
        return new ParallelAnimation({
          id: comp.id,
          delay: typeof comp.delay === "number" ? comp.delay : 0,
          priority: comp.priority,
          children,
        });
      }

      case "sequence": {
        const comp = node as DSLCompositionNode;
        const children = (comp.children ?? []).map((c) => this.compileNode(c));
        return new SequenceAnimation({
          id: comp.id,
          delay: typeof comp.delay === "number" ? comp.delay : 0,
          priority: comp.priority,
          children,
        });
      }

      case "delay": {
        const comp = node as DSLCompositionNode;
        return new DelayNode({
          id: comp.id,
          delay: typeof comp.delay === "number" ? comp.delay : 0,
          duration: Number(comp.duration ?? 0.5),
        });
      }

      case "hold": {
        const comp = node as DSLCompositionNode;
        return new HoldNode({
          id: comp.id,
          delay: typeof comp.delay === "number" ? comp.delay : 0,
          duration: Number(comp.duration ?? 1.0),
        });
      }

      case "repeat": {
        const comp = node as DSLCompositionNode;
        const child = this.compileNode(comp.children![0]);
        return new RepeatNode({
          id: comp.id,
          delay: typeof comp.delay === "number" ? comp.delay : 0,
          count: Number(comp.count ?? 1),
          child,
        });
      }

      case "offset": {
        const comp = node as DSLCompositionNode;
        const child = this.compileNode(comp.children![0]);
        return new OffsetNode({
          id: comp.id,
          delay: typeof comp.delay === "number" ? comp.delay : 0,
          offsetTime: Number(comp.offsetTime ?? 0),
          child,
        });
      }

      case "stagger": {
        const comp = node as DSLCompositionNode;
        const staggerDelay = Number(comp.staggerDelay ?? 0.1);
        const mode = comp.staggerMode ?? "forward";
        const count = (comp.children ?? []).length;

        const children: AnimationNode[] = (comp.children ?? []).map((c, i) => {
          const childNode = this.compileNode(c);
          const delta = mode === "reverse" ? (count - 1 - i) * staggerDelay : i * staggerDelay;
          childNode.delay += delta;
          return childNode;
        });

        return new ParallelAnimation({
          id: comp.id,
          delay: typeof comp.delay === "number" ? comp.delay : 0,
          priority: comp.priority,
          children,
        });
      }

      case "preset": {
        const presetNode = node as import("../types/index.js").DSLPresetNode;
        const targetElement = { id: presetNode.target.startsWith("#") ? presetNode.target.slice(1) : presetNode.target };
        return PresetResolver.resolve(presetNode.name, targetElement, presetNode.overrides ?? {});
      }

      case "textAnimation": {
        const textNode = node as import("../types/index.js").DSLTextAnimationNode;
        const targetElement = { id: textNode.target.startsWith("#") ? textNode.target.slice(1) : textNode.target, text: textNode.text };
        const baseAnim = this.compilePrimitiveNode(textNode.animation);
        return animateText(targetElement as any, {
          id: textNode.id,
          delay: typeof textNode.delay === "number" ? textNode.delay : undefined,
          priority: textNode.priority,
          scope: textNode.scope,
          order: textNode.order,
          seed: textNode.seed,
          stagger: textNode.stagger as any,
          animation: baseAnim,
        });
      }

      default:
        throw new Error(`Compiler does not support node type '${(node as any).type}'.`);
    }
  }

  private static compilePrimitiveNode(node: DSLBasicAnimationNode): BasicAnimation {
    const targetElement = { id: node.target.startsWith("#") ? node.target.slice(1) : node.target };
    const motion = this.compileMotion(node.motion);

    const opts: any = {
      id: node.id,
      duration: typeof node.duration === "number" ? node.duration : undefined,
      delay: typeof node.delay === "number" ? node.delay : undefined,
      easing: node.easing,
      priority: node.priority,
      motion,
    };

    switch (node.type) {
      case "fadeIn":
        return fadeIn(targetElement as any, { ...opts, from: node.from as any, to: node.to as any });
      case "fadeOut":
        return fadeOut(targetElement as any, { ...opts, from: node.from as any, to: node.to as any });
      case "slideIn":
        return slideIn(targetElement as any, {
          ...opts,
          direction: node.direction,
          distance: typeof node.distance === "number" ? node.distance : undefined,
          from: node.from as any,
          to: node.to as any,
        });
      case "slideOut":
        return slideOut(targetElement as any, {
          ...opts,
          direction: node.direction,
          distance: typeof node.distance === "number" ? node.distance : undefined,
          from: node.from as any,
          to: node.to as any,
        });
      case "scaleIn":
        return scaleIn(targetElement as any, { ...opts, from: node.from as any, to: node.to as any });
      case "scaleOut":
        return scaleOut(targetElement as any, { ...opts, from: node.from as any, to: node.to as any });
      case "rotateIn":
        return rotateIn(targetElement as any, { ...opts, from: node.from as any, to: node.to as any });
      case "rotateOut":
        return rotateOut(targetElement as any, { ...opts, from: node.from as any, to: node.to as any });
    }
  }

  private static collectTargets(node: AnimationNode, targets: Set<string>): void {
    if (node instanceof BasicAnimation) {
      for (const track of node.tracks) {
        targets.add(track.target.elementId);
      }
    } else if (node instanceof ParallelAnimation || node instanceof SequenceAnimation) {
      for (const child of node.children) {
        this.collectTargets(child, targets);
      }
    } else if (node instanceof RepeatNode || node instanceof OffsetNode) {
      this.collectTargets(node.child, targets);
    }
  }
}
