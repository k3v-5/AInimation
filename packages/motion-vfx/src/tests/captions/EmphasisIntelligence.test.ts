import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { EmphasisScorer } from "../../captions/intelligence/EmphasisScorer.js";
import { CaptionIntelligenceEngine } from "../../captions/intelligence/CaptionIntelligenceEngine.js";
import { CaptionDocument, CaptionWord } from "../../captions/types/index.js";

describe("Fase 16 — Emphasis Scorer & Intelligence Tests", () => {
  it("suppresses stopwords and boosts capitalized long content words", () => {
    const scorer = new EmphasisScorer({ emphasisThreshold: 0.55 });

    const stopword: CaptionWord = { id: "w1", text: "de", start: 0, end: 0.3, index: 0 };
    const contentWord: CaptionWord = { id: "w2", text: "EXTRAORDINARIO", start: 0.3, end: 1.0, index: 1 };

    const stopwordDecision = scorer.evaluateWord(stopword, 0, 2, "de EXTRAORDINARIO");
    const contentDecision = scorer.evaluateWord(contentWord, 1, 2, "de EXTRAORDINARIO");

    assert.equal(stopwordDecision.isEmphasized, false);
    assert.ok(contentDecision.score > 0.7);
    assert.equal(contentDecision.isEmphasized, true);
    assert.ok(contentDecision.reasons.includes("all-caps-emphasis"));
    assert.ok(contentDecision.reasons.includes("long-content-word"));
  });

  it("boosts words with emphatic punctuation and vocal prosodic signals", () => {
    const scorer = new EmphasisScorer();

    const prosodicWord: CaptionWord = {
      id: "w3",
      text: "¡Fuego!",
      start: 1.0,
      end: 1.5,
      index: 0,
      prosody: {
        energy: 0.95,
        pitch: 0.88,
        pauseAfter: 0.45,
      },
    };

    const decision = scorer.evaluateWord(prosodicWord, 0, 1, "¡Fuego!");
    assert.equal(decision.isEmphasized, true);
    assert.equal(decision.priority, 1);
    assert.ok(decision.reasons.includes("high-acoustic-energy"));
    assert.ok(decision.reasons.includes("emphatic-punctuation"));
  });

  it("applies custom keyword rules with custom animation override", () => {
    const customKeywords = new Map();
    customKeywords.set("secreto", { scoreBonus: 0.5, recommendedAnimation: "glowPulse", emojiTag: "idea" });

    const scorer = new EmphasisScorer({ customKeywords });
    const keyword: CaptionWord = { id: "w4", text: "secreto", start: 0, end: 0.5, index: 0 };

    const decision = scorer.evaluateWord(keyword, 0, 1, "secreto");
    assert.equal(decision.isEmphasized, true);
    assert.equal(decision.recommendedAnimation, "glowPulse");
    assert.equal(decision.recommendedEmojiTag, "idea");
  });

  it("CaptionIntelligenceEngine enforces maximum emphasis budget per segment", () => {
    const engine = new CaptionIntelligenceEngine({ maxEmphasizedWordsPerSegment: 2, minEmphasisInterval: 0.2 });

    const doc: CaptionDocument = {
      id: "budget_test",
      duration: 3.0,
      segments: [
        {
          id: "s1",
          start: 0,
          end: 3.0,
          text: "¡INCREÍBLE! ¡FANTÁSTICO! ¡EXTRAORDINARIO! ¡MAGNÍFICO!",
          words: [
            { id: "w1", text: "¡INCREÍBLE!", start: 0.0, end: 0.5, index: 0 },
            { id: "w2", text: "¡FANTÁSTICO!", start: 0.6, end: 1.1, index: 1 },
            { id: "w3", text: "¡EXTRAORDINARIO!", start: 1.2, end: 1.7, index: 2 },
            { id: "w4", text: "¡MAGNÍFICO!", start: 1.8, end: 2.3, index: 3 },
          ],
        },
      ],
    };

    const enriched = engine.analyzeDocument(doc);
    const emphasizedWords = enriched.segments[0].words.filter((w) => w.emphasis?.isEmphasized);

    // Debe regularse al presupuesto máximo de 2 palabras enfatizadas
    assert.equal(emphasizedWords.length, 2);
    assert.equal(emphasizedWords[0].text, "¡INCREÍBLE!");
    assert.equal(emphasizedWords[1].text, "¡EXTRAORDINARIO!");
    assert.ok(emphasizedWords[0].animation);
  });
});
