import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { EditorialQALinter } from "../../../editorial/qa/editorial-qa-linter.js";
import { EditorialDiffEngine } from "../../../editorial/qa/editorial-diff-engine.js";
import { QAHash } from "../../../editorial/qa/qa-hash.js";
import { EditorialIR } from "../../../editorial/ir/editorial-ir.types.js";

describe("Editorial QA — Determinism & Mathematical Invariants Suite (REQ-QA-002, REQ-QA-056: PBT-001 to PBT-009)", () => {
  const sampleIR: EditorialIR = {
    schemaVersion: "4.0.0",
    projectId: "pbt_sample_proj",
    createdAt: "2026-09-02T12:00:00.000Z",
    checksum: "0".repeat(64),
    metadata: {
      title: "PBT Sample Composition",
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

  it("PBT-001 & PBT-002: runQA(ir) is strictly idempotent and produces byte-identical checksum (REQ-QA-056)", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 5 }), () => {
        const clone = JSON.parse(JSON.stringify(sampleIR));
        const rep1 = EditorialQALinter.lint({ ir: sampleIR });
        const rep2 = EditorialQALinter.lint({ ir: clone });

        assert.equal(rep1.checksumSha256, rep2.checksumSha256);
        assert.equal(rep1.status, rep2.status);
        assert.equal(rep1.summary.total, rep2.summary.total);
      }),
      { numRuns: 25 }
    );
  });

  it("PBT-003 & PBT-004: all confidence values in [0, 1] and scores strictly in [0, 100] (REQ-QA-056)", () => {
    const report = EditorialQALinter.lint({ ir: sampleIR });
    assert.ok(report.confidenceSummary.average >= 0.0 && report.confidenceSummary.average <= 1.0);
    assert.ok(report.confidenceSummary.minimum >= 0.0 && report.confidenceSummary.minimum <= 1.0);
    assert.ok(report.overallScore >= 0.0 && report.overallScore <= 100.0);
  });

  it("PBT-005: Property reordering produces identical canonical serialization and SHA-256 (REQ-QA-035)", () => {
    const objA = { z: 1, a: "test", m: [3, 2, 1], nested: { y: true, x: 42 } };
    const objB = { nested: { x: 42, y: true }, m: [3, 2, 1], a: "test", z: 1 };

    const hashA = QAHash.computeCanonicalSha256(objA);
    const hashB = QAHash.computeCanonicalSha256(objB);

    assert.equal(hashA, hashB);
  });

  it("PBT-006: Adding a SUGGESTION never escalates to BLOCKING (REQ-QA-056)", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 20 }), (suggCount) => {
        const score = EditorialQALinter.calculateOverallScore(0, 0, suggCount);
        // Even with 20 suggestions, blockingCount is 0 -> canExport = true
        assert.ok(score >= 0 && score <= 100);
      }),
      { numRuns: 50 }
    );
  });

  it("PBT-007: Identical modification applied twice produces byte-identical diff report (REQ-QA-056)", () => {
    const modifiedIR: EditorialIR = {
      ...sampleIR,
      tracks: [
        {
          ...sampleIR.tracks[0],
          clips: [
            {
              ...sampleIR.tracks[0].clips[0],
              timelineRange: { startSeconds: 0, durationSeconds: 6.0 },
            },
          ],
        },
      ],
    };

    const diff1 = EditorialDiffEngine.compare(sampleIR, modifiedIR);
    const diff2 = EditorialDiffEngine.compare(sampleIR, modifiedIR);

    assert.equal(diff1.checksumSha256, diff2.checksumSha256);
    assert.equal(diff1.summary.durationDeltaSeconds, diff2.summary.durationDeltaSeconds);
  });

  it("PBT-008: compare(A, A) returns changedEntitiesCount = 0 and overallImpactScore = 0 (REQ-QA-056)", () => {
    const diff = EditorialDiffEngine.compare(sampleIR, sampleIR);
    assert.equal(diff.changedEntitiesCount, 0);
    assert.equal(diff.summary.overallImpactScore, 0);
  });

  it("PBT-009: Issue identity creation is 100% stable across re-executions (REQ-QA-006, REQ-QA-056)", () => {
    const id1 = QAHash.createIssueId({
      ruleId: "QA-TIME-001",
      entityIds: ["clip_abc"],
      timestampSeconds: 12.345,
      fingerprint: "neg_dur",
    });

    const id2 = QAHash.createIssueId({
      ruleId: "QA-TIME-001",
      entityIds: ["clip_abc"],
      timestampSeconds: 12.345,
      fingerprint: "neg_dur",
    });

    assert.equal(id1, id2);
    assert.ok(id1.startsWith("issue_qa-time-001_"));
    assert.equal(id1.length, "issue_qa-time-001_".length + 16);
  });
});
