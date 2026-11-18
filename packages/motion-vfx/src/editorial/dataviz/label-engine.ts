import { DataVizIssue } from "./errors.js";
import { DataPointEmphasis, Rect } from "./types.js";

export interface PlacedLabel {
  id: string;
  text: string;
  bounds: Rect;
  emphasis?: DataPointEmphasis;
}

export interface LabelCollisionResult {
  hasCollisions: boolean;
  issues: DataVizIssue[];
  collidingPairs: [string, string][];
}

/**
 * REQ-025 §97, §98: Label Collision Engine.
 * Detects visual bounding box intersections and blocks critical primary label collisions.
 */
export class LabelEngine {
  public static intersects(a: Rect, b: Rect): boolean {
    return !(
      a.x + a.width <= b.x ||
      b.x + b.width <= a.x ||
      a.y + a.height <= b.y ||
      b.y + b.height <= a.y
    );
  }

  public static detectCollisions(labels: PlacedLabel[]): LabelCollisionResult {
    const issues: DataVizIssue[] = [];
    const collidingPairs: [string, string][] = [];

    for (let i = 0; i < labels.length; i++) {
      for (let j = i + 1; j < labels.length; j++) {
        const l1 = labels[i];
        const l2 = labels[j];

        if (this.intersects(l1.bounds, l2.bounds)) {
          collidingPairs.push([l1.id, l2.id]);

          const hasPrimary = l1.emphasis === "PRIMARY" || l2.emphasis === "PRIMARY";
          if (hasPrimary) {
            // REQ-025 §98: Primary data label collision is BLOCKING
            issues.push({
              code: "CRITICAL_LABEL_COLLISION",
              path: `labels.${l1.id}`,
              message: `Critical primary label '${l1.text}' intersects with label '${l2.text}'`,
              severity: "BLOCKING",
            });
          } else {
            issues.push({
              code: "LABEL_COLLISION",
              path: `labels.${l1.id}`,
              message: `Label '${l1.text}' overlaps with label '${l2.text}'`,
              severity: "WARNING",
            });
          }
        }
      }
    }

    return {
      hasCollisions: collidingPairs.length > 0,
      issues,
      collidingPairs,
    };
  }
}
