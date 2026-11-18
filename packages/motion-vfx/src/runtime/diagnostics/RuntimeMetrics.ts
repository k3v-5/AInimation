export interface MetricSummary {
  count: number;
  min: number;
  max: number;
  mean: number;
  p50: number;
  p95: number;
  p99: number;
}

/**
 * Colector de métricas operacionales de latencia y rendimiento del Runtime (Fase 18).
 */
export class RuntimeMetrics {
  private static samples = new Map<string, number[]>();

  public static record(name: string, durationMs: number): void {
    if (!this.samples.has(name)) {
      this.samples.set(name, []);
    }
    const arr = this.samples.get(name)!;
    arr.push(durationMs);
    // Limitar muestras en memoria
    if (arr.length > 5000) {
      arr.shift();
    }
  }

  public static async time<T>(name: string, fn: () => Promise<T> | T): Promise<T> {
    const t0 = performance.now();
    try {
      return await fn();
    } finally {
      const duration = performance.now() - t0;
      this.record(name, duration);
    }
  }

  public static getSummary(name: string): MetricSummary | null {
    const arr = this.samples.get(name);
    if (!arr || arr.length === 0) return null;

    const sorted = [...arr].sort((a, b) => a - b);
    const count = sorted.length;
    const min = sorted[0];
    const max = sorted[count - 1];
    const sum = sorted.reduce((acc, val) => acc + val, 0);
    const mean = Number((sum / count).toFixed(2));

    const p50 = sorted[Math.floor(count * 0.5)];
    const p95 = sorted[Math.floor(count * 0.95)] ?? sorted[count - 1];
    const p99 = sorted[Math.floor(count * 0.99)] ?? sorted[count - 1];

    return {
      count,
      min: Number(min.toFixed(2)),
      max: Number(max.toFixed(2)),
      mean,
      p50: Number(p50.toFixed(2)),
      p95: Number(p95.toFixed(2)),
      p99: Number(p99.toFixed(2)),
    };
  }

  public static getAllSummaries(): Record<string, MetricSummary> {
    const result: Record<string, MetricSummary> = {};
    for (const key of this.samples.keys()) {
      const summary = this.getSummary(key);
      if (summary) {
        result[key] = summary;
      }
    }
    return result;
  }

  public static reset(): void {
    this.samples.clear();
  }
}
