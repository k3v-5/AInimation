import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  PacingConflictResolver,
  PacingConflictSchema,
} from "../../../vlog/index.js";

describe("Milestone 5 — Pacing Conflict Resolution Suite", () => {
  it("creates detailed conflicts and validates against PacingConflictSchema", () => {
    const conflict = PacingConflictResolver.createConflict({
      segmentId: "seg_intro_01",
      locale: "es-MX",
      conflictType: "STRETCH_LIMIT_EXCEEDED",
      severity: "BLOCKING",
      unresolvedDeltaSeconds: 3.5,
      requiredVoiceStretch: 1.25,
      measuredValue: 1.25,
      allowedValue: 1.05,
      suggestedAction: "MANUAL_SCRIPT_EDIT",
      description: "Voice duration is 25% longer than video, exceeding automatic 1.05x ceiling",
    });

    assert.equal(conflict.conflictType, "STRETCH_LIMIT_EXCEEDED");
    assert.equal(conflict.severity, "BLOCKING");
    assert.equal(conflict.requiredVoiceStretch, 1.25);

    // Validación formal Zod del esquema M1
    assert.doesNotThrow(() => PacingConflictSchema.parse(conflict));
  });

  it("handles anchor drift conflict with suggested pause insertion", () => {
    const conflict = PacingConflictResolver.createConflict({
      segmentId: "anchor_hook_01",
      locale: "en-US",
      conflictType: "ANCHOR_DRIFT",
      severity: "WARNING",
      unresolvedDeltaSeconds: 0.080,
      requiredVoiceStretch: 1.0,
      measuredValue: 0.080,
      allowedValue: 0.040,
      suggestedAction: "ADD_PAUSE",
      description: "Hook anchor shifted by 80ms into warning zone",
    });

    assert.equal(conflict.suggestedAction, "ADD_PAUSE");
    assert.doesNotThrow(() => PacingConflictSchema.parse(conflict));
  });
});
