import { RevisionDiff } from "./RevisionDiff.js";
import { RevisionPatch } from "./RevisionPatch.js";

export interface RevisionConflict {
  path: string;
  baseValue: unknown;
  leftValue: unknown;
  rightValue: unknown;
}

export interface MergeResult {
  merged: boolean;
  result?: Record<string, unknown>;
  conflicts: RevisionConflict[];
}

/**
 * Motor de fusión 3-way determinista para ramas de revisiones (Fase 18).
 */
export class RevisionMerge {
  /**
   * Realiza una fusión 3-way entre una revisión base común y dos ramas independientes (left y right).
   */
  public static merge(
    baseProject: Record<string, unknown>,
    leftProject: Record<string, unknown>,
    rightProject: Record<string, unknown>
  ): MergeResult {
    const leftDiff = RevisionDiff.diff(baseProject, leftProject);
    const rightDiff = RevisionDiff.diff(baseProject, rightProject);

    const conflicts: RevisionConflict[] = [];

    const leftChangeMap = new Map<string, any>(leftDiff.changes.map((c) => [c.path, c]));
    const rightChangeMap = new Map<string, any>(rightDiff.changes.map((c) => [c.path, c]));

    // Detectar conflictos en rutas compartidas
    for (const [path, leftChange] of leftChangeMap) {
      if (rightChangeMap.has(path)) {
        const rightChange = rightChangeMap.get(path)!;
        const leftVal = JSON.stringify(leftChange.after ?? leftChange.before);
        const rightVal = JSON.stringify(rightChange.after ?? rightChange.before);

        if (leftVal !== rightVal) {
          conflicts.push({
            path,
            baseValue: leftChange.before,
            leftValue: leftChange.after,
            rightValue: rightChange.after,
          });
        }
      }
    }

    if (conflicts.length > 0) {
      return {
        merged: false,
        conflicts,
      };
    }

    // Fusión limpia: aplicar cambios de left y cambios no conflictivos de right
    let mergedProject = RevisionPatch.applyPatch(baseProject, leftDiff.changes);
    const nonOverlappingRightChanges = rightDiff.changes.filter((c) => !leftChangeMap.has(c.path));
    mergedProject = RevisionPatch.applyPatch(mergedProject, nonOverlappingRightChanges);

    return {
      merged: true,
      result: mergedProject,
      conflicts: [],
    };
  }
}
