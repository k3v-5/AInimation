import { AssetChange, DiffEntry, ProjectDiff, TimingChange } from "./types.js";

/**
 * Motor de comparación diferencial semántica y estructural entre revisiones de proyecto (Fase 18).
 */
export class ProjectDiffEngine {
  public static diff(beforeEnvelope: any, afterEnvelope: any): ProjectDiff {
    const beforeProj = beforeEnvelope.project ?? beforeEnvelope;
    const afterProj = afterEnvelope.project ?? afterEnvelope;

    const projectId = beforeEnvelope.projectId ?? afterEnvelope.projectId ?? "unknown";
    const fromRev = beforeEnvelope.revisionId ?? "rev_before";
    const toRev = afterEnvelope.revisionId ?? "rev_after";

    const added: DiffEntry[] = [];
    const removed: DiffEntry[] = [];
    const modified: DiffEntry[] = [];
    const timingChanges: TimingChange[] = [];
    const assetChanges: AssetChange[] = [];

    const beforeElems = beforeProj.elements ?? beforeProj.composition?.elements ?? beforeProj.layers ?? [];
    const afterElems = afterProj.elements ?? afterProj.composition?.elements ?? afterProj.layers ?? [];

    const beforeMap = new Map<string, any>(beforeElems.map((e: any) => [e.id, e]));
    const afterMap = new Map<string, any>(afterElems.map((e: any) => [e.id, e]));

    // 1. Detectar capas añadidas y modificadas
    for (const [id, afterElem] of afterMap) {
      if (!beforeMap.has(id)) {
        added.push({
          path: `elements.${id}`,
          type: "added",
          after: afterElem,
          description: `Layer/Element '${afterElem.name}' [${id}] added`,
        });
      } else {
        const beforeElem = beforeMap.get(id)!;
        this.compareElements(beforeElem, afterElem, modified, timingChanges);
      }
    }

    // 2. Detectar capas eliminadas
    for (const [id, beforeElem] of beforeMap) {
      if (!afterMap.has(id)) {
        removed.push({
          path: `elements.${id}`,
          type: "removed",
          before: beforeElem,
          description: `Layer/Element '${beforeElem.name}' [${id}] removed`,
        });
      }
    }

    // 3. Detectar cambios en Assets
    const beforeAssets = new Map<string, any>((beforeProj.assets ?? []).map((a: any) => [a.id, a]));
    const afterAssets = new Map<string, any>((afterProj.assets ?? []).map((a: any) => [a.id, a]));

    for (const [id] of afterAssets) {
      if (!beforeAssets.has(id)) {
        assetChanges.push({ assetId: id, type: "added" });
      }
    }
    for (const [id] of beforeAssets) {
      if (!afterAssets.has(id)) {
        assetChanges.push({ assetId: id, type: "removed" });
      }
    }

    return {
      projectId,
      fromRevisionId: fromRev,
      toRevisionId: toRev,
      added,
      removed,
      modified,
      timingChanges,
      assetChanges,
      summary: {
        layersAdded: added.length,
        layersRemoved: removed.length,
        layersModified: modified.length,
        timingModifications: timingChanges.length,
        assetModifications: assetChanges.length,
      },
    };
  }

  private static compareElements(
    before: any,
    after: any,
    modified: DiffEntry[],
    timingChanges: TimingChange[]
  ): void {
    const id = before.id;

    // Comparar Nombre
    if (before.name !== after.name) {
      modified.push({
        path: `elements.${id}.name`,
        type: "modified",
        before: before.name,
        after: after.name,
        description: `Name updated from '${before.name}' to '${after.name}'`,
      });
    }

    // Comparar Timing
    const bStart = before.startTime ?? 0;
    const bDur = before.duration ?? (before.endTime ? before.endTime - bStart : 10);
    const aStart = after.startTime ?? 0;
    const aDur = after.duration ?? (after.endTime ? after.endTime - aStart : 10);

    if (bStart !== aStart || bDur !== aDur) {
      timingChanges.push({
        entityId: id,
        entityName: after.name ?? id,
        before: { startTime: bStart, duration: bDur },
        after: { startTime: aStart, duration: aDur },
      });
      modified.push({
        path: `elements.${id}.timing`,
        type: "modified",
        before: { startTime: bStart, duration: bDur },
        after: { startTime: aStart, duration: aDur },
        description: `Timing changed: start ${bStart}s -> ${aStart}s, dur ${bDur}s -> ${aDur}s`,
      });
    }

    // Comparar Texto y Tipografía
    if (before.text !== after.text) {
      modified.push({
        path: `elements.${id}.text`,
        type: "modified",
        before: before.text,
        after: after.text,
        description: `Text content updated from '${before.text}' to '${after.text}'`,
      });
    }

    if (before.style && after.style) {
      for (const key of Object.keys(after.style)) {
        if (before.style[key] !== after.style[key]) {
          modified.push({
            path: `elements.${id}.style.${key}`,
            type: "modified",
            before: before.style[key],
            after: after.style[key],
            description: `Typography.${key} changed from ${before.style[key]} to ${after.style[key]}`,
          });
        }
      }
    }
  }
}
