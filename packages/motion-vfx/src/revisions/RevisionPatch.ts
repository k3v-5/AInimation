import { RevisionChange } from "../persistence/schemas/revision.schema.js";

/**
 * Motor de aplicación y reversión determinista de parches sobre la IR del proyecto (Fase 18).
 */
export class RevisionPatch {
  /**
   * Aplica un conjunto de cambios a una copia defensiva del proyecto.
   */
  public static applyPatch(project: Record<string, unknown>, changes: RevisionChange[]): Record<string, unknown> {
    const clone = JSON.parse(JSON.stringify(project));

    for (const change of changes) {
      this.applySingleChange(clone, change);
    }

    return clone;
  }

  /**
   * Genera el parche inverso y lo aplica para revertir exactamente los cambios.
   */
  public static reversePatch(project: Record<string, unknown>, changes: RevisionChange[]): Record<string, unknown> {
    const inverseChanges = this.invertChanges(changes);
    return this.applyPatch(project, inverseChanges);
  }

  /**
   * Invierte el orden y las operaciones de un conjunto de cambios.
   */
  public static invertChanges(changes: RevisionChange[]): RevisionChange[] {
    const inverted: RevisionChange[] = [];

    // Recorrer en orden inverso
    for (let i = changes.length - 1; i >= 0; i--) {
      const c = changes[i];
      if (c.operation === "add") {
        inverted.push({
          path: c.path,
          operation: "remove",
          before: c.after,
          description: `Undo addition of '${c.path}'`,
        });
      } else if (c.operation === "remove") {
        inverted.push({
          path: c.path,
          operation: "add",
          after: c.before,
          description: `Undo removal of '${c.path}'`,
        });
      } else if (c.operation === "replace") {
        inverted.push({
          path: c.path,
          operation: "replace",
          before: c.after,
          after: c.before,
          description: `Undo replace on '${c.path}'`,
        });
      }
    }

    return inverted;
  }

  private static applySingleChange(target: any, change: RevisionChange): void {
    const pathParts = change.path.split(".");

    // Casos especiales directos
    if (pathParts[0] === "elements" && pathParts.length === 2) {
      const elemId = pathParts[1];
      const elements = target.elements ?? target.composition?.elements ?? [];
      if (change.operation === "add") {
        const idx = elements.findIndex((e: any) => e.id === elemId);
        if (idx >= 0) {
          elements[idx] = change.after;
        } else {
          elements.push(change.after);
        }
      } else if (change.operation === "remove") {
        const idx = elements.findIndex((e: any) => e.id === elemId);
        if (idx >= 0) {
          elements.splice(idx, 1);
        }
      }
      return;
    }

    if (pathParts[0] === "elements" && pathParts.length > 2) {
      const elemId = pathParts[1];
      const elements = target.elements ?? target.composition?.elements ?? [];
      const elem = elements.find((e: any) => e.id === elemId);
      if (elem) {
        const subPath = pathParts.slice(2);
        this.setDeepValue(elem, subPath, change.after);
      }
      return;
    }

    if (pathParts[0] === "assets" && pathParts.length === 2) {
      const assetId = pathParts[1];
      const assets = target.assets ?? [];
      if (change.operation === "add") {
        const idx = assets.findIndex((a: any) => a.id === assetId);
        if (idx >= 0) assets[idx] = change.after;
        else assets.push(change.after);
      } else if (change.operation === "remove") {
        const idx = assets.findIndex((a: any) => a.id === assetId);
        if (idx >= 0) assets.splice(idx, 1);
      }
      return;
    }

    // Ruta genérica
    this.setDeepValue(target, pathParts, change.after);
  }

  private static setDeepValue(obj: any, pathParts: string[], value: any): void {
    let curr = obj;
    for (let i = 0; i < pathParts.length - 1; i++) {
      const part = pathParts[i];
      if (curr[part] === undefined) {
        curr[part] = {};
      }
      curr = curr[part];
    }
    const lastPart = pathParts[pathParts.length - 1];
    curr[lastPart] = value;
  }
}
