import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { EditorialQALinter } from "../../../editorial/qa/editorial-qa-linter.js";
import {
  QA_AUDIO_001,
  QA_AUDIO_005,
  QA_EVIDENCE_001,
  QA_LOAD_001,
  QA_MEDIA_001,
  QA_PACE_001,
  QA_STRUCT_003,
  QA_TIME_001,
  QA_TIME_002,
  QA_TIME_004,
} from "../../../editorial/qa/editorial-qa-rules.js";
import { EditorialQAContext } from "../../../editorial/qa/editorial-qa-types.js";

describe("Editorial QA — Rules Suite (REQ-QA-005 to REQ-QA-021)", () => {
  const baseConfig = EditorialQALinter.createDefaultConfig();

  const createMinimalIR = (overrides?: any) => ({
    schemaVersion: "4.0.0" as const,
    projectId: "test_project",
    createdAt: new Date().toISOString(),
    checksum: "a".repeat(64),
    metadata: {
      title: "Test Editorial",
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
            id: "clip_1",
            assetId: "asset_1",
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
    ...overrides,
  });

  it("QA-STRUCT-003: flags duplicate track and clip IDs as BLOCKING (REQ-QA-008)", () => {
    const ir = createMinimalIR({
      tracks: [
        {
          id: "v_dupe",
          name: "Video 1",
          type: "VIDEO_PRIMARY",
          index: 0,
          isMuted: false,
          isLocked: false,
          clips: [
            {
              id: "c_dupe",
              assetId: "a1",
              label: "Shot A",
              sourceRange: { startSeconds: 0, durationSeconds: 2 },
              timelineRange: { startSeconds: 0, durationSeconds: 2 },
            },
            {
              id: "c_dupe", // Duplicate clip ID
              assetId: "a2",
              label: "Shot B",
              sourceRange: { startSeconds: 0, durationSeconds: 2 },
              timelineRange: { startSeconds: 2, durationSeconds: 2 },
            },
          ],
        },
        {
          id: "v_dupe", // Duplicate track ID
          name: "Video 2",
          type: "VIDEO_BROLL",
          index: 1,
          isMuted: false,
          isLocked: false,
          clips: [],
        },
      ],
    });

    const issues = QA_STRUCT_003.evaluate({ ir, config: baseConfig });
    assert.equal(issues.length, 2);
    assert.ok(issues.every((i) => i.severity === "BLOCKING"));
  });

  it("QA-TIME-001 & QA-TIME-004: flags non-positive durations and illegal overlaps (REQ-QA-009)", () => {
    const ir = createMinimalIR({
      tracks: [
        {
          id: "v1",
          name: "V1",
          type: "VIDEO_PRIMARY",
          index: 0,
          isMuted: false,
          isLocked: false,
          clips: [
            {
              id: "c_neg",
              assetId: "a1",
              label: "Zero Duration Shot",
              sourceRange: { startSeconds: 0, durationSeconds: 0 },
              timelineRange: { startSeconds: 0, durationSeconds: 0 },
            },
            {
              id: "c_over1",
              assetId: "a2",
              label: "Overlap 1",
              sourceRange: { startSeconds: 0, durationSeconds: 4 },
              timelineRange: { startSeconds: 1, durationSeconds: 4 }, // 1s to 5s
            },
            {
              id: "c_over2",
              assetId: "a3",
              label: "Overlap 2",
              sourceRange: { startSeconds: 0, durationSeconds: 3 },
              timelineRange: { startSeconds: 3, durationSeconds: 3 }, // 3s to 6s (overlaps by 2s!)
            },
          ],
        },
      ],
    });

    const durIssues = QA_TIME_001.evaluate({ ir, config: baseConfig });
    assert.equal(durIssues.length, 1);
    assert.equal(durIssues[0].entityIds[0], "c_neg");

    const overlapIssues = QA_TIME_004.evaluate({ ir, config: baseConfig });
    assert.equal(overlapIssues.length, 1);
    assert.deepEqual(overlapIssues[0].entityIds, ["c_over1", "c_over2"]);
  });

  it("QA-MEDIA-001: flags unresolvable assetIds as BLOCKING (REQ-QA-010)", () => {
    const ir = createMinimalIR();
    const context: EditorialQAContext = {
      ir,
      config: baseConfig,
      assetRegistry: {
        asset_1: { exists: false }, // Media offline/missing
      },
    };

    const issues = QA_MEDIA_001.evaluate(context);
    assert.equal(issues.length, 1);
    assert.equal(issues[0].severity, "BLOCKING");
  });

  it("QA-AUDIO-001 & QA-AUDIO-005: detects clipping and voice/music competition (REQ-QA-011)", () => {
    const ir = createMinimalIR({
      tracks: [
        {
          id: "t_speech",
          name: "Speech",
          type: "AUDIO_DIALOGUE",
          index: 0,
          isMuted: false,
          isLocked: false,
          clips: [
            {
              id: "c_speech",
              assetId: "a_voice",
              label: "Dialogue",
              timelineRange: { startSeconds: 0, durationSeconds: 5.0 },
              volumeDb: 2.5, // Clipping!
            },
          ],
        },
        {
          id: "t_music",
          name: "Music",
          type: "AUDIO_MUSIC",
          index: 1,
          isMuted: false,
          isLocked: false,
          clips: [
            {
              id: "c_music",
              assetId: "a_bgm",
              label: "BGM",
              timelineRange: { startSeconds: 0, durationSeconds: 5.0 },
              volumeDb: -3.0, // Loud music competing with voice without ducking
            },
          ],
        },
      ],
    });

    const clipIssues = QA_AUDIO_001.evaluate({ ir, config: baseConfig });
    assert.equal(clipIssues.length, 1);
    assert.equal(clipIssues[0].ruleId, "QA-AUDIO-001");

    const duckIssues = QA_AUDIO_005.evaluate({ ir, config: baseConfig });
    assert.equal(duckIssues.length, 1);
    assert.equal(duckIssues[0].ruleId, "QA-AUDIO-005");
    assert.ok(duckIssues[0].autoFixAvailable);
  });

  it("QA-EVIDENCE-001: flags verifiable claim without backing evidence (REQ-QA-015)", () => {
    const ir = createMinimalIR({
      claims: [
        {
          id: "claim_unverified",
          statement: "Inflation dropped by 50% in 2024",
          isVerifiable: true,
          evidenceIds: [], // Missing evidence!
        },
      ],
    });

    const issues = QA_EVIDENCE_001.evaluate({ ir, config: baseConfig });
    assert.equal(issues.length, 1);
    assert.equal(issues[0].severity, "BLOCKING");
  });

  it("QA-LOAD-001 & QA-PACE-001: detects sustained cognitive overload and pacing misalignment (REQ-QA-017, REQ-QA-019)", () => {
    const ir = createMinimalIR({
      metrics: {
        cognitiveLoadSamples: [
          { t: 0.0, load: 0.88 },
          { t: 1.0, load: 0.90 },
          { t: 2.0, load: 0.89 },
          { t: 3.5, load: 0.86 }, // >= 0.85 for 3.5 seconds!
          { t: 4.0, load: 0.50 },
        ],
        pacingAlignmentScore: 0.42, // Below 0.65 threshold
      },
    });

    const loadIssues = QA_LOAD_001.evaluate({ ir, config: baseConfig });
    assert.equal(loadIssues.length, 1);
    assert.equal(loadIssues[0].category, "COGNITIVE_LOAD");

    const paceIssues = QA_PACE_001.evaluate({ ir, config: baseConfig });
    assert.equal(paceIssues.length, 1);
    assert.equal(paceIssues[0].category, "PACING");
  });
});
