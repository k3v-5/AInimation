import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { ImpactAnalyzer } from "../../../editorial/qa/impact-analyzer.js";
import { EditorialDocument } from "../../../editorial/contracts/editorial-qa.types.js";

describe("REQ-082 — ImpactAnalyzer Suite", () => {
  const baseDoc: EditorialDocument = {
    schemaVersion: "4.0.0",
    projectId: "impact_test_doc",
    createdAt: "2026-09-02T00:00:00.000Z",
    checksum: "0".repeat(64),
    metadata: {
      title: "Impact Test",
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
        name: "Video",
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
            volumeDb: 0,
            pan: 0,
            scale: 1,
          },
        ],
      },
    ],
    transitions: [],
    markers: [],
  };

  it("classifies identical documents as ImpactLevel 'NONE' and duration delta 0", () => {
    const res = ImpactAnalyzer.analyzeImpact({
      beforeDoc: baseDoc,
      afterDoc: baseDoc,
      diffs: [],
    });

    assert.equal(res.impactLevel, "NONE");
    assert.equal(res.impact.durationDeltaSeconds, 0.0);
    assert.equal(res.impact.overallImpactScore, 0.0);
  });

  it("detects duration changes and computes exact delta", () => {
    const modifiedDoc: EditorialDocument = {
      ...baseDoc,
      tracks: [
        {
          ...baseDoc.tracks[0],
          clips: [
            {
              ...baseDoc.tracks[0].clips[0],
              timelineRange: { startSeconds: 0, durationSeconds: 8.0 }, // Extended by 3.0s
            },
          ],
        },
      ],
    };

    const res = ImpactAnalyzer.analyzeImpact({
      beforeDoc: baseDoc,
      afterDoc: modifiedDoc,
      diffs: [
        {
          id: "d1",
          type: "MODIFIED",
          entityType: "CLIP",
          entityId: "c1",
          path: "timelineRange.durationSeconds",
        },
      ],
    });

    assert.equal(res.impact.durationDeltaSeconds, 3.0);
    assert.equal(res.impactLevel, "MEDIUM");
    assert.ok(res.impact.overallImpactScore! > 0);
  });

  it("elevates impact to 'CRITICAL' when factual claims are affected", () => {
    const docWithClaims: EditorialDocument = {
      ...baseDoc,
      claims: [{ id: "claim_primary", statement: "Critical metric", isVerified: true }],
    } as any;

    const docWithoutClaims: EditorialDocument = {
      ...baseDoc,
      claims: [],
    } as any;

    const res = ImpactAnalyzer.analyzeImpact({
      beforeDoc: docWithClaims,
      afterDoc: docWithoutClaims,
      diffs: [
        {
          id: "d_claim",
          type: "REMOVED",
          entityType: "CLAIM",
          entityId: "claim_primary",
          path: "claims",
        },
      ],
    });

    assert.equal(res.impactLevel, "CRITICAL");
    assert.equal(res.impact.evidenceImpact?.claimsAffected, 1);
  });
});
