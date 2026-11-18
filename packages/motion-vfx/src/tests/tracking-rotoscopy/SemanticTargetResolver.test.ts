import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { SemanticTargetResolver } from "../../tracking-rotoscopy/core/SemanticTargetResolver.js";
import { Track } from "../../tracking-rotoscopy/types/index.js";

describe("Fase 12 — Semantic Target Resolver Tests", () => {
  const sampleTracks: Track[] = [
    {
      id: "track_person_secondary",
      targetType: "person",
      semanticClass: "person",
      role: "secondary_subject",
      start: 0,
      end: 5.0,
      confidence: 0.95,
      state: "active",
      samples: [],
    },
    {
      id: "track_person_main",
      targetType: "person",
      semanticClass: "person",
      role: "main_subject",
      start: 0,
      end: 5.0,
      confidence: 0.88,
      state: "active",
      samples: [],
    },
    {
      id: "track_laptop",
      targetType: "object",
      semanticClass: "laptop",
      role: "secondary_subject",
      start: 0,
      end: 3.0,
      confidence: 0.92,
      state: "active",
      samples: [],
    },
  ];

  it("prioritizes main_subject when querying person", () => {
    const target = SemanticTargetResolver.resolveTarget(sampleTracks, {
      semanticClass: "person",
      role: "main_subject",
    });

    assert.strictEqual(target !== undefined, true);
    assert.strictEqual(target?.id, "track_person_main");
  });

  it("resolves specific semantic class laptop correctly", () => {
    const target = SemanticTargetResolver.resolveTarget(sampleTracks, {
      semanticClass: "laptop",
    });

    assert.strictEqual(target !== undefined, true);
    assert.strictEqual(target?.id, "track_laptop");
  });
});
