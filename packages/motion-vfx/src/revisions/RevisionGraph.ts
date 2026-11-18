import { Revision } from "../persistence/schemas/revision.schema.js";

/**
 * Grafo acíclico dirigido (DAG) de revisiones con soporte de ramificación y consultas de ancestría (Fase 18).
 */
export class RevisionGraph {
  private nodes = new Map<string, Revision>(); // revisionId -> Revision
  private childrenMap = new Map<string, string[]>(); // parentRevisionId -> [childRevisionIds]
  private rootRevisionId?: string;
  private headRevisionId?: string;

  constructor(revisions: Revision[] = []) {
    for (const rev of revisions) {
      this.addRevision(rev);
    }
  }

  public addRevision(rev: Revision): void {
    this.nodes.set(rev.revisionId, rev);

    if (rev.parentRevisionId === null) {
      if (!this.rootRevisionId) {
        this.rootRevisionId = rev.revisionId;
      }
    } else {
      let siblings = this.childrenMap.get(rev.parentRevisionId);
      if (!siblings) {
        siblings = [];
        this.childrenMap.set(rev.parentRevisionId, siblings);
      }
      if (!siblings.includes(rev.revisionId)) {
        siblings.push(rev.revisionId);
        siblings.sort();
      }
    }

    this.headRevisionId = rev.revisionId;
  }

  public get(revisionId: string): Revision | undefined {
    return this.nodes.get(revisionId);
  }

  public has(revisionId: string): boolean {
    return this.nodes.has(revisionId);
  }

  public getRoot(): Revision | undefined {
    return this.rootRevisionId ? this.nodes.get(this.rootRevisionId) : undefined;
  }

  public getHead(): Revision | undefined {
    return this.headRevisionId ? this.nodes.get(this.headRevisionId) : undefined;
  }

  public getParent(revisionId: string): Revision | undefined {
    const rev = this.nodes.get(revisionId);
    if (!rev || !rev.parentRevisionId) return undefined;
    return this.nodes.get(rev.parentRevisionId);
  }

  public getChildren(revisionId: string): Revision[] {
    const childIds = this.childrenMap.get(revisionId) ?? [];
    return childIds
      .map((id) => this.nodes.get(id))
      .filter((r): r is Revision => r !== undefined)
      .sort((a, b) => a.revisionId.localeCompare(b.revisionId));
  }

  public getAncestors(revisionId: string): Revision[] {
    const ancestors: Revision[] = [];
    let current = this.getParent(revisionId);

    while (current) {
      ancestors.push(current);
      current = current.parentRevisionId ? this.nodes.get(current.parentRevisionId) : undefined;
    }

    return ancestors;
  }

  public getDescendants(revisionId: string): Revision[] {
    const descendants: Revision[] = [];
    const queue = [...(this.childrenMap.get(revisionId) ?? [])];
    const visited = new Set<string>();

    while (queue.length > 0) {
      const currId = queue.shift()!;
      if (visited.has(currId)) continue;
      visited.add(currId);

      const rev = this.nodes.get(currId);
      if (rev) {
        descendants.push(rev);
        const children = this.childrenMap.get(currId) ?? [];
        queue.push(...children);
      }
    }

    return descendants.sort((a, b) => a.revisionId.localeCompare(b.revisionId));
  }

  public isAncestor(ancestorId: string, descendantId: string): boolean {
    if (ancestorId === descendantId) return true;
    const ancestors = this.getAncestors(descendantId);
    return ancestors.some((a) => a.revisionId === ancestorId);
  }

  public getAll(): Revision[] {
    return Array.from(this.nodes.values()).sort((a, b) => a.revisionId.localeCompare(b.revisionId));
  }
}
