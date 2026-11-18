/**
 * REQ-030 §34: Excepciones de Bloqueo Pre-Exportación
 */

export class EditorialExportBlockedError extends Error {
  public readonly status: string;
  public readonly blockingCount: number;
  public readonly findingIds: string[];

  constructor(params: {
    status: string;
    blockingCount: number;
    findingIds: string[];
    message?: string;
  }) {
    super(
      params.message ||
        `[EDITORIAL_EXPORT_BLOCKED] La producción no puede exportarse en estado '${params.status}' con ${params.blockingCount} hallazgos BLOCKING (${params.findingIds.join(", ")}).`
    );
    this.name = "EditorialExportBlockedError";
    this.status = params.status;
    this.blockingCount = params.blockingCount;
    this.findingIds = params.findingIds;
  }
}
