import * as crypto from "crypto";
import { CapabilityReport } from "./CapabilityMatrix.js";

export interface ExportManifestFile {
  name: string;
  relativePath: string;
  byteSize: number;
  sha256: string;
}

export interface ExportManifest {
  exporter: string;
  exporterVersion: string;
  sourceIRVersion: string;
  projectId: string;
  revisionId: string;
  deterministicHash: string;
  files: ExportManifestFile[];
  capabilityReport: CapabilityReport;
  warnings: string[];
  generatedAt?: string;
}

/**
 * Generador determinista de manifiestos y cálculo criptográfico de hashes (Fase 17).
 */
export class ExportManifestBuilder {
  /**
   * Serializa cualquier objeto a una cadena JSON canónica con claves ordenadas alfabéticamente.
   */
  public static canonicalize(obj: any): string {
    if (obj === null || typeof obj !== "object") {
      return JSON.stringify(obj);
    }

    if (Array.isArray(obj)) {
      return "[" + obj.map((item) => this.canonicalize(item)).join(",") + "]";
    }

    const sortedKeys = Object.keys(obj).sort();
    const entries = sortedKeys
      .filter((k) => obj[k] !== undefined && k !== "generatedAt" && k !== "timestamp") // Excluir campos temporales volátiles
      .map((k) => `${JSON.stringify(k)}:${this.canonicalize(obj[k])}`);

    return "{" + entries.join(",") + "}";
  }

  /**
   * Calcula el hash SHA-256 de una cadena o buffer.
   */
  public static sha256(content: string | Buffer): string {
    return crypto.createHash("sha256").update(content).digest("hex");
  }

  /**
   * Construye un ExportManifest determinista.
   */
  public static buildManifest(params: {
    exporter: string;
    exporterVersion: string;
    sourceIRVersion: string;
    projectId: string;
    revisionId: string;
    exportedContent: string | Buffer;
    primaryFileName: string;
    capabilityReport: CapabilityReport;
    warnings?: string[];
  }): ExportManifest {
    const fileBuffer =
      typeof params.exportedContent === "string"
        ? Buffer.from(params.exportedContent, "utf8")
        : params.exportedContent;

    const fileHash = this.sha256(fileBuffer);

    // Hash canónico del contenido + configuración del exporter
    const deterministicInput = this.canonicalize({
      exporter: params.exporter,
      exporterVersion: params.exporterVersion,
      sourceIRVersion: params.sourceIRVersion,
      projectId: params.projectId,
      revisionId: params.revisionId,
      fileHash,
      capabilityReport: params.capabilityReport,
    });

    const deterministicHash = this.sha256(deterministicInput);

    return {
      exporter: params.exporter,
      exporterVersion: params.exporterVersion,
      sourceIRVersion: params.sourceIRVersion,
      projectId: params.projectId,
      revisionId: params.revisionId,
      deterministicHash,
      files: [
        {
          name: params.primaryFileName,
          relativePath: params.primaryFileName,
          byteSize: fileBuffer.length,
          sha256: fileHash,
        },
      ],
      capabilityReport: params.capabilityReport,
      warnings: params.warnings ?? [],
      generatedAt: new Date().toISOString(),
    };
  }
}
