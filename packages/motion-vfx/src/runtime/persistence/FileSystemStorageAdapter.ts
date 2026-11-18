import * as fs from "node:fs/promises";
import * as path from "node:path";
import { AtomicWriteError, PersistenceError } from "../../errors/runtime-errors.js";
import { SecurityPathError } from "../../exporters/common/PathSanitizer.js";
import { StorageAdapter } from "./StorageAdapter.js";

/**
 * Adaptador de almacenamiento en disco con escrituras atómicas y confinamiento seguro (Fase 18).
 */
export class FileSystemStorageAdapter implements StorageAdapter {
  private readonly storageRoot: string;

  constructor(storageRoot: string) {
    if (!storageRoot) {
      throw new PersistenceError("storageRoot must be provided to FileSystemStorageAdapter.");
    }
    this.storageRoot = path.resolve(storageRoot);
  }

  public getStorageRoot(): string {
    return this.storageRoot;
  }

  public async read(key: string): Promise<Uint8Array | null> {
    const fullPath = this.resolveSafePath(key);
    try {
      const buffer = await fs.readFile(fullPath);
      return new Uint8Array(buffer);
    } catch (err: any) {
      if (err.code === "ENOENT") {
        return null;
      }
      throw new PersistenceError(`Failed to read file at '${key}': ${err.message}`, { key, error: err });
    }
  }

  /**
   * Escritura atómica: escribe en archivo temporal y renombra atómicamente al destino.
   */
  public async write(key: string, data: Uint8Array): Promise<void> {
    const targetPath = this.resolveSafePath(key);
    const parentDir = path.dirname(targetPath);

    try {
      await fs.mkdir(parentDir, { recursive: true });
    } catch (err: any) {
      throw new PersistenceError(`Failed to create parent directory '${parentDir}': ${err.message}`, { parentDir, error: err });
    }

    const tmpPath = `${targetPath}.tmp.${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;

    try {
      // 1. Escribir y sincronizar archivo temporal
      const fileHandle = await fs.open(tmpPath, "w");
      await fileHandle.writeFile(data);
      await fileHandle.sync();
      await fileHandle.close();

      // 2. Renombrar atómicamente a la ruta final
      await fs.rename(tmpPath, targetPath);
    } catch (err: any) {
      // Intentar limpiar archivo temporal si falló
      try {
        await fs.unlink(tmpPath);
      } catch {
        // Silenciar error secundario de limpieza
      }
      throw new AtomicWriteError(targetPath, err.message, { key, tmpPath, error: err });
    }
  }

  public async delete(key: string): Promise<void> {
    const targetPath = this.resolveSafePath(key);
    try {
      await fs.unlink(targetPath);
    } catch (err: any) {
      if (err.code !== "ENOENT") {
        throw new PersistenceError(`Failed to delete file at '${key}': ${err.message}`, { key, error: err });
      }
    }
  }

  public async exists(key: string): Promise<boolean> {
    const targetPath = this.resolveSafePath(key);
    try {
      await fs.access(targetPath);
      return true;
    } catch {
      return false;
    }
  }

  public async list(prefix?: string): Promise<string[]> {
    const results: string[] = [];

    const walk = async (currentDir: string, currentPrefix: string) => {
      let entries: string[];
      try {
        entries = await fs.readdir(currentDir);
      } catch (err: any) {
        if (err.code === "ENOENT") return;
        throw err;
      }

      for (const entry of entries) {
        const full = path.join(currentDir, entry);
        const rel = currentPrefix ? `${currentPrefix}/${entry}` : entry;
        const stat = await fs.stat(full);

        if (stat.isDirectory()) {
          await walk(full, rel);
        } else {
          if (!prefix || rel.startsWith(prefix)) {
            results.push(rel.replace(/\\/g, "/"));
          }
        }
      }
    };

    await walk(this.storageRoot, "");
    return results.sort();
  }

  /**
   * Resuelve y sanitiza la ruta relativa verificando confinamiento estricto en storageRoot.
   */
  private resolveSafePath(key: string): string {
    if (!key || typeof key !== "string") {
      throw new SecurityPathError("Storage key must be a non-empty string.");
    }

    // Normalizar separadores y resolver de forma absoluta
    const normalizedKey = key.replace(/\\/g, "/");
    if (normalizedKey.includes("\0") || normalizedKey.includes("%2e%2e")) {
      throw new SecurityPathError(`Path contains forbidden characters: ${key}`);
    }

    const resolved = path.resolve(this.storageRoot, normalizedKey);
    const rootWithSep = this.storageRoot.endsWith(path.sep) ? this.storageRoot : this.storageRoot + path.sep;

    if (!resolved.startsWith(rootWithSep) && resolved !== this.storageRoot) {
      throw new SecurityPathError(`Path traversal attempt detected: '${key}' resolved outside storageRoot '${this.storageRoot}'`);
    }

    return resolved;
  }
}
