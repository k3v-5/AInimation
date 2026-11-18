import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ConflictArbitrator } from "../../ai-director/core/ConflictArbitrator.js";
import { AgentConflict } from "../../ai-director/types/index.js";

describe("Fase 8 — Conflict Arbitrator Tests", () => {
  it("arbitrates conflicting agent proposals selecting highest priority policy", () => {
    const conflict: AgentConflict = {
      agents: ["agent_story_01", "agent_visual_01"],
      conflictType: "timing",
      proposals: [
        {
          type: "narrative_timing",
          priority: 1, // Prioridad 1 (más alta)
          reasoning: "Narrative clarity requires exact 4s hook",
          parameters: { duration: 4.0 },
        },
        {
          type: "visual_timing",
          priority: 3,
          reasoning: "B-roll requires 6s",
          parameters: { duration: 6.0 },
        },
      ],
    };

    const resolution = ConflictArbitrator.resolve(conflict);
    assert.strictEqual(resolution.selectedProposalIndex, 1); // 3 > 1
    assert.strictEqual(resolution.resolvedParameters.duration, 6.0);
  });
});
