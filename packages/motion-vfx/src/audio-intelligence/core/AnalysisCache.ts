import { AnalysisMetadata, AudioAnalysis } from "../types/index.js";

/**
 * Cache determinista y versionado de análisis acústicos pesados (Fase 5I).
 */
export class AnalysisCache {
  private static cache = new Map<string, AudioAnalysis>();

  private static generateKey(metadata: AnalysisMetadata): string {
    return `${metadata.sourceHash}:${metadata.settingsHash}:${metadata.analyzerVersion}`;
  }

  public static set(analysis: AudioAnalysis): void {
    if (!analysis.metadata) return;
    const key = this.generateKey(analysis.metadata);
    this.cache.set(key, analysis);
  }

  public static get(metadata: AnalysisMetadata): AudioAnalysis | undefined {
    const key = this.generateKey(metadata);
    return this.cache.get(key);
  }

  public static has(metadata: AnalysisMetadata): boolean {
    const key = this.generateKey(metadata);
    return this.cache.has(key);
  }

  public static clear(): void {
    this.cache.clear();
  }

  public static get size(): number {
    return this.cache.size;
  }
}
