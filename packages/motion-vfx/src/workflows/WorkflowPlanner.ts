import { WorkflowDefinition, WorkflowStepDefinition } from "./WorkflowDefinition.js";
import { WorkflowDependencyError } from "./errors/workflow-errors.js";

/**
 * Planificador y validador de grafos dirigidos acíclicos (DAG) de workflows (Fase 18).
 */
export class WorkflowPlanner {
  /**
   * Ordena topológicamente los pasos según sus dependencias.
   */
  public static planExecution(definition: WorkflowDefinition): WorkflowStepDefinition[] {
    const stepsMap = new Map<string, WorkflowStepDefinition>(definition.steps.map((s) => [s.id, s]));
    const inDegree = new Map<string, number>();
    const graph = new Map<string, string[]>();

    for (const step of definition.steps) {
      inDegree.set(step.id, step.dependsOn.length);
      for (const dep of step.dependsOn) {
        if (!stepsMap.has(dep)) {
          throw new WorkflowDependencyError(step.id, dep);
        }
        let list = graph.get(dep);
        if (!list) {
          list = [];
          graph.set(dep, list);
        }
        list.push(step.id);
      }
    }

    const queue: string[] = [];
    for (const [id, deg] of inDegree.entries()) {
      if (deg === 0) queue.push(id);
    }
    queue.sort();

    const ordered: WorkflowStepDefinition[] = [];
    while (queue.length > 0) {
      const currId = queue.shift()!;
      ordered.push(stepsMap.get(currId)!);

      const dependents = graph.get(currId) ?? [];
      for (const depId of dependents) {
        const newDeg = inDegree.get(depId)! - 1;
        inDegree.set(depId, newDeg);
        if (newDeg === 0) {
          queue.push(depId);
          queue.sort();
        }
      }
    }

    if (ordered.length !== definition.steps.length) {
      throw new Error(`Cycle or unreachable steps detected in workflow '${definition.id}'`);
    }

    return ordered;
  }
}
