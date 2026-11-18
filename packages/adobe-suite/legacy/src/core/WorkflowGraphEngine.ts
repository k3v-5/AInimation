import { WorkflowGraph, WorkflowNode } from './abstractions.js';

export class WorkflowGraphEngine {
  public resolveExecutionOrder(graph: WorkflowGraph): WorkflowNode[][] {
    const inDegree: Map<string, number> = new Map();
    const adjList: Map<string, string[]> = new Map();
    const nodeMap: Map<string, WorkflowNode> = new Map();

    for (const node of graph.nodes) {
      inDegree.set(node.id, 0);
      adjList.set(node.id, []);
      nodeMap.set(node.id, node);
    }

    for (const edge of graph.edges) {
      if (!inDegree.has(edge.targetId) || !adjList.has(edge.sourceId)) {
        throw new Error(`Invalid edge: ${edge.sourceId} -> ${edge.targetId}`);
      }
      adjList.get(edge.sourceId)!.push(edge.targetId);
      inDegree.set(edge.targetId, inDegree.get(edge.targetId)! + 1);
    }

    const executionBatches: WorkflowNode[][] = [];
    let currentBatch: string[] = [];

    for (const [nodeId, degree] of inDegree.entries()) {
      if (degree === 0) {
        currentBatch.push(nodeId);
      }
    }

    while (currentBatch.length > 0) {
      const nextBatch: string[] = [];
      const batchNodes: WorkflowNode[] = currentBatch.map(id => nodeMap.get(id)!);
      executionBatches.push(batchNodes);

      for (const nodeId of currentBatch) {
        const neighbors = adjList.get(nodeId) || [];
        for (const neighbor of neighbors) {
          const currentInDegree = inDegree.get(neighbor)! - 1;
          inDegree.set(neighbor, currentInDegree);
          if (currentInDegree === 0) {
            nextBatch.push(neighbor);
          }
        }
      }
      currentBatch = nextBatch;
    }

    for (const degree of inDegree.values()) {
      if (degree > 0) {
        throw new Error('Cycle detected in WorkflowGraph');
      }
    }

    return executionBatches;
  }
}