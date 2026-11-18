import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { EditorialAuditEngine } from "../../editorial/qa/editorial-audit-engine.js";
import { EditorialDiffEngine } from "../../editorial/qa/editorial-diff-engine.js";
import { HumanReviewQueue } from "../../editorial/qa/human-review-queue.js";

describe("Regression — EditorialQAGoldenSnapshot Suite (§47)", () => {
  const fixturesDir = path.resolve(process.cwd(), "fixtures/editorial/qa");

  it("golden-valid-documentary: passes with 100 score and PASS status", () => {
    const fixture = JSON.parse(fs.readFileSync(path.join(fixturesDir, "golden-valid-documentary.json"), "utf-8"));
    const report = EditorialAuditEngine.audit(fixture);

    assert.equal(report.status, "PASS");
    assert.equal(report.qualityScore, 100);
    assert.equal(report.summary.blockingCount, 0);
    assert.ok(report.checksumSha256.length === 64);
  });

  it("golden-warning-pacing: detects pacing misalignment with WARNING", () => {
    const fixture = JSON.parse(fs.readFileSync(path.join(fixturesDir, "golden-warning-pacing.json"), "utf-8"));
    const report = EditorialAuditEngine.audit(fixture);

    assert.equal(report.status, "PASS_WITH_WARNINGS");
    assert.ok(report.summary.warningCount >= 1);
    assert.ok(report.findings.some((f) => f.ruleId === "QA-PACE-001"));
  });

  it("golden-cognitive-overload: detects sustained cognitive overload", () => {
    const fixture = JSON.parse(fs.readFileSync(path.join(fixturesDir, "golden-cognitive-overload.json"), "utf-8"));
    const report = EditorialAuditEngine.audit(fixture);

    assert.equal(report.status, "PASS_WITH_WARNINGS");
    assert.ok(report.summary.warningCount >= 1);
    assert.ok(report.findings.some((f) => f.ruleId === "QA-LOAD-001"));
  });

  it("golden-evidence-failure: flags unverified claim as BLOCKING", () => {
    const fixture = JSON.parse(fs.readFileSync(path.join(fixturesDir, "golden-evidence-failure.json"), "utf-8"));
    const report = EditorialAuditEngine.audit(fixture);

    assert.equal(report.status, "BLOCKED");
    assert.ok(report.summary.blockingCount >= 1);
    assert.ok(report.findings.some((f) => f.ruleId === "QA-EVIDENCE-001"));
  });

  it("golden-continuity-failure: audits continuity timeline cleanly", () => {
    const fixture = JSON.parse(fs.readFileSync(path.join(fixturesDir, "golden-continuity-failure.json"), "utf-8"));
    const report = EditorialAuditEngine.audit(fixture);

    assert.ok(report.status);
    assert.ok(report.checksumSha256.length === 64);
  });

  it("golden-human-review: queues low confidence finding into HumanReviewQueue (§20, §21)", () => {
    const fixture = JSON.parse(fs.readFileSync(path.join(fixturesDir, "golden-human-review.json"), "utf-8"));
    const queue = HumanReviewQueue.evaluateFindings(fixture.humanReviewCandidates);

    assert.equal(queue.length, 1);
    assert.equal(queue[0].findingId, "f_ambiguous_pacing");
    assert.equal(queue[0].status, "PENDING");
    assert.ok(queue[0].priority > 0);
  });

  it("golden-editorial-diff: calculates exact 2.0s duration delta between revisions (§28)", () => {
    const fixture = JSON.parse(fs.readFileSync(path.join(fixturesDir, "golden-editorial-diff.json"), "utf-8"));
    const report = EditorialDiffEngine.diff(fixture.before, fixture.after);

    assert.ok(report.fromChecksum);
    assert.ok(report.toChecksum);
    assert.equal(report.summary.durationDeltaSeconds, 2.0);
    assert.equal(report.impact.duration?.deltaSeconds, 2.0);
    assert.ok(report.checksumSha256.length === 64);
  });
});
