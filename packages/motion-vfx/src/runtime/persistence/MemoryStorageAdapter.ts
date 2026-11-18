import { StorageAdapter } from "./StorageAdapter.js";

/**
 * Adaptador de almacenamiento en memoria volátil de alta velocidad (Fase 18).
 */
export class MemoryStorageAdapter implements StorageAdapter {
  private store = new Map<string, Uint8Array>();

  public async read(key: string): Promise<Uint8Array | null> {
    const data = this.store.get(key);
    if (!data) return null;
    return new Uint8Array(data); // Retornar copia defensiva
  }

  public async write(key: string, data: Uint8Array): Promise<void> {
    this.store.set(key, new Uint8Array(data)); // Almacenar copia defensiva
  }

  public async delete(key: string): Promise<void> {
    this.store.delete(key);
  }

  public async exists(key: string): Promise<boolean> {
    return this.store.has(key);
  }

  public async list(prefix?: string): Promise<string[]> {
    const keys = Array.from(this.store.keys());
    if (!prefix) return keys.sort();
    return keys.filter((k) => k.startsWith(prefix)).sort();
  }

  public clear(): void {
    this.store.clear();
  }
}
