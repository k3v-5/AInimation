import { RevisionChange } from "../persistence/schemas/revision.schema.js";

export interface RevisionDiffResult {
  fromRevisionId?: string;
  toRevisionId?: string;
  changes: RevisionChange[];
  summary: {
    added: number;
    removed: number;
    modified: number;
  };
}

/**
 * Motor de cálculo diferencial semántico y estructural entre revisiones de la IR (Fase 18).
 */
export class RevisionDiff {
  public static diff(fromProjectOrRev: any, toProjectOrRev: any): RevisionDiffResult {
    const fromProj = fromProjectOrRev.project ?? fromProjectOrRev;
    const toProj = toProjectOrRev.project ?? toProjectOrRev;

    const fromRevId = fromProjectOrRev.revisionId;
    const toRevId = toProjectOrRev.revisionId;

    const changes: RevisionChange[] = [];

    const fromElements = fromProj.elements ?? fromProj.composition?.elements ?? fromProj.layers ?? [];
    const toElements = toProj.elements ?? toProj.composition?.elements ?? toProj.layers ?? [];

    const fromMap = new Map<string, any>(fromElements.map((e: any) => [e.id, e]));
    const toMap = new Map<string, any>(toElements.map((e: any) => [e.id, e]));

    // 1. Detectar elementos añadidos o modificados
    for (const [id, toElem] of toMap) {
      if (!fromMap.has(id)) {
        changes.push({
          path: `elements.${id}`,
          operation: "add",
          after: toElem,
          description: `Element '${toElem.name ?? id}' added`,
        });
      } else {
        const fromElem = fromMap.get(id)!;
        this.compareElements(id, fromElem, toElem, changes);
      }
    }

    // 2. Detectar elementos eliminados
    for (const [id, fromElem] of fromMap) {
      if (!toMap.has(id)) {
        changes.push({
          path: `elements.${id}`,
          operation: "remove",
          before: fromElem,
          description: `Element '${fromElem.name ?? id}' removed`,
        });
      }
    }

    // 3. Detectar cambios en Assets
    const fromAssets = new Map<string, any>((fromProj.assets ?? []).map((a: any) => [a.id, a]));
    const toAssets = new Map<string, any>((toProj.assets ?? []).map((a: any) => [a.id, a]));

    for (const [id, toAsset] of toAssets) {
      if (!fromAssets.has(id)) {
        changes.push({
          path: `assets.${id}`,
          operation: "add",
          after: toAsset,
          description: `Asset '${toAsset.name ?? id}' added`,
        });
      }
    }

    for (const [id, fromAsset] of fromAssets) {
      if (!toAssets.has(id)) {
        changes.push({
          path: `assets.${id}`,
          operation: "remove",
          before: fromAsset,
          description: `Asset '${fromAsset.name ?? id}' removed`,
        });
      }
    }

    // 4. Detectar cambios en Composición y Metadatos
    const fromComp = fromProj.composition ?? fromProj;
    const toComp = toProj.composition ?? toProj;

    if (fromComp.duration !== toComp.duration) {
      changes.push({
        path: "composition.duration",
        operation: "replace",
        before: fromComp.duration,
        after: toComp.duration,
        description: `Duration changed from ${fromComp.duration}s to ${toComp.duration}s`,
      });
    }

    if (fromComp.fps !== toComp.fps) {
      changes.push({
        path: "composition.fps",
        operation: "replace",
        before: fromComp.fps,
        after: toComp.fps,
        description: `FPS changed from ${fromComp.fps} to ${toComp.fps}`,
      });
    }

    const added = changes.filter((c) => c.operation === "add").length;
    const removed = changes.filter((c) => c.operation === "remove").length;
    const modified = changes.filter((c) => c.operation === "replace" || c.operation === "move").length;

    return {
      fromRevisionId: fromRevId,
      toRevisionId: toRevId,
      changes,
      summary: {
        added,
        removed,
        modified,
      },
    };
  }

  private static compareElements(id: string, fromElem: any, toElem: any, changes: RevisionChange[]): void {
    if (fromElem.name !== toElem.name) {
      changes.push({
        path: `elements.${id}.name`,
        operation: "replace",
        before: fromElem.name,
        after: toElem.name,
        description: `Name changed from '${fromElem.name}' to '${toElem.name}'`,
      });
    }

    if (fromElem.startTime !== toElem.startTime || fromElem.duration !== toElem.duration) {
      changes.push({
        path: `elements.${id}.timing`,
        operation: "replace",
        before: { startTime: fromElem.startTime, duration: fromElem.duration },
        after: { startTime: toElem.startTime, duration: toElem.duration },
        description: `Timing changed: start ${fromElem.startTime}->${toElem.startTime}, dur ${fromElem.duration}->${toElem.duration}`,
      });
    }

    if (fromElem.text !== toElem.text) {
      changes.push({
        path: `elements.${id}.text`,
        operation: "replace",
        before: fromElem.text,
        after: toElem.text,
        description: `Text changed from '${fromElem.text}' to '${toElem.text}'`,
      });
    }

    // Comparar propiedades de Transform
    if (fromElem.transform && toElem.transform) {
      for (const propName of ["position", "scale", "rotation", "opacity", "anchorPoint"]) {
        const fromProp = fromElem.transform[propName];
        const toProp = toElem.transform[propName];
        if (fromProp && toProp) {
          const fromBase = fromProp.baseValue ?? fromProp;
          const toBase = toProp.baseValue ?? toProp;
          if (JSON.stringify(fromBase) !== JSON.stringify(toBase)) {
            changes.push({
              path: `elements.${id}.transform.${propName}.baseValue`,
              operation: "replace",
              before: fromBase,
              after: toBase,
              description: `Transform ${propName} baseValue modified`,
            });
          }
        }
      }
    }
  }
}
