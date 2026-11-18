import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { MediaFingerprint } from "../contracts/ingestion.types.js";

/**
 * Calculador determinista de huellas criptográficas y hashes para medios audiovisuales.
 */
export class MediaHasher {
  /**
   * Calcula el hash SHA-256 de un buffer en memoria de forma determinista.
   */
  public static hashBuffer(buffer: Buffer | Uint8Array): string {
    return crypto.createHash("sha256").update(buffer).digest("hex");
  }

  /**
   * Calcula el hash SHA-256 de un archivo en disco mediante streaming.
   * Evita cargar archivos grandes de video completos en RAM.
   */
  public static async hashFileStream(filePath: string): Promise<string> {
    return new Promise((resolve, reject) => {
      const hash = crypto.createHash("sha256");
      const stream = fs.createReadStream(filePath);

      stream.on("data", (chunk) => hash.update(chunk));
      stream.on("end", () => resolve(hash.digest("hex")));
      stream.on("error", (err) => reject(err));
    });
  }

  /**
   * Genera un ID de activo estable y determinista a partir de su hash SHA-256.
   * No depende de inodes de filesystem, mtime, ni del orden de ingestión.
   */
  public static generateStableAssetId(checksumSha256: string): string {
    return `asset_${checksumSha256.substring(0, 16)}`;
  }

  /**
   * Genera una huella digital determinista completa a partir del archivo y sus metadatos.
   */
  public static generateFingerprint(
    checksumSha256: string,
    sizeBytes: number,
    lastModifiedTimestamp: number,
    durationSeconds?: number,
    width?: number,
    height?: number,
    fps?: number
  ): MediaFingerprint {
    return {
      checksumSha256,
      sizeBytes,
      lastModifiedTimestamp,
      durationSeconds: durationSeconds !== undefined ? Number(durationSeconds.toFixed(4)) : undefined,
      width,
      height,
      fps: fps !== undefined ? Number(fps.toFixed(2)) : undefined,
    };
  }
}
