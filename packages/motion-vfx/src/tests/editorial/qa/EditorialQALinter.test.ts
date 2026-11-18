import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { EditorialQALinter } from "../../../editorial/qa/editorial-qa-linter.js";
import { EditorialDocument } from "../../../editorial/contracts/editorial-qa.types.js";

describe("REQ-030 — EditorialQALinter Suite", () => {
  const cleanDoc: EditorialDocument = {
    schemaVersion: "4.0.0",
    projectId: "linter_clean_doc",
    createdAt: "2026-09-02T00:00:00.000Z",
    checksum: "0".repeat(64),
    metadata: {
      title: "Clean Documentary Master",
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
            sourceRange: { startSeconds: 0, durationSeconds: 6.0 },
            timelineRange: { startSeconds: 0, durationSeconds: 6.0 },
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

  it("§4, §17: certifies clean document as 'PASSED' with 100 score and export ready", () => {
    const report = EditorialQALinter.lint(cleanDoc);
    assert.equal(report.status, "PASSED");
    assert.equal(report.summary.blocking, 0);
    assert.equal(report.summary.warnings, 0);
    assert.equal(report.score, 100.0);
    assert.equal(report.exportReadiness.ready, true);
    assert.equal(report.exportReadiness.blockers.length, 0);
    assert.equal(report.checksumSha256.length, 64);
  });

  it("§5.2: classifies document with audio clipping as 'PASSED_WITH_WARNINGS'", () => {
    const warningDoc: EditorialDocument = {
      ...cleanDoc,
      tracks: [
        {
          ...cleanDoc.tracks[0],
          clips: [
            {
              ...cleanDoc.tracks[0].clips[0],
              volumeDb: 2.5, // Audio clipping warning
            },
          ],
        },
      ],
    };

    const report = EditorialQALinter.lint(warningDoc);
    assert.equal(report.status, "PASSED_WITH_WARNINGS");
    assert.equal(report.summary.blocking, 0);
    assert.ok(report.summary.warnings > 0);
    assert.equal(report.exportReadiness.ready, true);
  });

  it("§5.1: classifies document with non-positive duration as 'BLOCKED'", () => {
    const blockedDoc: EditorialDocument = {
      ...cleanDoc,
      tracks: [
        {
          ...cleanDoc.tracks[0],
          clips: [
            {
              ...cleanDoc.tracks[0].clips[0],
              timelineRange: { startSeconds: 0, durationSeconds: -1.0 }, // Negative duration
            },
          ],
        },
      ],
    };

    const report = EditorialQALinter.lint(blockedDoc);
    assert.equal(report.status, "BLOCKED");
    assert.ok(report.summary.blocking > 0);
    assert.equal(report.exportReadiness.ready, false);
    assert.ok(report.exportReadiness.blockers.length > 0);
  });

  it("§42: strict mode with failOnWarnings blocks export when warnings exist", () => {
    const warningDoc: EditorialDocument = {
      ...cleanDoc,
      tracks: [
        {
          ...cleanDoc.tracks[0],
          clips: [
            {
              ...cleanDoc.tracks[0].clips[0],
              volumeDb: 1.5,
            },
          ],
        },
      ],
    };

    const report = EditorialQALinter.lint(warningDoc, { failOnWarnings: true });
    assert.equal(report.canExport, false);
    assert.equal(report.exportReadiness.ready, false);
  });
});
