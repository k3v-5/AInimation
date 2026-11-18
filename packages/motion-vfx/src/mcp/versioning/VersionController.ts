import { MCPStructuredError } from "../types/index.js";
import { MCPErrorCatalog } from "../errors/MCPErrorCatalog.js";

/**
 * Controlador de versionado optimista para control de concurrencia y prevención de sobreescrituras (REQ-010).
 */
export class VersionController {
  private currentVersion: number;

  constructor(initialVersion = 1) {
    this.currentVersion = Math.max(1, initialVersion);
  }

  public getVersion(): number {
    return this.currentVersion;
  }

  /**
   * Valida si la versión esperada por el agente coincide con la versión actual del proyecto.
   */
  public checkVersion(expectedVersion?: number): { valid: boolean; error?: MCPStructuredError } {
    if (expectedVersion === undefined) {
      return { valid: true };
    }

    if (expectedVersion !== this.currentVersion) {
      return {
        valid: false,
        error: MCPErrorCatalog.create(
          "VERSION_CONFLICT",
          `Optimistic concurrency conflict: expected version ${expectedVersion} but current project version is ${this.currentVersion}.`,
          {
            context: {
              expectedVersion,
              currentVersion: this.currentVersion,
            },
          }
        ),
      };
    }

    return { valid: true };
  }

  /**
   * Incrementa la versión monótonamente al commitear una transacción exitosa.
   */
  public advanceVersion(): number {
    this.currentVersion += 1;
    return this.currentVersion;
  }

  public setVersion(v: number): void {
    this.currentVersion = v;
  }
}
