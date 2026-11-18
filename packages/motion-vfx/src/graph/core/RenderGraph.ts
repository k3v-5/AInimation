import { ValidationError } from "../../errors/index.js";
import { RenderContext, RenderNode } from "../types/index.js";

/**
 * Grafo Acíclico Dirigido (DAG) de dependencias de renderizado y compilación de escena (Fase 5H).
 */
export class RenderGraph {
  private nodes = new Map<string, RenderNode>();

  public addNode(node: RenderNode): this {
    if (!node || !node.id) {
      throw new ValidationError("RenderNode must have a valid id.");
    }
    if (this.nodes.has(node.id)) {
      throw new ValidationError(`DUPLICATE_RENDER_NODE: Node '${node.id}' already exists.`);
    }
    this.nodes.set(node.id, node);
    return this;
  }

  public getNode(id: string): RenderNode | undefined {
    return this.nodes.get(id);
  }

  public get size(): number {
    return this.nodes.size;
  }

  /**
   * Compila el grafo resolviendo el orden topológico y detectando ciclos.
   */
  public compile(): RenderNode[] {
    const inDegree = new Map<string, number>();
    const adjacency = new Map<string, string[]>();

    for (const [id] of this.nodes) {
      inDegree.set(id, 0);
      adjacency.set(id, []);
    }

    // Construir lista de adyacencia (u -> v significa que v depende de u)
    for (const [id, node] of this.nodes) {
      for (const inputId of node.inputs) {
        if (!this.nodes.has(inputId)) {
          throw new ValidationError(
            `MISSING_GRAPH_INPUT: Node '${id}' depends on non-existent node '${inputId}'.`
          );
        }
        adjacency.get(inputId)!.push(id);
        inDegree.set(id, (inDegree.get(id) ?? 0) + 1);
      }
    }

    // Algoritmo de Kahn para ordenación topológica
    const queue: string[] = [];
    for (const [id, degree] of inDegree) {
      if (degree === 0) {
        queue.push(id);
      }
    }

    const sortedNodes: RenderNode[] = [];

    while (queue.length > 0) {
      const currentId = queue.shift()!;
      sortedNodes.push(this.nodes.get(currentId)!);

      for (const neighbor of adjacency.get(currentId)!) {
        const newDegree = inDegree.get(neighbor)! - 1;
        inDegree.set(neighbor, newDegree);
        if (newDegree === 0) {
          queue.push(neighbor);
        }
      }
    }

    if (sortedNodes.length !== this.nodes.size) {
      throw new ValidationError("GRAPH_CYCLE_DETECTED: Cyclic dependency detected in RenderGraph.");
    }

    return sortedNodes;
  }

  /**
   * Ejecuta el grafo evaluando cada nodo en orden topológico.
   */
  public execute(context: RenderContext): Map<string, any> {
    const sorted = this.compile();
    const results = new Map<string, any>();

    for (const node of sorted) {
      const nodeInputs = new Map<string, any>();
      for (const inputId of node.inputs) {
        nodeInputs.set(inputId, results.get(inputId));
      }
      const output = node.evaluate(context, nodeInputs);
      results.set(node.id, output);
    }

    return results;
  }
}
