import { normalizeNumber } from "./data-normalizer.js";
import { DataVizHash } from "./dataviz-hash.js";
import { DataVizIssue } from "./errors.js";
import { LabelEngine, PlacedLabel } from "./label-engine.js";
import { LayoutEngine } from "./layout-engine.js";
import { SafeZoneEngine } from "./safe-zone-engine.js";
import { ColorResolver } from "./color-resolver.js";
import { AnimationPlanner } from "./animation-planner.js";
import { DataVizIR, DataVizReport } from "./types.js";

/**
 * REQ-025 §41, §56, §57, §58: Data Visualization Static Semantic & Geometric Validator.
 */
export class DataVizValidator {
  public static validate(ir: DataVizIR): DataVizReport {
    const blockingIssues: DataVizIssue[] = [];
    const warnings: DataVizIssue[] = [];

    // 1. Element ID Uniqueness
    const seenElementIds = new Set<string>();
    for (let i = 0; i < ir.elements.length; i++) {
      const el = ir.elements[i];
      if (seenElementIds.has(el.id)) {
        blockingIssues.push({
          code: "DUPLICATE_ELEMENT_ID",
          path: `elements.${i}.id`,
          message: `Duplicate visual element id detected: '${el.id}'`,
          severity: "BLOCKING",
        });
      }
      seenElementIds.add(el.id);
    }

    // 2. Geometry & Bounds Validation
    let safeElementsCount = 0;
    let overflowCount = 0;
    let totalElementArea = 0;

    const placedLabels: PlacedLabel[] = [];

    for (const el of ir.elements) {
      if (!Number.isFinite(el.position.x) || !Number.isFinite(el.position.y)) {
        blockingIssues.push({
          code: "NON_FINITE_POSITION",
          path: `elements.${el.id}.position`,
          message: `Element '${el.id}' has non-finite position: (${el.position.x}, ${el.position.y})`,
          severity: "BLOCKING",
        });
      }

      if (el.bounds) {
        totalElementArea += el.bounds.width * el.bounds.height;

        if (LayoutEngine.isOutOfBounds(el.bounds, ir.layout.bounds)) {
          overflowCount++;
          warnings.push({
            code: "ELEMENT_OUT_OF_BOUNDS",
            path: `elements.${el.id}.bounds`,
            message: `Element '${el.id}' extends outside canvas bounds`,
            severity: "WARNING",
          });
        }

        if (SafeZoneEngine.isInsideSafeZone(el.bounds, ir.layout.safeZone)) {
          safeElementsCount++;
        }

        if (el.type === "LABEL") {
          placedLabels.push({
            id: el.id,
            text: (el.properties.text as string) ?? el.id,
            bounds: el.bounds,
            emphasis: (el.properties.emphasis as any) ?? "NONE",
          });
        }
      } else {
        safeElementsCount++;
      }
    }

    // 3. Label Collisions
    const collisionResult = LabelEngine.detectCollisions(placedLabels);
    for (const issue of collisionResult.issues) {
      if (issue.severity === "BLOCKING") {
        blockingIssues.push(issue);
      } else {
        warnings.push(issue);
      }
    }

    // 4. Animation Invariants
    for (const anim of ir.animations) {
      if (!seenElementIds.has(anim.targetId)) {
        blockingIssues.push({
          code: "MISSING_ANIMATION_TARGET",
          path: `animations.${anim.id}.targetId`,
          message: `Animation '${anim.id}' targets non-existent element '${anim.targetId}'`,
          severity: "BLOCKING",
        });
      }

      const animIssues = AnimationPlanner.validateAnimation(anim, ir.composition.durationSeconds);
      for (const ai of animIssues) {
        if (ai.severity === "BLOCKING") blockingIssues.push(ai);
        else warnings.push(ai);
      }
    }

    // 5. Color Contrast Check
    const contrastIssue = ColorResolver.checkContrast(ir.style.textColor, ir.style.backgroundColor);
    if (contrastIssue) {
      if (contrastIssue.severity === "BLOCKING") blockingIssues.push(contrastIssue);
      else warnings.push(contrastIssue);
    }

    // 6. Metrics
    const contentArea = Math.max(1, ir.layout.contentBounds.width * ir.layout.contentBounds.height);
    const occupiedAreaRatio = normalizeNumber(Math.min(1.0, totalElementArea / contentArea));
    const safeZoneCompliance = normalizeNumber(
      ir.elements.length > 0 ? safeElementsCount / ir.elements.length : 1.0
    );

    // Compute canonical checksum
    const checksumSha256 = ir.checksumSha256 ?? DataVizHash.computeSha256(ir);

    const status =
      blockingIssues.length > 0
        ? "BLOCKED"
        : warnings.length > 0
        ? "VALID_WITH_WARNINGS"
        : "VALID";

    return {
      status,
      visualizationType: ir.type,
      blockingIssues,
      warnings,
      elementCount: ir.elements.length,
      animationCount: ir.animations.length,
      checksumSha256,
      deterministic: true,
      metrics: {
        dataPointCount: ir.dataset.points.length,
        occupiedAreaRatio,
        safeZoneCompliance,
        overlapCount: collisionResult.collidingPairs.length,
        overflowCount,
      },
    };
  }
}
