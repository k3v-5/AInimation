import { QARule, QAIssue, EditorialDocument, QARuleContext } from "../../contracts/editorial-qa.types.js";
import { QAId } from "../qa-id.js";

export const NarrativeRules: QARule[] = [
  {
    id: "QA-NARR-001",
    description: "Validates required narrative beats in documentary profile",
    severity: "BLOCKING",
    evaluate(doc: EditorialDocument, ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      const profile = ctx.profile ?? doc.metadata.profile;
      if (profile === "DOCUMENTARY" || profile === "DOCUMENTARY_INVESTIGATIVE") {
        const docBeats = (doc as any).beats as Array<{ id: string; type: string }> | undefined;
        if (docBeats && docBeats.length > 0) {
          const beatTypes = new Set(docBeats.map((b) => b.type));
          const mandatory = ["HOOK", "EVIDENCE", "REVELATION"];
          for (const m of mandatory) {
            if (!beatTypes.has(m)) {
              issues.push({
                id: QAId.createIssueId({
                  ruleId: "QA-NARR-001",
                  entityIds: [doc.projectId],
                  severity: "BLOCKING",
                  fingerprint: `missing_beat_${m}`,
                }),
                ruleId: "QA-NARR-001",
                severity: "BLOCKING",
                title: "Missing Mandatory Narrative Beat",
                message: `Documentary project '${doc.projectId}' is missing required '${m}' beat.`,
                entityIds: [doc.projectId],
                expectedValue: m,
                confidence: 1.0,
                autoFixAvailable: false,
                fingerprint: `missing_beat_${m}`,
              });
            }
          }
        }
      }
      return issues;
    },
  },
  {
    id: "QA-NARR-003",
    description: "Detects absence of resolution/reflection in documentary",
    severity: "WARNING",
    evaluate(doc: EditorialDocument, ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      const profile = ctx.profile ?? doc.metadata.profile;
      if (profile === "DOCUMENTARY") {
        const docBeats = (doc as any).beats as Array<{ id: string; type: string }> | undefined;
        if (docBeats && docBeats.length > 0) {
          const hasResolution = docBeats.some((b) => b.type === "RESOLUTION" || b.type === "REFLECTION");
          if (!hasResolution) {
            issues.push({
              id: QAId.createIssueId({
                ruleId: "QA-NARR-003",
                entityIds: [doc.projectId],
                severity: "WARNING",
                fingerprint: "missing_resolution",
              }),
              ruleId: "QA-NARR-003",
              severity: "WARNING",
              title: "Missing Dramatic Resolution",
              message: "Documentary structure ends abruptly without RESOLUTION or REFLECTION beat.",
              entityIds: [doc.projectId],
              confidence: 0.85,
              autoFixAvailable: false,
              fingerprint: "missing_resolution",
            });
          }
        }
      }
      return issues;
    },
  },
];
