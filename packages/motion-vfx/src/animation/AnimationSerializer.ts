import { SerializationError } from "../errors/index.js";
import { AnimationNode } from "./AnimationNode.js";
import { BasicAnimation } from "./BasicAnimation.js";
import { DelayNode } from "./composition/DelayNode.js";
import { HoldNode } from "./composition/HoldNode.js";
import { OffsetNode } from "./composition/OffsetNode.js";
import { RepeatNode } from "./composition/RepeatNode.js";
import { MotionRegistry } from "./motion/MotionRegistry.js";
import { ParallelAnimation } from "./ParallelAnimation.js";
import { SequenceAnimation } from "./SequenceAnimation.js";
import { SerializedAnimationNode, SerializedBasicAnimation } from "./types.js";

/**
 * Serializador y deserializador para árboles polimórficos de animación (Fase 3D).
 */
export class AnimationSerializer {
  /**
   * Serializa un nodo de animación a un objeto plano JSON.
   */
  public static serialize(node: AnimationNode): any {
    if (node instanceof BasicAnimation) {
      return {
        type: "basic",
        id: node.id,
        delay: node.delay,
        duration: node.duration,
        priority: node.priority,
        easing: node.easing,
        motion: node.motion ? node.motion.toJSON() : undefined,
        tracks: node.tracks.map((t) => ({
          target: { ...t.target },
          from: t.from,
          to: t.to,
          easing: t.easing,
        })),
      };
    }

    if (node instanceof ParallelAnimation) {
      return {
        type: "parallel",
        id: node.id,
        delay: node.delay,
        priority: node.priority,
        children: node.children.map((c) => this.serialize(c)),
      };
    }

    if (node instanceof SequenceAnimation) {
      return {
        type: "sequence",
        id: node.id,
        delay: node.delay,
        priority: node.priority,
        children: node.children.map((c) => this.serialize(c)),
      };
    }

    if (node instanceof DelayNode) {
      return {
        type: "delay",
        id: node.id,
        delay: node.delay,
        duration: node.duration,
      };
    }

    if (node instanceof HoldNode) {
      return {
        type: "hold",
        id: node.id,
        delay: node.delay,
        duration: node.duration,
      };
    }

    if (node instanceof RepeatNode) {
      return {
        type: "repeat",
        id: node.id,
        delay: node.delay,
        count: node.count,
        child: this.serialize(node.child),
      };
    }

    if (node instanceof OffsetNode) {
      return {
        type: "offset",
        id: node.id,
        delay: node.delay,
        offsetTime: node.offsetTime,
        child: this.serialize(node.child),
      };
    }

    throw new SerializationError(`Cannot serialize unknown animation node type.`);
  }

  /**
   * Deserializa un objeto JSON en un árbol polimórfico de AnimationNode.
   */
  public static deserialize(raw: any): AnimationNode {
    if (!raw || typeof raw !== "object") {
      throw new SerializationError("Animation JSON must be an object.");
    }

    const { type, id, delay, priority } = raw;

    switch (type) {
      case "basic": {
        const basic = raw as SerializedBasicAnimation;
        const motion = basic.motion ? MotionRegistry.fromJSON(basic.motion) : undefined;
        return new BasicAnimation({
          id,
          delay,
          priority,
          duration: basic.duration,
          easing: basic.easing,
          motion,
          tracks: basic.tracks.map((t) => ({
            target: { ...t.target },
            from: t.from,
            to: t.to,
            easing: t.easing,
          })),
        });
      }

      case "parallel": {
        const children = (raw.children ?? []).map((c: any) => this.deserialize(c));
        return new ParallelAnimation({
          id,
          delay,
          priority,
          children,
        });
      }

      case "sequence": {
        const children = (raw.children ?? []).map((c: any) => this.deserialize(c));
        return new SequenceAnimation({
          id,
          delay,
          priority,
          children,
        });
      }

      case "delay": {
        return new DelayNode({
          id,
          delay,
          duration: raw.duration,
        });
      }

      case "hold": {
        return new HoldNode({
          id,
          delay,
          duration: raw.duration,
        });
      }

      case "repeat": {
        return new RepeatNode({
          id,
          delay,
          count: raw.count,
          child: this.deserialize(raw.child),
        });
      }

      case "offset": {
        return new OffsetNode({
          id,
          delay,
          offsetTime: raw.offsetTime,
          child: this.deserialize(raw.child),
        });
      }

      default:
        throw new SerializationError(`Unsupported animation node type '${type}'.`);
    }
  }
}
