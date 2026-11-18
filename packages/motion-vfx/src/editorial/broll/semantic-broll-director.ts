import {
  SemanticBRollCandidate,
  SemanticBRollCandidateSchema,
  BRollSelectionResult,
  BRollSelectionResultSchema,
  RankedSemanticBRollCandidate,
  SemanticMatchScore,
  SemanticMatchScoreSchema,
} from "./semantic-broll.types.js";

/**
 * REQ-013 & REQ-014: Semantic B-Roll Director 2.0.
 * Multi-criteria matching based on spoken narrative concepts and emotional tone,
 * enforcing exponential repetition penalties against cliché stock footage overuse.
 */
export class SemanticBRollDirector {
  private readonly usageHistory: Map<string, number> = new Map(); // assetId -> usage count
  private readonly familyUsageHistory: Map<string, number> = new Map(); // family -> usage count

  /**
   * Registers that an asset was placed in the timeline to track repetition.
   */
  public registerAssetUsage(candidate: SemanticBRollCandidate): void {
    const currentAssetCount = this.usageHistory.get(candidate.assetId) ?? 0;
    this.usageHistory.set(candidate.assetId, currentAssetCount + 1);

    const currentFamilyCount = this.familyUsageHistory.get(candidate.categoryFamily) ?? 0;
    this.familyUsageHistory.set(candidate.categoryFamily, currentFamilyCount + 1);
  }

  /**
   * Selects the best B-Roll candidate for a spoken narrative context.
   */
  public selectBestBRoll(params: {
    spokenSentence: string;
    requiredDurationSeconds: number;
    candidates: SemanticBRollCandidate[];
    targetTone?: "NEUTRAL" | "TENSE" | "HOPEFUL" | "MELANCHOLY" | "ENERGETIC" | "CALM";
  }): BRollSelectionResult {
    const { spokenSentence, requiredDurationSeconds, candidates, targetTone } = params;

    if (candidates.length === 0) {
      return BRollSelectionResultSchema.parse({
        selectedCandidate: null,
        matchScore: null,
        rankedAlternatives: [],
        queryContext: {
          spokenSentence,
          requiredDurationSeconds,
          targetTone,
        },
      });
    }

    const queryKeywords = this.extractNormalizedKeywords(spokenSentence);

    const rankedAlternatives: RankedSemanticBRollCandidate[] = candidates.map((candidate) => {
      const validated = SemanticBRollCandidateSchema.parse(candidate);
      const score = this.evaluateCandidate(validated, queryKeywords, requiredDurationSeconds, targetTone);
      return { candidate: validated, score };
    });

    // Sort descending by finalScore
    rankedAlternatives.sort((a, b) => b.score.finalScore - a.score.finalScore);

    const best = rankedAlternatives[0] ?? null;

    return BRollSelectionResultSchema.parse({
      selectedCandidate: best ? best.candidate : null,
      matchScore: best ? best.score : null,
      rankedAlternatives,
      queryContext: {
        spokenSentence,
        requiredDurationSeconds,
        targetTone,
      },
    });
  }

  /**
   * Computes the exponential repetition penalty based on previous occurrences.
   * Penalty formula: P = 1 - exp(-0.70 * k)
   */
  public computeRepetitionPenalty(assetId: string, categoryFamily: string): number {
    const assetCount = this.usageHistory.get(assetId) ?? 0;
    const familyCount = this.familyUsageHistory.get(categoryFamily) ?? 0;

    // Direct asset repetition carries higher weight than family repetition
    const effectiveK = assetCount * 1.5 + Math.max(0, familyCount - 1) * 0.5;

    const penalty = 1.0 - Math.exp(-0.7 * effectiveK);
    return Math.min(1.0, Math.max(0.0, Number(penalty.toFixed(4))));
  }

  /**
   * Evaluates candidate suitability and returns a detailed SemanticMatchScore.
   */
  private evaluateCandidate(
    candidate: SemanticBRollCandidate,
    queryKeywords: string[],
    requiredDurationSeconds: number,
    targetTone?: string
  ): SemanticMatchScore {
    // 1. Conceptual Match via Keyword & Tag Overlap
    const candidateTerms = new Set([
      ...candidate.tags.map((t) => t.toLowerCase()),
      ...candidate.semanticConcepts.map((c) => c.toLowerCase()),
      ...this.extractNormalizedKeywords(candidate.description),
    ]);

    let matchCount = 0;
    for (const word of queryKeywords) {
      if (candidateTerms.has(word)) {
        matchCount++;
      }
    }

    const conceptualMatch = queryKeywords.length > 0 ? Math.min(1.0, matchCount / Math.max(1, queryKeywords.length)) : 0.5;

    // 2. Emotional Tone Alignment
    let emotionalMatch = 0.7;
    if (targetTone) {
      if (candidate.emotionalTone === targetTone) {
        emotionalMatch = 1.0;
      } else if (candidate.emotionalTone === "NEUTRAL") {
        emotionalMatch = 0.7;
      } else {
        emotionalMatch = 0.3; // Conflicting tone
      }
    }

    // 3. Narrative Relevance & Duration Fit
    const durationRatio = candidate.durationSeconds / Math.max(0.1, requiredDurationSeconds);
    const durationScore = durationRatio >= 0.8 ? 1.0 : Math.max(0.2, durationRatio);
    const narrativeRelevance = Number(((conceptualMatch * 0.7 + durationScore * 0.3)).toFixed(4));

    // 4. Repetition Penalty (REQ-014)
    const repetitionPenalty = this.computeRepetitionPenalty(candidate.assetId, candidate.categoryFamily);

    // 5. Final Composite Score
    const rawScore =
      0.45 * conceptualMatch +
      0.25 * narrativeRelevance +
      0.15 * emotionalMatch +
      0.15 * candidate.technicalQuality;

    // Multiplier drops significantly as repetition penalty increases
    const penaltyMultiplier = 1.0 - 0.75 * repetitionPenalty;
    const finalScore = Math.min(100.0, Math.max(0.0, rawScore * penaltyMultiplier * 100.0));

    return SemanticMatchScoreSchema.parse({
      conceptualMatch: Number(conceptualMatch.toFixed(4)),
      emotionalMatch: Number(emotionalMatch.toFixed(4)),
      narrativeRelevance: Number(narrativeRelevance.toFixed(4)),
      repetitionPenalty,
      finalScore: Number(finalScore.toFixed(2)),
    });
  }

  private static readonly STOP_WORDS = new Set([
    "the", "and", "with", "that", "this", "from", "for", "are", "was", "were",
    "will", "been", "have", "has", "had", "into", "onto", "through", "about",
    "los", "las", "les", "con", "por", "para", "que", "este", "esta", "estos", "estas",
  ]);

  /**
   * Tokenizes and normalizes text into lowercase searchable keywords.
   */
  private extractNormalizedKeywords(text: string): string[] {
    return text
      .toLowerCase()
      .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?"']/g, " ")
      .split(/\s+/)
      .filter((word) => word.length >= 3 && !SemanticBRollDirector.STOP_WORDS.has(word));
  }
}
