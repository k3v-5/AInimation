import { EditorialIssue, EditorialIssueCategory, EditorialQAContext } from "./editorial-qa-types.js";
import { EditorialIssueSeverity } from "./editorial-qa-severity.js";

/**
 * REQ-QA-005, REQ-QA-067: Contrato de regla de auditoría editorial.
 */
export interface EditorialQARule {
  id: string;
  version: string;
  category: EditorialIssueCategory;
  defaultSeverity: EditorialIssueSeverity;
  description: string;
  enabledByDefault: boolean;
  evaluate(context: EditorialQAContext): EditorialIssue[];
}

/**
 * REQ-QA-005: Registro estático y determinista de reglas QA.
 * Prohibido descubrimiento dinámico desde filesystem.
 */
export class EditorialQARegistry {
  private static rules = new Map<string, EditorialQARule>();

  public static register(rule: EditorialQARule): void {
    this.rules.set(rule.id, rule);
  }

  public static getRule(id: string): EditorialQARule | undefined {
    return this.rules.get(id);
  }

  public static getAllRules(): EditorialQARule[] {
    // Deterministic order sorted by rule ID
    return Array.from(this.rules.values()).sort((a, b) => a.id.localeCompare(b.id));
  }

  public static getEnabledRules(enabledRuleIds?: string[]): EditorialQARule[] {
    const all = this.getAllRules();
    if (!enabledRuleIds || enabledRuleIds.length === 0) {
      return all.filter((r) => r.enabledByDefault);
    }
    const filterSet = new Set(enabledRuleIds);
    return all.filter((r) => filterSet.has(r.id));
  }

  public static clear(): void {
    this.rules.clear();
  }

  public static evaluate(context: any): any[] {
    const rules = this.getEnabledRules(context.config?.enabledRules);
    const issues: any[] = [];
    for (const rule of rules) {
      issues.push(...rule.evaluate(context));
    }
    return issues;
  }
}
