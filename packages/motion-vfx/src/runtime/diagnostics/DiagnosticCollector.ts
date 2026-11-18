import { Diagnostic } from "../types.js";

export { Diagnostic };

/**
 * Colector de diagnósticos y métricas de advertencia en tiempo de ejecución (Fase 18).
 */
export class DiagnosticCollector {
  private diagnostics: Diagnostic[] = [];

  public add(diag: Diagnostic): void {
    this.diagnostics.push(diag);
  }

  public error(code: string, message: string, path?: string, context?: Record<string, unknown>): void {
    this.add({ severity: "error", code, message, path, context });
  }

  public warning(code: string, message: string, path?: string, context?: Record<string, unknown>): void {
    this.add({ severity: "warning", code, message, path, context });
  }

  public info(code: string, message: string, path?: string, context?: Record<string, unknown>): void {
    this.add({ severity: "info", code, message, path, context });
  }

  public getAll(): Diagnostic[] {
    return [...this.diagnostics];
  }

  public hasErrors(): boolean {
    return this.diagnostics.some((d) => d.severity === "error");
  }

  public clear(): void {
    this.diagnostics = [];
  }
}
