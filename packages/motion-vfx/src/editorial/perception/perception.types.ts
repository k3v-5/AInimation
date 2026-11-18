import { z } from "zod";

/**
 * REQ-013 §4: Perceptual Visual Features
 */
export interface VisualComposition {
  framing: "WIDE" | "MEDIUM" | "CLOSE_UP" | "EXTREME_CLOSE";
  ruleOfThirdsAlignment: number; // 0.0 a 1.0
  symmetryScore: number; // 0.0 a 1.0
  depthOfField: "SHALLOW" | "DEEP";
}

export interface MotionCharacteristics {
  cameraMotion: "STATIC" | "PAN" | "TILT" | "DOLLY" | "ZOOM" | "HANDHELD" | "TRACKING";
  motionSpeed: "STILL" | "SLOW" | "MODERATE" | "FAST" | "ERRATIC";
  dominantMotionVector: [number, number]; // [dx, dy] normalizado
}

export interface DominantColor {
  hex: string;
  percentage: number;
}

export interface DetectedEntity {
  name: string;
  category: "PERSON" | "OBJECT" | "ANIMAL" | "VEHICLE" | "ARCHITECTURE" | "NATURE";
  confidence: number;
  boundingBox?: [number, number, number, number]; // [ymin, xmin, ymax, xmax]
}

export interface VisualFeature {
  dominantColors: DominantColor[];
  motion: MotionCharacteristics;
  composition: VisualComposition;
  detectedEntities: DetectedEntity[];
  lightingMood: "DAYLIGHT" | "NIGHT" | "GOLDEN_HOUR" | "DRAMATIC_LOW_KEY" | "HIGH_KEY";
}

/**
 * Registro de Plano Indexado en el Espacio Multimodal
 */
export type EmbeddingProviderType = "DETERMINISTIC_HEURISTIC" | "LOCAL_MULTIMODAL_NEURAL";

export interface ShotIndexRecord {
  shotId: string;
  sourceAssetId: string;
  sourceAssetHash: string;
  startTimeSeconds: number;
  durationSeconds: number;
  visualFeatures: VisualFeature;
  detectedSubjects: string[];
  transcriptText?: string;
  embedding: number[]; // Vector normalizado L2
  modelProvenance: {
    providerType: EmbeddingProviderType;
    modelId: string;
    modelVersion: string;
    modelHash: string;
    runtime: string;
  };
}

/**
 * Manifiesto del Índice Persistente Local
 */
export interface PersistentIndexManifest {
  schemaVersion: "4.0.0";
  providerType: EmbeddingProviderType;
  modelId: string;
  modelVersion: string;
  modelHash: string;
  runtime: string;
  indexVersion: string;
  assetCount: number;
  shotCount: number;
  sourceAssetHashes: Record<string, string>;
  configurationHash: string;
  canonicalIndexHash: string;
}

/**
 * Desglose Estructurado de Explicabilidad de la Búsqueda Semántica
 */
export interface SemanticExplanationBreakdown {
  semanticSimilarity: number;
  visualSubjectMatch: number;
  sceneContextMatch: number;
  colorMatch: number;
  motionMatch: number;
  transcriptMatch: number;
  summary: string;
}

export interface SemanticSearchResult {
  shotId: string;
  sourceAssetId: string;
  score: number; // [0.0, 100.0]
  startTimeSeconds: number;
  durationSeconds: number;
  matchingFeatures: string[];
  explanation: SemanticExplanationBreakdown;
}
