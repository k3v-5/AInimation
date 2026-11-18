import { EditorialQAFinding, EditorialSeverity } from "./editorial-qa-finding.js";
import { EditorialQAProfile } from "./editorial-qa-profile.js";

export interface EditorialQAContext {
  ir: any;
  profile?: Partial<EditorialQAProfile>;
  metadata?: Record<string, unknown>;
  evidenceReport?: any;
  cognitiveAnalysis?: any;
  pacingAnalysis?: any;
  continuityReport?: any;
  attentionCurve?: any;
  contrastReport?: any;
  [key: string]: unknown;
}

export interface EditorialQARule {
  readonly id: string;
  readonly description: string;
  readonly severity: EditorialSeverity;

  evaluate(context: EditorialQAContext): EditorialQAFinding[];
}
