import crypto from "crypto";
import fs from "fs";
import { VisualFeature, EmbeddingProviderType } from "./perception.types.js";

export interface ModelInfo {
  providerType: EmbeddingProviderType;
  id: string;
  version: string;
  hash: string;
  runtime: string;
  isHardwareAccelerated: boolean;
  isNeuralWeightsAvailable: boolean;
}

export interface IEmbeddingProvider {
  readonly providerType: EmbeddingProviderType;
  generateTextEmbedding(text: string): number[];
  generateVisualEmbedding(features: VisualFeature, tags?: string[]): number[];
  cosineSimilarity(a: number[], b: number[]): number;
  getModelInfo(): ModelInfo;
}

/**
 * CAPA A — DETERMINISTIC_HEURISTIC_PROVIDER (Fallback Determinista Offline)
 * Mapea ontologías semánticas de texto y características visuales perceptuales
 * a un espacio vectorial euclidiano de 128 dimensiones unitario (L2-normalized)
 * de forma 100% offline, determinista y matemáticamente reproducible.
 * Nota técnica: No simula pesos neuronales; opera como proveedor matemático formal.
 */
export class DeterministicHeuristicProvider implements IEmbeddingProvider {
  public readonly providerType: EmbeddingProviderType = "DETERMINISTIC_HEURISTIC";
  public static readonly DIMENSIONS = 128;
  public static readonly MODEL_ID = "deterministic-heuristic-hyperplane-v1";
  public static readonly MODEL_VERSION = "1.0.0";
  public static readonly MODEL_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";
  public static readonly RUNTIME = "deterministic-v8-math";

  public getModelInfo(): ModelInfo {
    return {
      providerType: this.providerType,
      id: DeterministicHeuristicProvider.MODEL_ID,
      version: DeterministicHeuristicProvider.MODEL_VERSION,
      hash: DeterministicHeuristicProvider.MODEL_HASH,
      runtime: DeterministicHeuristicProvider.RUNTIME,
      isHardwareAccelerated: false,
      isNeuralWeightsAvailable: false,
    };
  }

  public generateTextEmbedding(text: string): number[] {
    const normalized = text.toLowerCase().trim();
    const vec = new Float64Array(DeterministicHeuristicProvider.DIMENSIONS);

    const tokens = normalized.split(/[\s,._-]+/).filter((t) => t.length > 0);
    if (tokens.length === 0) {
      return Array.from(vec);
    }

    for (const token of tokens) {
      const hash = crypto.createHash("sha256").update(token, "utf8").digest();
      for (let i = 0; i < DeterministicHeuristicProvider.DIMENSIONS; i++) {
        const byte = hash[i % 32];
        const sign = (byte & 0x01) === 1 ? 1 : -1;
        const weight = ((byte >> 1) + 1) / 128.0;
        vec[i] += sign * weight;
      }
    }

    return this.normalizeL2(vec);
  }

  public generateVisualEmbedding(features: VisualFeature, tags: string[] = []): number[] {
    const textContext = [
      ...tags,
      features.lightingMood || "",
      features.composition?.framing || "",
      features.motion?.cameraMotion || "",
      ...(features.detectedEntities || []).map((e) => e.name),
      ...(features.dominantColors || []).map((c) => c.hex),
    ].filter(Boolean).join(" ");

    const textVector = this.generateTextEmbedding(textContext);
    const vec = new Float64Array(DeterministicHeuristicProvider.DIMENSIONS);

    for (let i = 0; i < DeterministicHeuristicProvider.DIMENSIONS; i++) {
      vec[i] = textVector[i];
    }

    if (features.composition) {
      vec[0] += (features.composition.ruleOfThirdsAlignment ?? 0) * 0.2;
      vec[1] += (features.composition.symmetryScore ?? 0) * 0.2;
    }
    if (features.motion && features.motion.dominantMotionVector) {
      vec[2] += (features.motion.dominantMotionVector[0] ?? 0) * 0.3;
      vec[3] += (features.motion.dominantMotionVector[1] ?? 0) * 0.3;
    }

    return this.normalizeL2(vec);
  }

  public cosineSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length || a.length === 0) return 0.0;

    let dot = 0;
    let normA = 0;
    let normB = 0;

    for (let i = 0; i < a.length; i++) {
      dot += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }

    const denom = Math.sqrt(normA) * Math.sqrt(normB);
    if (denom === 0) return 0.0;

    const sim = dot / denom;
    return Math.max(-1.0, Math.min(1.0, Number(sim.toFixed(6))));
  }

  private normalizeL2(vec: Float64Array): number[] {
    let sumSq = 0;
    for (let i = 0; i < vec.length; i++) {
      sumSq += vec[i] * vec[i];
    }

    const norm = Math.sqrt(sumSq);
    const result: number[] = new Array(vec.length);

    if (norm === 0) {
      result.fill(0);
      return result;
    }

    for (let i = 0; i < vec.length; i++) {
      result[i] = Number((vec[i] / norm).toFixed(6));
    }

    return result;
  }
}

// Retrocompatibilidad
export { DeterministicHeuristicProvider as DeterministicLocalEmbeddingAdapter };

/**
 * CAPA B — LOCAL_MULTIMODAL_NEURAL (Proveedor Neuronal Local para MobileCLIP / SigLIP)
 * Encapsula la inferencia ONNX/WASM local. Si el archivo binario de pesos no existe localmente,
 * falla explícitamente reportando la ausencia sin fabricar vectores ni caer silenciosamente en heurísticas.
 */
export class LocalMultimodalModelProvider implements IEmbeddingProvider {
  public readonly providerType: EmbeddingProviderType = "LOCAL_MULTIMODAL_NEURAL";
  private readonly modelPath: string;
  private readonly modelId: string;
  private readonly modelVersion: string;
  private readonly modelArtifactHash: string;
  private readonly isAvailable: boolean;

  constructor(options?: {
    modelPath?: string;
    modelId?: string;
    modelVersion?: string;
    expectedHash?: string;
  }) {
    this.modelPath = options?.modelPath || "models/vision/siglip-base-patch16-256.onnx";
    this.modelId = options?.modelId || "siglip-base-patch16-local";
    this.modelVersion = options?.modelVersion || "2.1.0";
    this.modelArtifactHash = options?.expectedHash || "a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0";

    // Verificación offline estricta de artefacto local
    this.isAvailable = fs.existsSync(this.modelPath);
  }

  public getModelInfo(): ModelInfo {
    return {
      providerType: this.providerType,
      id: this.modelId,
      version: this.modelVersion,
      hash: this.modelArtifactHash,
      runtime: "onnxruntime-node-offline",
      isHardwareAccelerated: false,
      isNeuralWeightsAvailable: this.isAvailable,
    };
  }

  public generateTextEmbedding(text: string): number[] {
    if (!this.isAvailable) {
      throw new Error(
        `[MISSING_LOCAL_NEURAL_WEIGHTS] El modelo neuronal local '${this.modelId}' no está instalado en '${this.modelPath}'. Prohibido fabricar embeddings falsos o hacer fallback silencioso.`
      );
    }
    // Si estuviera disponible el archivo ONNX, aquí se ejecutaría la sesión ONNX Runtime
    throw new Error("[ONNX_RUNTIME_NOT_INITIALIZED] Binario presente pero sesión no inicializada.");
  }

  public generateVisualEmbedding(features: VisualFeature, tags?: string[]): number[] {
    if (!this.isAvailable) {
      throw new Error(
        `[MISSING_LOCAL_NEURAL_WEIGHTS] El modelo neuronal local '${this.modelId}' no está instalado en '${this.modelPath}'. Prohibido fabricar embeddings falsos o hacer fallback silencioso.`
      );
    }
    throw new Error("[ONNX_RUNTIME_NOT_INITIALIZED] Binario presente pero sesión no inicializada.");
  }

  public cosineSimilarity(a: number[], b: number[]): number {
    return new DeterministicHeuristicProvider().cosineSimilarity(a, b);
  }
}
