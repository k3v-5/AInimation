import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { QARulesRegistry } from "../../../editorial/qa/qa-rules.js";
import { EditorialDocument } from "../../../editorial/contracts/editorial-qa.types.js";

describe("REQ-030 — QARules Registry & Domain Rules Suite", () => {
  const baseDoc: EditorialDocument = {
    schemaVersion: "4.0.0",
    projectId: "rules_test_doc",
    createdAt: "2026-09-02T00:00:00.000Z",
    checksum: "0".repeat(64),
    metadata: {
      title: "Rules Test Document",
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

  it("§8: registers all domain rules explicitly without dynamic loading", () => {
    const rules = QARulesRegistry.getAllRules();
    assert.ok(rules.length >= 10);
    const ruleIds = rules.map((r) => r.id);
    assert.ok(ruleIds.includes("QA-TIME-001"));
    assert.ok(ruleIds.includes("QA-NARR-001"));
    assert.ok(ruleIds.includes("QA-EVID-001"));
    assert.ok(ruleIds.includes("QA-VIS-001"));
    assert.ok(ruleIds.includes("QA-AUD-001"));
    assert.ok(ruleIds.includes("QA-EXP-001"));
    assert.ok(ruleIds.includes("QA-SAFE-001"));
  });

  it("evaluates safety injection attempts as BLOCKING", () => {
    const maliciousDoc: EditorialDocument = {
      ...baseDoc,
      metadata: {
        ...baseDoc.metadata,
        title: "Malicious <script>alert(1)</script> Title",
      },
    };

    const issues = QARulesRegistry.evaluateAll(maliciousDoc);
    const safeIssue = issues.find((i) => i.ruleId === "QA-SAFE-001");
    assert.ok(safeIssue);
    assert.equal(safeIssue?.severity, "BLOCKING");
  });

  it("evaluates empty track list as BLOCKING via QA-EXP-001", () => {
    const emptyDoc: EditorialDocument = {
      ...baseDoc,
      tracks: [],
    };

    const issues = QARulesRegistry.evaluateAll(emptyDoc);
    const expIssue = issues.find((i) => i.ruleId === "QA-EXP-001");
    assert.ok(expIssue);
    assert.equal(expIssue?.severity, "BLOCKING");
  });
});
