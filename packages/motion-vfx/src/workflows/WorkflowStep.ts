import { WorkflowContext } from "./WorkflowContext.js";

export type StepHandler = (context: WorkflowContext, parameters?: Record<string, unknown>) => Promise<unknown>;

/**
 * Registro de manejadores de pasos ejecutables para workflows (Fase 18).
 */
export class StepRegistry {
  private static handlers = new Map<string, StepHandler>();

  public static register(type: string, handler: StepHandler): void {
    this.handlers.set(type, handler);
  }

  public static get(type: string): StepHandler | undefined {
    return this.handlers.get(type);
  }

  public static has(type: string): boolean {
    return this.handlers.has(type);
  }
}
