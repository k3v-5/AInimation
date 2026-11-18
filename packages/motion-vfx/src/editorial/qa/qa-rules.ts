import { QARule, QAIssue, EditorialDocument, QARuleContext } from "../contracts/editorial-qa.types.js";
import { TimelineRules } from "./rules/timeline.rules.js";
import { ContinuityRules } from "./rules/continuity.rules.js";
import { NarrativeRules } from "./rules/narrative.rules.js";
import { EvidenceRules } from "./rules/evidence.rules.js";
import { CognitiveRules } from "./rules/cognitive.rules.js";
import { PacingRules } from "./rules/pacing.rules.js";
import { VisualRules } from "./rules/visual.rules.js";
import { AudioRules } from "./rules/audio.rules.js";
import { ExportRules } from "./rules/export.rules.js";
import { SafetyRules } from "./rules/safety.rules.js";

export type QAEvaluationContext = any;

/**
 * REQ-030 §8: Explicit Deterministic QA Rules Registry
 */
export class QARulesRegistry {
  private static readonly RULES: QARule[] = [
    ...TimelineRules,
    ...ContinuityRules,
    ...NarrativeRules,
    ...EvidenceRules,
    ...CognitiveRules,
    ...PacingRules,
    ...VisualRules,
    ...AudioRules,
    ...ExportRules,
    ...SafetyRules,
  ];

  public static getAllRules(): readonly QARule[] {
    return this.RULES;
  }

  public static evaluateAll(doc: EditorialDocument, context: QARuleContext = {}): QAIssue[] {
    const issues: QAIssue[] = [];
    for (const rule of this.RULES) {
      const ruleIssues = rule.evaluate(doc, context);
      issues.push(...ruleIssues);
    }

    // Canonical sorting of issues:
    // severity -> category/ruleId -> timestamp -> issueId
    const severityOrder = { BLOCKING: 0, WARNING: 1, SUGGESTION: 2 };
    return issues.sort((a, b) => {
      const sDiff = severityOrder[a.severity] - severityOrder[b.severity];
      if (sDiff !== 0) return sDiff;
      const tA = a.timestampSeconds ?? -1;
      const tB = b.timestampSeconds ?? -1;
      if (tA !== tB) return tA - tB;
      const rDiff = a.ruleId.localeCompare(b.ruleId);
      if (rDiff !== 0) return rDiff;
      return a.id.localeCompare(b.id);
    });
  }
}
