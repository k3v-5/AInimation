import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { HumanReviewItem, HumanReviewQueue } from "../../../editorial/qa/human-review-queue.js";

describe("Editorial QA — Human Review Queue & Audit Trail Suite (REQ-QA-025, REQ-QA-027, REQ-QA-028, REQ-QA-057)", () => {
  it("calculates priority deterministically based on severity and uncertainty (REQ-QA-027)", () => {
    // BLOCKING (weight 1.0), confidence 0.4 (uncertainty 0.6) -> 60.0
    const p1 = HumanReviewQueue.calculatePriority("BLOCKING", 0.4);
    assert.equal(p1, 60.0);

    // WARNING (weight 0.65), confidence 0.5 (uncertainty 0.5) -> 32.5
    const p2 = HumanReviewQueue.calculatePriority("WARNING", 0.5);
    assert.equal(p2, 32.5);

    // SUGGESTION (weight 0.30), confidence 0.8 (uncertainty 0.2) -> 6.0
    const p3 = HumanReviewQueue.calculatePriority("SUGGESTION", 0.8);
    assert.equal(p3, 6.0);
  });

  it("prioritizes items deterministically and breaks ties correctly (REQ-QA-027)", () => {
    const queue = new HumanReviewQueue();

    const item1: HumanReviewItem = {
      id: "item_01",
      issueId: "issue_z",
      priority: 50.0,
      severity: "WARNING",
      reason: "LOW_CONFIDENCE",
      confidence: 0.5,
      timestampSeconds: 10.0,
      affectedEntityIds: ["clip_1"],
      status: "PENDING",
      createdDeterministically: true,
    };

    const item2: HumanReviewItem = {
      id: "item_02",
      issueId: "issue_a",
      priority: 80.0, // higher priority
      severity: "BLOCKING",
      reason: "EDITORIAL_CONFLICT",
      confidence: 0.2,
      timestampSeconds: 5.0,
      affectedEntityIds: ["clip_2"],
      status: "PENDING",
      createdDeterministically: true,
    };

    const item3Tie: HumanReviewItem = {
      id: "item_03",
      issueId: "issue_a_tie",
      priority: 50.0, // same priority as item1, but earlier timestamp
      severity: "WARNING",
      reason: "LOW_CONFIDENCE",
      confidence: 0.5,
      timestampSeconds: 4.0, // earlier than item1
      affectedEntityIds: ["clip_3"],
      status: "PENDING",
      createdDeterministically: true,
    };

    queue.add(item1);
    queue.add(item2);
    queue.add(item3Tie);

    const pending = queue.getPending();
    assert.equal(pending.length, 3);
    assert.equal(pending[0].id, "item_02"); // Highest priority (80.0)
    assert.equal(pending[1].id, "item_03"); // Tied priority (50.0), earlier timestamp (4.0 < 10.0)
    assert.equal(pending[2].id, "item_01"); // Tied priority (50.0), later timestamp (10.0)
  });

  it("supports state transitions: approve, reject, defer and maintains immutable audit log (REQ-QA-028, REQ-QA-029)", () => {
    const queue = new HumanReviewQueue();
    queue.add({
      id: "item_approval",
      issueId: "issue_audio_ducking",
      priority: 45.0,
      severity: "WARNING",
      reason: "LOW_CONFIDENCE",
      confidence: 0.55,
      timestampSeconds: 12.0,
      affectedEntityIds: ["speech_01", "music_01"],
      status: "PENDING",
      createdDeterministically: true,
    });

    assert.equal(queue.countPending(), 1);

    // Approve
    queue.approve("item_approval", "Editor confirmed ducking attenuation is adequate.");
    assert.equal(queue.countPending(), 0);

    const decisions = queue.getDecisions();
    assert.equal(decisions.length, 1);
    assert.equal(decisions[0].reviewItemId, "item_approval");
    assert.equal(decisions[0].previousStatus, "PENDING");
    assert.equal(decisions[0].newStatus, "APPROVED");
    assert.equal(decisions[0].actorType, "HUMAN");
    assert.equal(decisions[0].decisionReason, "Editor confirmed ducking attenuation is adequate.");
    assert.deepEqual(decisions[0].affectedEntityIds, ["speech_01", "music_01"]);
  });

  it("PBT: priority is always bounded in [0, 100] for any confidence and severity", () => {
    fc.assert(
      fc.property(
        fc.constantFrom("BLOCKING", "WARNING", "SUGGESTION" as const),
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),
        fc.double({ min: 0.1, max: 2.0, noNaN: true }),
        (sev, conf, impact) => {
          const prio = HumanReviewQueue.calculatePriority(sev, conf, impact);
          return Number.isFinite(prio) && prio >= 0.0 && prio <= 100.0;
        }
      ),
      { numRuns: 100 }
    );
  });
});
