import { ProjectEnvelopeFactory } from "./persistence/ProjectEnvelope.js";
import { StorageAdapter } from "./persistence/StorageAdapter.js";
import { JournalEntry } from "./types.js";

export interface RecoveryReport {
  projectId: string;
  recovered: boolean;
  recoveredFromTemp: boolean;
  cleanedTempFiles: string[];
  warnings: string[];
}

/**
 * Subsistema de recuperación ante interrupciones de proceso y fallos de I/O (Fase 18).
 */
export class ProjectRecovery {
  private storage: StorageAdapter;

  constructor(storage: StorageAdapter) {
    this.storage = storage;
  }

  /**
   * Inspecciona el estado de un proyecto en almacenamiento y se recupera de operaciones incompletas.
   */
  public async recoverProject(projectId: string): Promise<RecoveryReport> {
    const report: RecoveryReport = {
      projectId,
      recovered: false,
      recoveredFromTemp: false,
      cleanedTempFiles: [],
      warnings: [],
    };

    const projectPrefix = `projects/${projectId}/`;
    const allFiles = await this.storage.list(projectPrefix);

    const headKey = `${projectPrefix}project.json`;
    const headExists = await this.storage.exists(headKey);
    const tempFiles = allFiles.filter((f) => f.includes(".tmp."));

    let headValid = false;
    if (headExists) {
      try {
        const headData = await this.storage.read(headKey);
        if (headData) {
          const rawStr = new TextDecoder("utf-8").decode(headData);
          ProjectEnvelopeFactory.validate(JSON.parse(rawStr));
          headValid = true;
        }
      } catch (err: any) {
        report.warnings.push(`Head project.json was corrupted: ${err.message}`);
      }
    }

    // 1. Si head es válido, los archivos temporales son basura huérfana de un proceso interrumpido
    if (headValid) {
      for (const tmpFile of tempFiles) {
        await this.storage.delete(tmpFile);
        report.cleanedTempFiles.push(tmpFile);
      }
      report.recovered = true;
      return report;
    }

    // 2. Si head no es válido pero existe un archivo temporal válido, intentamos recuperar
    for (const tmpFile of tempFiles) {
      try {
        const tmpData = await this.storage.read(tmpFile);
        if (tmpData) {
          const rawStr = new TextDecoder("utf-8").decode(tmpData);
          const parsed = JSON.parse(rawStr);
          ProjectEnvelopeFactory.validate(parsed);

          // Archivo temporal válido -> Promover a head
          await this.storage.write(headKey, tmpData);
          await this.storage.delete(tmpFile);
          report.cleanedTempFiles.push(tmpFile);
          report.recovered = true;
          report.recoveredFromTemp = true;
          return report;
        }
      } catch {
        // Archivo temporal no recuperable
      }
    }

    return report;
  }

  /**
   * Registra una entrada en el Journal de operaciones.
   */
  public async logJournal(entry: JournalEntry): Promise<void> {
    const journalKey = `projects/${entry.projectId}/journals/${entry.operationId}.json`;
    const bytes = new TextEncoder().encode(JSON.stringify(entry));
    await this.storage.write(journalKey, bytes);
  }
}
