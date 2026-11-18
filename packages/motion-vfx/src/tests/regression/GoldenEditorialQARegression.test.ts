import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { EditorialQALinter } from "../../editorial/qa/editorial-qa-linter.js";
import { EditorialDiffEngine } from "../../editorial/qa/editorial-diff-engine.js";
import { EditorialDocument } from "../../editorial/contracts/editorial-qa.types.js";

describe("Regression — Golden Editorial QA & Diff Suite (§52, §53)", () => {
  const fixturePath = path.resolve(process.cwd(), "fixtures/editorial/qa/golden-production-project.json");
  const goldenProject: EditorialDocument = JSON.parse(fs.readFileSync(fixturePath, "utf-8"));

  it("produces deterministic, byte-identical QA report and SHA-256 seal from golden fixture", () => {
    const report = EditorialQALinter.lint(goldenProject);

    assert.equal(report.status, "PASSED");
    assert.equal(report.summary.blocking, 0);
    assert.equal(report.summary.warnings, 0);
    assert.equal(report.summary.suggestions, 0);
    assert.equal(report.score, 100.0);
    assert.equal(report.exportReadiness.ready, true);
    assert.ok(report.checksumSha256.length === 64);

    // Save golden QA snapshot if not exists
    const snapshotPath = path.resolve(process.cwd(), "fixtures/editorial/qa/golden-production-project.qa.json");
    if (!fs.existsSync(snapshotPath)) {
      fs.writeFileSync(snapshotPath, JSON.stringify(report, null, 2), "utf-8");
    }

    const savedSnapshot = JSON.parse(fs.readFileSync(snapshotPath, "utf-8"));
    assert.equal(report.checksumSha256, savedSnapshot.checksumSha256);
    assert.equal(report.score, savedSnapshot.score);
  });

  it("produces deterministic diff report on modified golden project without regression", () => {
    const modified: EditorialDocument = {
      ...goldenProject,
      tracks: [
        {
          ...goldenProject.tracks[0],
          clips: [
            goldenProject.tracks[0].clips[0],
            {
              ...goldenProject.tracks[0].clips[1],
              timelineRange: { startSeconds: 5.0, durationSeconds: 8.0 }, // Extended by 3.0s
            },
          ],
        },
      ],
    };

    const diff1 = EditorialDiffEngine.diff(goldenProject, modified);
    const diff2 = EditorialDiffEngine.diff(goldenProject, modified);

    assert.equal(diff1.checksumSha256, diff2.checksumSha256);
    assert.equal(diff1.summary.durationDeltaSeconds, 3.0);
    assert.equal(diff1.totalChanges, 1);
  });
});
