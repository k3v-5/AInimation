import { ValidationError } from "../../errors/index.js";
import { EditingIssue, EditingPlan } from "../types/index.js";

/**
 * Validador estricto y de integridad estructural de planes de edición generados por IA (Fase 7).
 */
export class PlanValidator {
  public static validate(plan: EditingPlan): EditingIssue[] {
    const issues: EditingIssue[] = [];

    // 1. Validar Brief
    if (!plan.brief || plan.brief.targetDuration <= 0) {
      issues.push({
        severity: "error",
        message: "Brief targetDuration must be greater than 0.",
      });
    }

    // 2. Validar Secciones Editoriales
    if (!plan.sections || plan.sections.length === 0) {
      issues.push({
        severity: "error",
        message: "EditingPlan must contain at least one editorial section.",
      });
    } else {
      let prevEnd = 0;
      for (const section of plan.sections) {
        if (section.start < 0 || section.end < section.start) {
          issues.push({
            severity: "error",
            sectionId: section.id,
            message: `Section '${section.id}' has inverted or negative timestamps: [${section.start}, ${section.end}].`,
          });
        }
        if (section.start < prevEnd - 0.001) {
          issues.push({
            severity: "warning",
            sectionId: section.id,
            message: `Section '${section.id}' overlaps with previous section.`,
          });
        }
        prevEnd = section.end;
      }
    }

    // 3. Validar Tomas (Shots)
    for (const scene of plan.scenes || []) {
      for (const shot of scene.shots || []) {
        if (shot.duration <= 0) {
          issues.push({
            severity: "error",
            sectionId: scene.sectionId,
            message: `Shot '${shot.id}' has non-positive duration: ${shot.duration}s.`,
          });
        }
      }
    }

    return issues;
  }

  public static assertValid(plan: EditingPlan): void {
    const issues = this.validate(plan);
    const errors = issues.filter((i) => i.severity === "error");
    if (errors.length > 0) {
      throw new ValidationError(
        `INVALID_EDITING_PLAN: ${errors.map((e) => e.message).join(" | ")}`
      );
    }
  }
}
