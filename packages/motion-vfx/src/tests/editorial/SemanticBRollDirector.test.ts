import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  SemanticBRollDirector,
  SemanticBRollCandidate,
} from "../../editorial/index.js";

test("Fase 4B — Semantic B-Roll Director Suite", async (t) => {
  const candidates: SemanticBRollCandidate[] = [
    {
      id: "broll_iceland_geyser",
      assetId: "geyser_eruption.mp4",
      description: "Huge geothermal steam eruption in volcanic landscape",
      tags: ["iceland", "volcano", "geothermal", "steam", "geyser"],
      semanticConcepts: ["energy", "explosion", "nature", "power"],
      emotionalTone: "ENERGETIC",
      durationSeconds: 6.0,
      scale: "WIDE",
      categoryFamily: "volcanic_geothermal",
      technicalQuality: 0.95,
    },
    {
      id: "broll_iceland_glacier",
      assetId: "glacier_crevasse.mp4",
      description: "Ancient blue ice crevasses on solitary glacial expanse",
      tags: ["iceland", "glacier", "ice", "crevasse", "cold"],
      semanticConcepts: ["frozen", "solitude", "ancient", "climate"],
      emotionalTone: "CALM",
      durationSeconds: 8.0,
      scale: "EXTREME_WIDE",
      categoryFamily: "glacier_ice",
      technicalQuality: 0.92,
    },
    {
      id: "broll_generic_city",
      assetId: "tokyo_crosswalk.mp4",
      description: "Crowds walking across busy Shibuya street at dusk",
      tags: ["city", "urban", "crowd", "tokyo", "street"],
      semanticConcepts: ["human", "society", "busy"],
      emotionalTone: "NEUTRAL",
      durationSeconds: 5.0,
      scale: "MEDIUM",
      categoryFamily: "urban_crowd",
      technicalQuality: 0.88,
    },
  ];

  await t.test("matches relevant B-roll based on spoken concept and tone", () => {
    const director = new SemanticBRollDirector();

    const result = director.selectBestBRoll({
      spokenSentence: "The geothermal energy erupted with massive steam power through the rocks.",
      requiredDurationSeconds: 4.0,
      candidates,
      targetTone: "ENERGETIC",
    });

    assert.ok(result.selectedCandidate);
    assert.equal(result.selectedCandidate.id, "broll_iceland_geyser");
    assert.ok(result.matchScore);
    assert.ok(result.matchScore.conceptualMatch >= 0.4);
    assert.equal(result.matchScore.repetitionPenalty, 0); // First usage: 0 penalty
    assert.ok(result.matchScore.finalScore > 70 && result.matchScore.finalScore <= 100);
  });

  await t.test("penalizes repeated asset exponentially to suppress clichés (REQ-014)", () => {
    const director = new SemanticBRollDirector();
    const geyser = candidates[0];

    // First usage: 0 penalty
    const penalty0 = director.computeRepetitionPenalty(geyser.assetId, geyser.categoryFamily);
    assert.equal(penalty0, 0);

    // Register 1st usage
    director.registerAssetUsage(geyser);
    const penalty1 = director.computeRepetitionPenalty(geyser.assetId, geyser.categoryFamily);
    assert.ok(penalty1 > 0.45 && penalty1 < 0.85);

    // Register 2nd usage
    director.registerAssetUsage(geyser);
    const penalty2 = director.computeRepetitionPenalty(geyser.assetId, geyser.categoryFamily);
    assert.ok(penalty2 > penalty1);

    // If we select B-roll again, the heavily repeated asset will drop in final score
    const selection = director.selectBestBRoll({
      spokenSentence: "The geothermal energy erupted with massive steam power through the rocks.",
      requiredDurationSeconds: 4.0,
      candidates,
      targetTone: "ENERGETIC",
    });

    const geyserRanked = selection.rankedAlternatives.find((r) => r.candidate.id === geyser.id);
    assert.ok(geyserRanked);
    assert.ok(geyserRanked.score.repetitionPenalty > 0.7);
  });

  await t.test("PBT: repetition penalty is strictly monotonic non-decreasing with usage count", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 10 }), (usages) => {
        const director = new SemanticBRollDirector();
        const assetId = "test_asset";
        const family = "test_family";

        let prevPenalty = director.computeRepetitionPenalty(assetId, family);
        for (let i = 0; i < usages; i++) {
          director.registerAssetUsage({
            id: `cand_${i}`,
            assetId,
            description: "test",
            tags: [],
            semanticConcepts: [],
            emotionalTone: "NEUTRAL",
            durationSeconds: 5,
            scale: "WIDE",
            categoryFamily: family,
            technicalQuality: 0.9,
          });
          const newPenalty = director.computeRepetitionPenalty(assetId, family);
          if (newPenalty < prevPenalty) {
            return false;
          }
          prevPenalty = newPenalty;
        }
        return prevPenalty <= 1.0;
      }),
      { numRuns: 40 }
    );
  });
});
