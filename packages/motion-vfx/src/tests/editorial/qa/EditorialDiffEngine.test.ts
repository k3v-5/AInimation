import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { EditorialDiffEngine } from "../../../editorial/qa/editorial-diff-engine.js";
import { EditorialIR } from "../../../editorial/ir/editorial-ir.types.js";

describe("Editorial QA — Editorial Diff Engine Suite (REQ-QA-030 to REQ-QA-042, REQ-QA-058)", () => {
  const baseIR: EditorialIR = {
    schemaVersion: "4.0.0",
    projectId: "diff_proj_base",
    createdAt: new Date().toISOString(),
    checksum: "0".repeat(64),
    metadata: {
      title: "Diff Base Composition",
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
        name: "Primary Video",
        type: "VIDEO_PRIMARY",
        index: 0,
        isMuted: false,
        isLocked: false,
        clips: [
          {
            id: "c1",
            assetId: "a1",
            label: "Shot 1",
            sourceRange: { startSeconds: 0, durationSeconds: 5.0 },
            timelineRange: { startSeconds: 0, durationSeconds: 5.0 },
            speed: 1.0,
            volumeDb: 0.0,
            pan: 0.0,
            scale: 1.0,
          },
          {
            id: "c2",
            assetId: "a2",
            label: "Shot 2",
            sourceRange: { startSeconds: 0, durationSeconds: 5.0 },
            timelineRange: { startSeconds: 5.0, durationSeconds: 5.0 },
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

  it("PBT-008: compare(A, A) returns changedEntitiesCount = 0 and overallImpactScore = 0 (REQ-QA-056)", () => {
    const report = EditorialDiffEngine.compare(baseIR, baseIR);
    assert.equal(report.changedEntitiesCount, 0);
    assert.equal(report.addedCount, 0);
    assert.equal(report.removedCount, 0);
    assert.equal(report.modifiedCount, 0);
    assert.equal(report.diffs.length, 0);
    assert.equal(report.summary.overallImpactScore, 0);
    assert.equal(report.beforeChecksumSha256, report.afterChecksumSha256);
    assert.ok(report.checksumSha256.length === 64);
  });

  it("detects ADD, REMOVE and calculates exact duration deltas (REQ-QA-031, REQ-QA-033)", () => {
    const candidateIR: EditorialIR = {
      ...baseIR,
      tracks: [
        {
          ...baseIR.tracks[0],
          clips: [
            baseIR.tracks[0].clips[0], // c1 preserved
            {
              id: "c3_added",
              assetId: "a3",
              label: "New Shot 3",
              sourceRange: { startSeconds: 0, durationSeconds: 3.0 },
              timelineRange: { startSeconds: 5.0, durationSeconds: 3.0 },
              speed: 1.0,
              volumeDb: 0.0,
              pan: 0.0,
              scale: 1.0,
            },
          ],
        },
      ],
    };

    const report = EditorialDiffEngine.compare(baseIR, candidateIR);
    assert.equal(report.addedCount, 1);
    assert.equal(report.removedCount, 1);
    assert.ok(report.diffs.some((d) => d.type === "REMOVED" && d.entityId === "c2"));
    assert.ok(report.diffs.some((d) => d.type === "ADDED" && d.entityId === "c3_added"));
    assert.equal(report.summary.durationDeltaSeconds, -2.0); // 10s -> 8s
  });

  it("differentiates DIRECT from DERIVED changes when timeline ripple occurs (REQ-QA-040)", () => {
    const candidateIR: EditorialIR = {
      ...baseIR,
      tracks: [
        {
          ...baseIR.tracks[0],
          clips: [
            {
              ...baseIR.tracks[0].clips[0],
              timelineRange: { startSeconds: 0, durationSeconds: 8.0 }, // c1 extended by 3s -> DIRECT
            },
            {
              ...baseIR.tracks[0].clips[1],
              timelineRange: { startSeconds: 8.0, durationSeconds: 5.0 }, // c2 pushed forward -> DERIVED
            },
          ],
        },
      ],
    };

    const report = EditorialDiffEngine.compare(baseIR, candidateIR);
    assert.equal(report.modifiedCount, 2);

    const c1Diff = report.diffs.find((d) => d.entityId === "c1");
    const c2Diff = report.diffs.find((d) => d.entityId === "c2");

    assert.equal(c1Diff?.origin, "DIRECT");
    assert.equal(c1Diff?.type, "RESIZED");
    assert.equal(c2Diff?.origin, "DERIVED");
    assert.equal(c2Diff?.type, "MOVED");
  });
});
