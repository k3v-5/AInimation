import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AIHookCoverGenerator, CoverCandidateFrame } from "../../media-intelligence/covers/AIHookCoverGenerator.js";

describe("Media Intelligence — AIHookCoverGenerator Tests", () => {
  it("selects hero frame based on lighting contrast, centering and aesthetic score", () => {
    const candidates: CoverCandidateFrame[] = [
      { clipId: "c1", timestamp: 1.0, aestheticScore: 80, hasLightingContrast: false, subjectCentered: false },
      { clipId: "c2", timestamp: 2.5, aestheticScore: 75, hasLightingContrast: true, subjectCentered: true }, // score = 75 + 15 + 10 = 100
      { clipId: "c3", timestamp: 4.0, aestheticScore: 82, hasLightingContrast: false, subjectCentered: true }, // score = 82 + 10 = 92
    ];

    const hero = AIHookCoverGenerator.selectHeroFrame(candidates);
    assert.equal(hero.clipId, "c2");
    assert.equal(hero.timestamp, 2.5);
  });

  it("generates well-formed ExtendScript hook cover composition snippet", () => {
    const snippet = AIHookCoverGenerator.generateHookCoverComp(
      "project",
      "COVER_MASTER_9X16",
      "footage_hero",
      {
        title: "TURRAZO LIVE",
        heroTimestamp: 2.5,
        badge: "CONCIERTO // 2023",
      }
    );

    assert.ok(snippet.includes('project.items.addComp("COVER_MASTER_9X16", 1080, 1920'));
    assert.ok(snippet.includes('Hero_Background'));
    assert.ok(snippet.includes('Cover_Title_Main'));
    assert.ok(snippet.includes('TURRAZO LIVE'));
    assert.ok(snippet.includes('CONCIERTO // 2023'));
    assert.ok(snippet.includes('ADBE Glo2'));
  });
});
