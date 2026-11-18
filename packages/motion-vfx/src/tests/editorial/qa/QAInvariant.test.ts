import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { EditorialQALinter } from "../../../editorial/qa/editorial-qa-linter.js";
import { EditorialDiffEngine } from "../../../editorial/qa/editorial-diff-engine.js";
import { EditorialDocument } from "../../../editorial/contracts/editorial-qa.types.js";

describe("REQ-030 / REQ-082 — QA Mathematical Invariants & PBT Suite (§50, §51)", () => {
  const sampleDoc: EditorialDocument = {
    schemaVersion: "4.0.0",
    projectId: "invariant_sample",
    createdAt: "2026-09-02T00:00:00.000Z",
    checksum: "0".repeat(64),
    metadata: {
      title: "Invariant Sample",
      profile: "DOCUMENTARY",
      frameRate: 30,
      width: 1920,
      height: 1080,
      sampleRate: 44100,
      targetDialogueLufs: -16,
    },
    tracks: [
      {
        id: "v1",
        name: "Video 1",
        type: "VIDEO_PRIMARY",
        index: 0,
        isMuted: false,
        isLocked: false,
        clips: [
          {
            id: "clip_01",
            assetId: "asset_01",
            label: "Shot 1",
            sourceRange: { startSeconds: 0, durationSeconds: 4.0 },
            timelineRange: { startSeconds: 0, durationSeconds: 4.0 },
            speed: 1.0,
            volumeDb: 0.0,
            pan: 0.0,
            scale: 1.0,
          },
        ],
      },
    ],
    transitions: [],
    markers: [],
  };

  it("§50: diff(x, x) strictly returns 0 total changes and impactLevel 'NONE'", () => {
    const diffReport = EditorialDiffEngine.diff(sampleDoc, sampleDoc);
    assert.equal(diffReport.totalChanges, 0);
    assert.equal(diffReport.impactLevel, "NONE");
    assert.equal(diffReport.summary.added, 0);
    assert.equal(diffReport.summary.removed, 0);
    assert.equal(diffReport.summary.modified, 0);
    assert.equal(diffReport.summary.moved, 0);
  });

  it("§50: lint(x) is strictly idempotent and score is bounded within [0, 100]", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 10 }), () => {
        const rep1 = EditorialQALinter.lint(sampleDoc);
        const rep2 = EditorialQALinter.lint(sampleDoc);

        assert.equal(rep1.checksumSha256, rep2.checksumSha256);
        assert.equal(rep1.score, rep2.score);
        assert.ok(rep1.score >= 0.0 && rep1.score <= 100.0);
        return true;
      }),
      { numRuns: 20 }
    );
  });
});
