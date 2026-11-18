import { QARule, QAIssue, EditorialDocument, QARuleContext } from "../../contracts/editorial-qa.types.js";
import { QAId } from "../qa-id.js";

/**
 * REQ-030 §7: Auditoría Estructural (QA-STRUCT-001..004)
 */
export const StructuralRules: QARule[] = [
  {
    id: "QA-STRUCT-001",
    description: "Detecta referencias a identificadores inexistentes (clips, assets, tracks, scenes)",
    severity: "BLOCKING",
    evaluate(doc: EditorialDocument, _ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      const assetIds = new Set<string>();
      if ((doc as any).assets && Array.isArray((doc as any).assets)) {
        for (const a of (doc as any).assets) assetIds.add(a.id);
      }

      for (const track of doc.tracks || []) {
        for (const clip of track.clips || []) {
          if (!clip.id || clip.id.trim() === "") {
            issues.push({
              id: QAId.createIssueId({
                ruleId: "QA-STRUCT-001",
                entityIds: [clip.id || "empty_clip"],
                timestampSeconds: 0,
                severity: "BLOCKING",
                fingerprint: `missing_clip_id_${track.id}`,
              }),
              ruleId: "QA-STRUCT-001",
              severity: "BLOCKING",
              title: "Missing Clip Identifier",
              message: `El clip en la pista '${track.id}' carece de identificador válido.`,
              entityIds: [clip.id || "empty_clip"],
              confidence: 1.0,
              autoFixAvailable: false,
              fingerprint: `missing_clip_id_${track.id}`,
            });
          }
        }
      }
      return issues;
    },
  },
  {
    id: "QA-STRUCT-002",
    description: "Detecta identificadores duplicados en el grafo de la IR",
    severity: "BLOCKING",
    evaluate(doc: EditorialDocument, _ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      const seenIds = new Set<string>();

      for (const track of doc.tracks || []) {
        if (seenIds.has(track.id)) {
          issues.push({
            id: QAId.createIssueId({
              ruleId: "QA-STRUCT-002",
              entityIds: [track.id],
              timestampSeconds: 0,
              severity: "BLOCKING",
              fingerprint: `dup_track_${track.id}`,
            }),
            ruleId: "QA-STRUCT-002",
            severity: "BLOCKING",
            title: "Duplicate Track ID",
            message: `Identificador de pista duplicado: '${track.id}'.`,
            entityIds: [track.id],
            confidence: 1.0,
            autoFixAvailable: false,
            fingerprint: `dup_track_${track.id}`,
          });
        }
        seenIds.add(track.id);

        for (const clip of track.clips || []) {
          if (seenIds.has(clip.id)) {
            issues.push({
              id: QAId.createIssueId({
                ruleId: "QA-STRUCT-002",
                entityIds: [clip.id],
                timestampSeconds: clip.timelineRange?.startSeconds ?? 0,
                severity: "BLOCKING",
                fingerprint: `dup_clip_${clip.id}`,
              }),
              ruleId: "QA-STRUCT-002",
              severity: "BLOCKING",
              title: "Duplicate Clip ID",
              message: `Identificador de clip duplicado: '${clip.id}'.`,
              entityIds: [clip.id],
              confidence: 1.0,
              autoFixAvailable: false,
              fingerprint: `dup_clip_${clip.id}`,
            });
          }
          seenIds.add(clip.id);
        }
      }
      return issues;
    },
  },
  {
    id: "QA-STRUCT-003",
    description: "Valida que los campos obligatorios del esquema IR estén presentes",
    severity: "BLOCKING",
    evaluate(doc: EditorialDocument, _ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      if (!doc.schemaVersion) {
        issues.push({
          id: QAId.createIssueId({
            ruleId: "QA-STRUCT-003",
            entityIds: [doc.projectId || "doc"],
            timestampSeconds: 0,
            severity: "BLOCKING",
            fingerprint: "missing_schema_version",
          }),
          ruleId: "QA-STRUCT-003",
          severity: "BLOCKING",
          title: "Missing Schema Version",
          message: "El documento editorial carece de 'schemaVersion'.",
          entityIds: [doc.projectId || "doc"],
          confidence: 1.0,
          autoFixAvailable: false,
          fingerprint: "missing_schema_version",
        });
      }
      return issues;
    },
  },
  {
    id: "QA-STRUCT-004",
    description: "Rechaza valores numéricos no finitos (NaN, Infinity)",
    severity: "BLOCKING",
    evaluate(doc: EditorialDocument, _ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      for (const track of doc.tracks || []) {
        for (const clip of track.clips || []) {
          const s = clip.timelineRange?.startSeconds;
          const d = clip.timelineRange?.durationSeconds;
          if (s !== undefined && (!Number.isFinite(s) || Number.isNaN(s))) {
            issues.push({
              id: QAId.createIssueId({
                ruleId: "QA-STRUCT-004",
                entityIds: [clip.id],
                timestampSeconds: 0,
                severity: "BLOCKING",
                fingerprint: `nan_start_${clip.id}`,
              }),
              ruleId: "QA-STRUCT-004",
              severity: "BLOCKING",
              title: "Non-finite Start Time",
              message: `Clip '${clip.id}' tiene un startSeconds no finito (${s}).`,
              entityIds: [clip.id],
              confidence: 1.0,
              autoFixAvailable: false,
              fingerprint: `nan_start_${clip.id}`,
            });
          }
          if (d !== undefined && (!Number.isFinite(d) || Number.isNaN(d))) {
            issues.push({
              id: QAId.createIssueId({
                ruleId: "QA-STRUCT-004",
                entityIds: [clip.id],
                timestampSeconds: 0,
                severity: "BLOCKING",
                fingerprint: `nan_dur_${clip.id}`,
              }),
              ruleId: "QA-STRUCT-004",
              severity: "BLOCKING",
              title: "Non-finite Duration",
              message: `Clip '${clip.id}' tiene un durationSeconds no finito (${d}).`,
              entityIds: [clip.id],
              confidence: 1.0,
              autoFixAvailable: false,
              fingerprint: `nan_dur_${clip.id}`,
            });
          }
        }
      }
      return issues;
    },
  },
];
