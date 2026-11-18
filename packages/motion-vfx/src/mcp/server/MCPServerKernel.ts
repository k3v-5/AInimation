import { Composition } from "../../core/composition.js";
import { MCPRequestEnvelope, MCPResponseEnvelope } from "../types/index.js";
import { PermissionManager } from "../permissions/PermissionManager.js";
import { VersionController } from "../versioning/VersionController.js";
import { IdempotencyRegistry } from "../idempotency/IdempotencyRegistry.js";
import { TransactionManager } from "../transactions/TransactionManager.js";
import { MCPErrorCatalog } from "../errors/MCPErrorCatalog.js";

export type MutationHandler = (comp: Composition, params: Record<string, unknown>) => void;

/**
 * Kernel Central del Servidor MCP Autónomo (Fase 3 Kernel MCP / REQ-001 a REQ-022).
 * Orquesta el flujo de ejecución estricto:
 * Request -> Permisos -> Versionado -> Idempotencia -> Transacción -> Mutación IR -> Commit/Rollback -> Respuesta.
 */
export class MCPServerKernel {
  public readonly versionController: VersionController;
  public readonly idempotencyRegistry: IdempotencyRegistry;
  public readonly transactionManager: TransactionManager;
  public composition: Composition;

  private mutationHandlers: Map<string, MutationHandler> = new Map();

  constructor(initialComp?: Composition, initialVersion = 1) {
    this.composition =
      initialComp ??
      new Composition({
        name: "mcp_main_comp",
        width: 1080,
        height: 1920,
        fps: 60,
        duration: 30.0,
      });
    this.versionController = new VersionController(initialVersion);
    this.idempotencyRegistry = new IdempotencyRegistry();
    this.transactionManager = new TransactionManager();

    this.registerDefaultHandlers();
  }

  /**
   * Registra un manejador de mutación para una herramienta.
   */
  public registerMutationHandler(toolName: string, handler: MutationHandler): void {
    this.mutationHandlers.set(toolName, handler);
  }

  /**
   * Procesa una solicitud MCP a través de los 7 filtros de integridad del kernel.
   */
  public async handleRequest<T = Record<string, unknown>>(
    request: MCPRequestEnvelope<T>
  ): Promise<MCPResponseEnvelope> {
    // 1. Verificación de Seguridad y Permisos
    const permCheck = PermissionManager.validate(request.category, request.toolName, request.params);
    if (!permCheck.valid) {
      return {
        operationId: request.operationId,
        success: false,
        projectVersion: this.versionController.getVersion(),
        projectHash: this.transactionManager.computeHash(this.composition),
        error: permCheck.error,
      };
    }

    // 2. Verificación de Idempotencia (¿Ya ejecutado?)
    const cachedResponse = this.idempotencyRegistry.get(request.operationId);
    if (cachedResponse) {
      return cachedResponse;
    }

    // 3. Verificación de Versionado Optimista
    const versionCheck = this.versionController.checkVersion(request.expectedVersion);
    if (!versionCheck.valid) {
      return {
        operationId: request.operationId,
        success: false,
        projectVersion: this.versionController.getVersion(),
        projectHash: this.transactionManager.computeHash(this.composition),
        error: versionCheck.error,
      };
    }

    // 4. Modo Simulación (Dry-Run)
    if (request.dryRun) {
      return {
        operationId: request.operationId,
        success: true,
        projectVersion: this.versionController.getVersion(),
        projectHash: this.transactionManager.computeHash(this.composition),
        dryRunReport: {
          plannedChanges: 1,
          warnings: [],
          estimatedRenderTimeSec: 2.5,
        },
      };
    }

    // 5. Envolvente Transaccional
    const txId = request.transactionId ?? `tx_${request.operationId}`;
    const txBegin = this.transactionManager.beginTransaction(
      txId,
      this.composition,
      this.versionController.getVersion()
    );

    if (!txBegin.success) {
      return {
        operationId: request.operationId,
        success: false,
        projectVersion: this.versionController.getVersion(),
        projectHash: this.transactionManager.computeHash(this.composition),
        error: txBegin.error,
      };
    }

    try {
      // 6. Mutación de la IR Canónica
      const handler = this.mutationHandlers.get(request.toolName);
      if (!handler && request.category === "mutation") {
        throw new Error(`No mutation handler registered for tool '${request.toolName}'`);
      }

      if (handler) {
        handler(this.composition, request.params as Record<string, unknown>);
      }

      // 7. Commit Transaccional y Avance de Versión
      this.transactionManager.commitTransaction(txId);
      const newVersion = this.versionController.advanceVersion();
      const currentHash = this.transactionManager.computeHash(this.composition);

      const response: MCPResponseEnvelope = {
        operationId: request.operationId,
        success: true,
        projectVersion: newVersion,
        projectHash: currentHash,
        result: { status: "applied", tool: request.toolName },
      };

      // 8. Registro en caché de Idempotencia
      this.idempotencyRegistry.set(request.operationId, response);
      return response;

    } catch (err: unknown) {
      // 9. Rollback Criptográfico Automático ante Errores
      const rollback = this.transactionManager.rollbackTransaction(txId);
      if (rollback.restoredComposition) {
        this.composition = rollback.restoredComposition;
      }

      const structuredError = MCPErrorCatalog.create(
        "INVALID_OPERATION",
        `Mutation execution failed: ${err instanceof Error ? err.message : String(err)}`
      );

      return {
        operationId: request.operationId,
        success: false,
        projectVersion: this.versionController.getVersion(),
        projectHash: this.transactionManager.computeHash(this.composition),
        error: structuredError,
      };
    }
  }

  private registerDefaultHandlers(): void {
    // Handler por defecto para mutaciones genéricas
    this.registerMutationHandler("set_property", (comp, params) => {
      if (params.name && typeof params.name === "string") {
        comp.name = params.name;
      }
    });
  }
}
