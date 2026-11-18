import { Diagnostic } from "../types.js";

/**
 * Validador de integridad referencial y enlaces estructurales (Fase 18).
 */
export class ReferentialIntegrityValidator {
  public static validate(projectData: any): Diagnostic[] {
    const diagnostics: Diagnostic[] = [];

    const elements = projectData.elements ?? projectData.composition?.elements ?? [];
    const layers = projectData.layers ?? projectData.composition?.layers ?? [];
    const allItems = [...elements, ...layers];

    const itemIds = new Set<string>(allItems.map((i) => i.id));
    const assetIds = new Set<string>((projectData.assets ?? []).map((a: any) => a.id));

    // 1. Validar jerarquía y parents
    const parentMap = new Map<string, string>();

    for (const item of allItems) {
      if (item.parentId) {
        if (!itemIds.has(item.parentId)) {
          diagnostics.push({
            severity: "error",
            code: "MISSING_PARENT_ID",
            message: `Element '${item.id}' refers to non-existent parentId '${item.parentId}'.`,
            path: `elements.${item.id}.parentId`,
          });
        } else {
          parentMap.set(item.id, item.parentId);
        }
      }

      // 2. Validar referencias a assets
      if (item.assetId && !assetIds.has(item.assetId)) {
        diagnostics.push({
          severity: "error",
          code: "MISSING_ASSET_ID",
          message: `Element '${item.id}' refers to unknown assetId '${item.assetId}'.`,
          path: `elements.${item.id}.assetId`,
        });
      }
    }

    // 3. Detectar ciclos de jerarquía
    for (const [startId] of parentMap) {
      const visited = new Set<string>();
      let curr: string | undefined = startId;

      while (curr && parentMap.has(curr)) {
        if (visited.has(curr)) {
          diagnostics.push({
            severity: "error",
            code: "HIERARCHY_CYCLE_DETECTED",
            message: `Circular parent hierarchy cycle detected involving element '${curr}'.`,
            path: `elements.${curr}.parentId`,
          });
          break;
        }
        visited.add(curr);
        curr = parentMap.get(curr);
      }
    }

    return diagnostics;
  }
}
