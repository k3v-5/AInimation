/**
 * Interfaz fundamental para desacoplar el almacenamiento de datos del Runtime (Fase 18).
 */
export interface StorageAdapter {
  read(key: string): Promise<Uint8Array | null>;
  write(key: string, data: Uint8Array): Promise<void>;
  delete(key: string): Promise<void>;
  exists(key: string): Promise<boolean>;
  list(prefix?: string): Promise<string[]>;
}
