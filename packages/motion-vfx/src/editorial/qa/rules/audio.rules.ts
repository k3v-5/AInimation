import { QARule, QAIssue, EditorialDocument, QARuleContext } from "../../contracts/editorial-qa.types.js";
import { QAId } from "../qa-id.js";

export const AudioRules: QARule[] = [
  {
    id: "QA-AUD-001",
    description: "Detects audio volume clipping risks (> 0 dB)",
    severity: "WARNING",
    evaluate(doc: EditorialDocument, _ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      for (const track of doc.tracks) {
        for (const clip of track.clips) {
          if (clip.volumeDb > 0.0) {
            issues.push({
              id: QAId.createIssueId({
                ruleId: "QA-AUD-001",
                entityIds: [clip.id],
                timestampSeconds: clip.timelineRange.startSeconds,
                severity: "WARNING",
                fingerprint: `audio_clipping_${clip.id}`,
              }),
              ruleId: "QA-AUD-001",
              severity: "WARNING",
              title: "Audio Volume Clipping Risk",
              message: `Clip '${clip.id}' has volumeDb ${clip.volumeDb} dB > 0.0 dB, risk of acoustic distortion.`,
              timestampSeconds: clip.timelineRange.startSeconds,
              entityIds: [clip.id],
              actualValue: clip.volumeDb,
              threshold: 0.0,
              confidence: 0.95,
              autoFixAvailable: true,
              fingerprint: `audio_clipping_${clip.id}`,
            });
          }
        }
      }
      return issues;
    },
  },
  {
    id: "QA-AUD-002",
    description: "Detecta violación crítica de True Peak (> -1.0 dBTP)",
    severity: "BLOCKING",
    evaluate(doc: EditorialDocument, _ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      const truePeak = (doc as any).audioLoudness?.truePeakDb;
      if (truePeak !== undefined && truePeak > -1.0) {
        issues.push({
          id: QAId.createIssueId({
            ruleId: "QA-AUD-002",
            entityIds: [doc.projectId],
            timestampSeconds: 0,
            severity: "BLOCKING",
            fingerprint: "true_peak_violation",
          }),
          ruleId: "QA-AUD-002",
          severity: "BLOCKING",
          title: "True Peak Limit Exceeded",
          message: `True Peak medido de ${truePeak} dBTP excede el límite máximo admisible (-1.0 dBTP).`,
          entityIds: [doc.projectId],
          actualValue: truePeak,
          threshold: -1.0,
          confidence: 1.0,
          autoFixAvailable: true,
          fingerprint: "true_peak_violation",
        });
      }
      return issues;
    },
  },
  {
    id: "QA-AUD-003",
    description: "Valida que el sample rate del proyecto sea canónico (44.1 kHz o 48 kHz)",
    severity: "BLOCKING",
    evaluate(doc: EditorialDocument, _ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      const sr = doc.metadata?.sampleRate;
      if (sr && sr !== 44100 && sr !== 48000) {
        issues.push({
          id: QAId.createIssueId({
            ruleId: "QA-AUD-003",
            entityIds: [doc.projectId],
            timestampSeconds: 0,
            severity: "BLOCKING",
            fingerprint: `invalid_sample_rate_${sr}`,
          }),
          ruleId: "QA-AUD-003",
          severity: "BLOCKING",
          title: "Invalid Audio Sample Rate",
          message: `La frecuencia de muestreo de audio (${sr} Hz) no es un estándar canónico admitido (44.1 kHz o 48 kHz).`,
          entityIds: [doc.projectId],
          actualValue: sr,
          expectedValue: "44100 | 48000",
          confidence: 1.0,
          autoFixAvailable: false,
          fingerprint: `invalid_sample_rate_${sr}`,
        });
      }
      return issues;
    },
  },
];
