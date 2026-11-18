/**
 * Implementación eficiente de caché LRU (Least Recently Used) para recursos de runtime (Fase 5A).
 */
export class LRUCache<K, V> {
  private cache = new Map<K, V>();
  public readonly maxSize: number;

  constructor(maxSize = 100) {
    this.maxSize = Math.max(1, maxSize);
  }

  public get(key: K): V | undefined {
    if (!this.cache.has(key)) return undefined;

    // Re-insertar al final para marcar como recientemente usado
    const value = this.cache.get(key)!;
    this.cache.delete(key);
    this.cache.set(key, value);
    return value;
  }

  public set(key: K, value: V): void {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    } else if (this.cache.size >= this.maxSize) {
      // Eliminar el elemento menos recientemente usado (primer elemento del Map)
      const oldestKey = this.cache.keys().next().value;
      if (oldestKey !== undefined) {
        this.cache.delete(oldestKey);
      }
    }
    this.cache.set(key, value);
  }

  public has(key: K): boolean {
    return this.cache.has(key);
  }

  public delete(key: K): boolean {
    return this.cache.delete(key);
  }

  public clear(): void {
    this.cache.clear();
  }

  public get size(): number {
    return this.cache.size;
  }
}
