import { Composition } from "../../core/composition.js";
import { TransactionSnapshot, MCPStructuredError } from "../types/index.js";
import { MCPErrorCatalog } from "../errors/MCPErrorCatalog.js";
import { createHash } from "node:crypto";

/**
 * Gestor de transacciones ACID y Rollback Criptográfico para el MCP (REQ-012, REQ-013, REQ-014).
 * Garantiza que si cualquier sub-operación falla, el estado de la IR se restaura exactamente
 * al snapshot inicial con idéntico hash SHA-256.
 */
export class TransactionManager {
  private activeTransactions: Map<string, TransactionSnapshot> = new Map();

  /**
   * Inicia una transacción tomando un snapshot inmutable de la composición.
   */
  public beginTransaction(
    transactionId: string,
    composition: Composition,
    version: number
  ): { success: boolean; snapshot?: TransactionSnapshot; error?: MCPStructuredError } {
    if (this.activeTransactions.has(transactionId)) {
      return {
        success: false,
        error: MCPErrorCatalog.create(
          "TRANSACTION_ABORTED",
          `Transaction '${transactionId}' is already active.`
        ),
      };
    }

    const hash = this.computeHash(composition);
    const snapshot: TransactionSnapshot = {
      transactionId,
      initialVersion: version,
      initialHash: hash,
      compositionSnapshot: this.cloneComposition(composition),
      operationsLog: [],
      status: "active",
    };

    this.activeTransactions.set(transactionId, snapshot);
    return { success: true, snapshot };
  }

  /**
   * Clona una composición de forma segura.
   */
  public cloneComposition(comp: Composition): Composition {
    const cloned = new Composition({
      id: comp.id,
      name: comp.name,
      width: comp.width,
      height: comp.height,
      fps: comp.fps,
      duration: comp.duration,
    });
    for (const l of comp.getLayers()) {
      cloned.addLayer(l);
    }
    return cloned;
  }

  /**
   * Hace rollback estricto restaurando el snapshot inmutable.
   */
  public rollbackTransaction(transactionId: string): {
    success: boolean;
    restoredComposition?: Composition;
    restoredHash?: string;
    error?: MCPStructuredError;
  } {
    const tx = this.activeTransactions.get(transactionId);
    if (!tx) {
      return {
        success: false,
        error: MCPErrorCatalog.create(
          "TRANSACTION_ABORTED",
          `Cannot rollback: transaction '${transactionId}' not found.`
        ),
      };
    }

    const restoredComp = this.cloneComposition(tx.compositionSnapshot);
    const restoredHash = this.computeHash(restoredComp);

    // Invariante REQ-013: El hash restaurado debe coincidir exactamente con el hash inicial
    if (restoredHash !== tx.initialHash) {
      return {
        success: false,
        error: MCPErrorCatalog.create(
          "TRANSACTION_ABORTED",
          `Fatal integrity error: restored hash (${restoredHash}) does not match snapshot hash (${tx.initialHash}).`,
          { severity: "fatal", recoverable: false }
        ),
      };
    }

    tx.status = "rolled_back";
    this.activeTransactions.delete(transactionId);

    return {
      success: true,
      restoredComposition: restoredComp,
      restoredHash,
    };
  }

  /**
   * Commitea la transacción con éxito.
   */
  public commitTransaction(transactionId: string): { success: boolean; error?: MCPStructuredError } {
    const tx = this.activeTransactions.get(transactionId);
    if (!tx) {
      return {
        success: false,
        error: MCPErrorCatalog.create(
          "TRANSACTION_ABORTED",
          `Cannot commit: transaction '${transactionId}' not found.`
        ),
      };
    }

    tx.status = "committed";
    this.activeTransactions.delete(transactionId);
    return { success: true };
  }

  /**
   * Calcula el hash determinista SHA-256 de una composición.
   */
  public computeHash(comp: Composition): string {
    const snapshot = comp.evaluate(0);
    const json = JSON.stringify({
      id: comp.id,
      name: comp.name,
      width: comp.width,
      height: comp.height,
      fps: comp.fps,
      duration: comp.duration,
      layers: snapshot.layers,
      elements: snapshot.elements,
    });

    return createHash("sha256").update(json).digest("hex");
  }
}
