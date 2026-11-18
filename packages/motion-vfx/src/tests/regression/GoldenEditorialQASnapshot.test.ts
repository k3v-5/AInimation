import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { EditorialQALinter } from "../../editorial/qa/editorial-qa-linter.js";
import { EditorialDiffEngine } from "../../editorial/qa/editorial-diff-engine.js";
import { EditorialIR } from "../../editorial/ir/editorial-ir.types.js";

describe("Regression — Golden Editorial QA & Diff Snapshot (REQ-QA-059)", () => {
  const goldenIR: EditorialIR = {
    schemaVersion: "4.0.0",
    projectId: "golden_qa_project",
    createdAt: "2026-09-02T00:00:00.000Z",
    checksum: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    metadata: {
      title: "Golden Editorial QA Project",
      profile: "DOCUMENTARY",
      frameRate: 30,
      width: 1920,
      height: 1080,
      sampleRate: 44100,
      targetDialogueLufs: -16,
    },
    tracks: [
      {
        id: "v_primary",
        name: "Video Primary",
        type: "VIDEO_PRIMARY",
        index: 0,
        isMuted: false,
        isLocked: false,
        clips: [
          {
            id: "shot_01",
            assetId: "asset_01",
            label: "Opening Master",
            sourceRange: { startSeconds: 0, durationSeconds: 6.0 },
            timelineRange: { startSeconds: 0, durationSeconds: 6.0 },
            speed: 1.0,
            volumeDb: 0.0,
            pan: 0.0,
            scale: 1.0,
          },
          {
            id: "shot_02",
            assetId: "asset_02",
            label: "Supporting B-Roll",
            sourceRange: { startSeconds: 0, durationSeconds: 4.0 },
            timelineRange: { startSeconds: 6.0, durationSeconds: 4.0 },
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

  it("produces deterministic, frozen QA report and checksum SHA-256 (REQ-QA-059)", () => {
    const report = EditorialQALinter.lint({ ir: goldenIR });

    assert.equal(report.status, "PASS");
    assert.equal(report.summary.blocking, 0);
    assert.equal(report.summary.warnings, 0);
    assert.equal(report.summary.suggestions, 0);
    assert.equal(report.summary.total, 0);
    assert.equal(report.overallScore, 100.0);
    assert.equal(report.humanReviewRequired, false);
    assert.equal(report.humanReviewCount, 0);

    // Verify SHA-256 integrity
    assert.equal(report.checksumSha256.length, 64);
    assert.equal(report.integrity.deterministic, true);

    // Rerun check
    const rerun = EditorialQALinter.lint({ ir: goldenIR });
    assert.equal(rerun.checksumSha256, report.checksumSha256);
  });

  it("produces deterministic, frozen Diff report against modified version (REQ-QA-059)", () => {
    const modifiedIR: EditorialIR = {
      ...goldenIR,
      tracks: [
        {
          ...goldenIR.tracks[0],
          clips: [
            goldenIR.tracks[0].clips[0],
            {
              ...goldenIR.tracks[0].clips[1],
              timelineRange: { startSeconds: 6.0, durationSeconds: 6.0 }, // Extended by 2.0s
            },
          ],
        },
      ],
    };

    const diff = EditorialDiffEngine.compare(goldenIR, modifiedIR);
    assert.equal(diff.changedEntitiesCount, 1);
    assert.equal(diff.modifiedCount, 1);
    assert.equal(diff.summary.durationDeltaSeconds, 2.0);
    assert.equal(diff.checksumSha256.length, 64);

    const rerun = EditorialDiffEngine.compare(goldenIR, modifiedIR);
    assert.equal(rerun.checksumSha256, diff.checksumSha256);
  });
});
