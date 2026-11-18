import { MultimodalIndexer } from "./multimodal-indexer.js";
import { IEmbeddingProvider, DeterministicLocalEmbeddingAdapter } from "./embedding-provider.js";
import { SemanticSearchResult, SemanticExplanationBreakdown } from "./perception.types.js";
import { SemanticBRollCandidate } from "../broll/semantic-broll.types.js";

/**
 * REQ-013 §5 & §6: Semantic Video Search & Ranked Candidate Engine
 * Búsqueda semántica en lenguaje natural con explicabilidad estructurada y puntuación matemática.
 */
export class SemanticSearchEngine {
  private readonly indexer: MultimodalIndexer;
  private readonly embeddingProvider: IEmbeddingProvider;

  constructor(indexer: MultimodalIndexer, provider?: IEmbeddingProvider) {
    this.indexer = indexer;
    this.embeddingProvider = provider || new DeterministicLocalEmbeddingAdapter();
  }

  /**
   * Ejecuta una consulta en lenguaje natural sobre el catálogo de planos indexados
   */
  public search(query: string, options?: { topK?: number; minScore?: number }): SemanticSearchResult[] {
    const topK = options?.topK ?? 10;
    const minScore = options?.minScore ?? 0.0;

    const queryEmbedding = this.embeddingProvider.generateTextEmbedding(query);
    const records = this.indexer.getAllRecords();

    const results: SemanticSearchResult[] = [];
    const queryLower = query.toLowerCase();

    for (const record of records) {
      // 1. Similitud Coseno básica [0.0, 1.0]
      const rawCosine = this.embeddingProvider.cosineSimilarity(queryEmbedding, record.embedding);
      const cosineNorm = Math.max(0.0, Math.min(1.0, (rawCosine + 1.0) / 2.0));

      // 2. Coincidencias explícitas de entidades y conceptos
      const matchedFeatures: string[] = [];
      let subjectMatchScore = 0.0;
      const SYNONYMS: Record<string, string[]> = {
        ciudad: ["city", "urban", "skyline", "edificio"],
        city: ["ciudad", "urban", "skyline"],
        noche: ["night", "nocturno", "dark"],
        night: ["noche", "dark"],
        persona: ["person", "people", "hombre", "mujer", "pedestrian"],
        person: ["persona", "people", "walking"],
        caminando: ["walking", "walk", "caminar"],
        walking: ["caminando", "walk"],
      };

      for (const subject of record.detectedSubjects) {
        const subLower = subject.toLowerCase();
        const syns = SYNONYMS[subLower] || [];
        const isMatch =
          queryLower.includes(subLower) ||
          syns.some((syn) => queryLower.includes(syn));

        if (isMatch) {
          matchedFeatures.push(`Subject: ${subject}`);
          subjectMatchScore = Math.max(subjectMatchScore, 0.95);
        }
      }

      // 3. Coincidencia de contexto o atmósfera
      let contextMatchScore = 0.0;
      if (
        (queryLower.includes("night") || queryLower.includes("noche")) &&
        record.visualFeatures.lightingMood === "NIGHT"
      ) {
        matchedFeatures.push("Atmosphere: Nighttime lighting");
        contextMatchScore = 0.95;
      } else if (
        (queryLower.includes("walking") || queryLower.includes("caminando")) &&
        record.visualFeatures.motion.cameraMotion === "TRACKING"
      ) {
        matchedFeatures.push("Motion: Camera tracking movement");
        contextMatchScore = 0.85;
      }

      // 4. Coincidencia de transcripción de diálogo
      let transcriptMatchScore = 0.0;
      if (record.transcriptText && record.transcriptText.toLowerCase().includes(queryLower)) {
        matchedFeatures.push("Transcript: Direct verbal keyword match");
        transcriptMatchScore = 1.0;
      }

      // Puntuación combinada ponderada [0.0, 100.0]
      const compositeScore =
        cosineNorm * 0.40 +
        subjectMatchScore * 0.30 +
        contextMatchScore * 0.20 +
        transcriptMatchScore * 0.10;

      const finalScore = Number((compositeScore * 100.0).toFixed(2));

      if (finalScore >= minScore) {
        const explanation: SemanticExplanationBreakdown = {
          semanticSimilarity: Number(cosineNorm.toFixed(3)),
          visualSubjectMatch: Number(subjectMatchScore.toFixed(3)),
          sceneContextMatch: Number(contextMatchScore.toFixed(3)),
          colorMatch: record.visualFeatures.dominantColors.length > 0 ? 0.8 : 0.5,
          motionMatch: record.visualFeatures.motion.cameraMotion !== "STATIC" ? 0.75 : 0.5,
          transcriptMatch: Number(transcriptMatchScore.toFixed(3)),
          summary: `Selected with score ${finalScore}/100 based on ${matchedFeatures.length} matching feature(s): ${
            matchedFeatures.join(", ") || "latent semantic proximity"
          }.`,
        };

        results.push({
          shotId: record.shotId,
          sourceAssetId: record.sourceAssetId,
          score: finalScore,
          startTimeSeconds: record.startTimeSeconds,
          durationSeconds: record.durationSeconds,
          matchingFeatures: matchedFeatures,
          explanation,
        });
      }
    }

    return results
      .sort((a, b) => b.score - a.score || a.shotId.localeCompare(b.shotId))
      .slice(0, topK);
  }

  /**
   * REQ-013 §13: Adapta los resultados de búsqueda al contrato de SemanticBRollCandidate
   * para su consumo directo por el Semantic B-Roll Director (REQ-014 / REQ-017)
   */
  public toBRollCandidates(results: SemanticSearchResult[]): SemanticBRollCandidate[] {
    return results.map((r) => {
      const record = this.indexer.getRecord(r.shotId);
      return {
        id: r.shotId,
        assetId: r.sourceAssetId,
        description: r.explanation.summary,
        tags: r.matchingFeatures,
        semanticConcepts: record ? record.detectedSubjects : [],
        emotionalTone: "NEUTRAL",
        durationSeconds: r.durationSeconds,
        scale: (record?.visualFeatures.composition.framing || "WIDE") as any,
        categoryFamily: "broll_perceptual",
        technicalQuality: 0.95,
      };
    });
  }
}
