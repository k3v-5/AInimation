import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { EditorialAuditEngine } from "../../../editorial/qa/audit-engine.js";
import { EditorialDocument } from "../../../editorial/contracts/editorial-qa.types.js";

describe("REQ-030 — EditorialAuditEngine Suite", () => {
  const testDoc: EditorialDocument = {
    schemaVersion: "4.0.0",
    projectId: "audit_engine_doc",
    createdAt: "2026-09-02T00:00:00.000Z",
    checksum: "0".repeat(64),
    metadata: {
      title: "Audit Test Timeline",
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
            id: "clip_01",
            assetId: "a1",
            label: "Opening",
            sourceRange: { startSeconds: 0, durationSeconds: 4.0 },
            timelineRange: { startSeconds: 0, durationSeconds: 4.0 },
            speed: 1.0,
            volumeDb: 0.0,
            pan: 0.0,
            scale: 1.0,
          },
          {
            id: "clip_02",
            assetId: "a2",
            label: "Sound clip",
            sourceRange: { startSeconds: 0, durationSeconds: 4.0 },
            timelineRange: { startSeconds: 4.0, durationSeconds: 4.0 },
            speed: 1.0,
            volumeDb: 3.0, // Triggers AUDIO warning
            pan: 0.0,
            scale: 1.0,
          },
        ],
      },
    ],
    transitions: [],
    markers: [],
  };

  it("§17: categorizes issues accurately across domain categories", () => {
    const report = EditorialAuditEngine.audit(testDoc);
    assert.ok(report.categories.AUDIO);
    assert.equal(report.categories.AUDIO.issuesCount, 1);
    assert.ok(report.categories.AUDIO.score < 100);
    assert.equal(report.categories.TIMELINE.issuesCount, 0);
    assert.equal(report.categories.TIMELINE.score, 100);
  });

  it("produces deterministic SHA-256 report checksum", () => {
    const rep1 = EditorialAuditEngine.audit(testDoc);
    const rep2 = EditorialAuditEngine.audit(testDoc);

    assert.equal(rep1.checksumSha256.length, 64);
    assert.equal(rep1.checksumSha256, rep2.checksumSha256);
  });
});
