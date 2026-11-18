/**
 * Motor de cálculo de similitud vectorial y búsqueda semántica multimodal (Fase 6).
 */
export class EmbeddingService {
  /**
   * Calcula la similitud coseno entre dos vectores normalizados en el rango [-1, 1] o [0, 1].
   */
  public static cosineSimilarity(a: number[], b: number[]): number {
    if (a.length === 0 || b.length === 0 || a.length !== b.length) {
      return 0;
    }

    let dot = 0;
    let normA = 0;
    let normB = 0;

    for (let i = 0; i < a.length; i++) {
      dot += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }

    const denom = Math.sqrt(normA) * Math.sqrt(normB);
    return denom > 0 ? dot / denom : 0;
  }

  /**
   * Simula o genera un vector sintético determinista a partir de un texto para propósitos de prueba/mock.
   */
  public static generateDeterministicMockVector(text: string, dimensions = 8): number[] {
    const vec: number[] = [];
    for (let i = 0; i < dimensions; i++) {
      let sum = 0;
      for (let c = 0; c < text.length; c++) {
        sum += text.charCodeAt(c) * (i + 1) * (c + 1);
      }
      vec.push(Math.sin(sum));
    }
    // Normalizar a vector unitario
    const norm = Math.sqrt(vec.reduce((acc, v) => acc + v * v, 0));
    return norm > 0 ? vec.map((v) => v / norm) : vec;
  }
}
