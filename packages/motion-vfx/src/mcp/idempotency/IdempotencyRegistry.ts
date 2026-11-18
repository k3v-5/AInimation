import { MCPResponseEnvelope } from "../types/index.js";

/**
 * Registro de idempotencia y deduplicación de reintentos de red (REQ-009, REQ-011).
 * Almacena respuestas previas por `operation_id` para garantizar que la re-ejecución devuelva el resultado
 * original sin generar duplicados de capas o mutaciones laterales.
 */
export class IdempotencyRegistry {
  private cache: Map<string, { response: MCPResponseEnvelope; timestamp: number }> = new Map();
  private maxCacheSize = 1000;

  /**
   * Comprueba si una operación ya fue ejecutada y retorna su respuesta en caché.
   */
  public get(operationId: string): MCPResponseEnvelope | undefined {
    const cached = this.cache.get(operationId);
    return cached ? cached.response : undefined;
  }

  /**
   * Registra la respuesta de una operación ejecutada.
   */
  public set(operationId: string, response: MCPResponseEnvelope): void {
    if (this.cache.size >= this.maxCacheSize) {
      const oldestKey = this.cache.keys().next().value;
      if (oldestKey) this.cache.delete(oldestKey);
    }

    this.cache.set(operationId, {
      response,
      timestamp: Date.now(),
    });
  }

  /**
   * Limpia el registro de idempotencia.
   */
  public clear(): void {
    this.cache.clear();
  }
}
