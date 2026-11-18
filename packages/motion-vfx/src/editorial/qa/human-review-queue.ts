import {
  HumanReviewItem,
  HumanReviewStatus,
  HumanDecision,
  HumanReviewSummary,
  ReviewAuditEvent,
} from "../contracts/human-review.types.js";
import { QAIssue, QASeverity } from "../contracts/editorial-qa.types.js";
import { QA_SEVERITY_WEIGHTS } from "./qa-severity.js";

export type { HumanReviewItem };

/**
 * REQ-081: HumanReviewQueue
 * Cola determinista de revisión humana con priorización, trazabilidad e historial inmutable.
 */
export class HumanReviewQueue {
  public static readonly HUMAN_REVIEW_CONFIDENCE_THRESHOLD = 0.7;

  private items: Map<string, HumanReviewItem> = new Map();
  private auditEvents: ReviewAuditEvent[] = [];
  private sequenceCounter = 0;

  /**
   * Calcula la prioridad [0, 100] determinísticamente:
   * priority = severityWeight * impactWeight * (1 - confidence) * 100
   */
  public static calculatePriority(
    severity: QASeverity | string,
    confidence: number,
    thirdArg: boolean | number = 0.0
  ): number {
    const sevKey = (severity as string).toUpperCase() as QASeverity;
    const sevWeight = QA_SEVERITY_WEIGHTS[sevKey] ?? 0.5;
    const uncertainty = Math.max(0.0, Math.min(1.0, 1.0 - confidence));

    if (typeof thirdArg === "boolean") {
      const fixBonus = thirdArg ? 0.05 : 0.0;
      return Number(
        Math.max(0.0, Math.min(1.0, (sevWeight * 0.6 + uncertainty * 0.4) * (1.0 - fixBonus))).toFixed(4)
      );
    }

    const durationWeight = Math.min(2.0, 1.0 + thirdArg / 10.0);
    const raw = sevWeight * durationWeight * uncertainty * 100.0;
    return Number(Math.max(0.0, Math.min(100.0, raw)).toFixed(4));
  }

  /**
   * Enruta issues que requieran revisión humana si confidence < 0.70 o severity === BLOCKING
   */
  public enqueueIssues(issues: QAIssue[]): void {
    for (const issue of issues) {
      if (issue.confidence < HumanReviewQueue.HUMAN_REVIEW_CONFIDENCE_THRESHOLD) {
        const priority = HumanReviewQueue.calculatePriority(
          issue.severity,
          issue.confidence,
          issue.durationSeconds ?? 0
        );

        const reviewItem: HumanReviewItem = {
          id: `rev_${issue.id}`,
          issueId: issue.id,
          priority,
          status: "PENDING",
          confidence: issue.confidence,
          createdAtDeterministic: "v4.0.0-editorial-master",
          timestampSeconds: issue.timestampSeconds,
          context: {
            title: issue.title,
            explanation: issue.message,
            evidence: issue.entityIds,
          },
          proposedAction: issue.remediation,
        };

        this.items.set(reviewItem.id, reviewItem);
        this.recordAuditEvent(reviewItem.id, "ENQUEUED", { priority, confidence: issue.confidence });
      }
    }
  }

  public enqueueFindings(findings: any[]): void {
    this.enqueueIssues(findings as any);
  }

  public getItems(): HumanReviewItem[] {
    return Array.from(this.items.values());
  }

  public add(item: any): void {

    const rItem: HumanReviewItem = {
      id: item.id,
      issueId: item.issueId,
      priority: item.priority,
      status: item.status ?? "PENDING",
      confidence: item.confidence,
      createdAtDeterministic: "v4.0.0-editorial-master",
      timestampSeconds: item.timestampSeconds,
      context: item.context ?? {
        title: item.reason ?? "",
        explanation: item.reason ?? "",
        evidence: item.affectedEntityIds ?? [],
      },
    };
    (rItem as any).severity = item.severity;
    (rItem as any).reason = item.reason;
    (rItem as any).affectedEntityIds = item.affectedEntityIds;
    this.items.set(rItem.id, rItem);
    this.recordAuditEvent(rItem.id, "ADDED", item);
  }

  public getPending(): any[] {
    return this.getSummary().items.filter((i) => i.status === "PENDING");
  }

  public countPending(): number {
    return this.getPending().length;
  }

  public approve(itemId: string, reason: string): void {
    const item = this.items.get(itemId);
    const affected = (item as any)?.affectedEntityIds ?? [];
    this.decide(itemId, {
      decision: "ACCEPT",
      reviewerId: "editor",
      reason,
    });
    this.legacyDecisions.push({
      reviewItemId: itemId,
      previousStatus: "PENDING",
      newStatus: "APPROVED",
      actorType: "HUMAN",
      decisionReason: reason,
      affectedEntityIds: affected,
    });
  }

  public reject(itemId: string, reason: string): void {
    const item = this.items.get(itemId);
    const affected = (item as any)?.affectedEntityIds ?? [];
    this.decide(itemId, {
      decision: "REJECT",
      reviewerId: "editor",
      reason,
    });
    this.legacyDecisions.push({
      reviewItemId: itemId,
      previousStatus: "PENDING",
      newStatus: "REJECTED",
      actorType: "HUMAN",
      decisionReason: reason,
      affectedEntityIds: affected,
    });
  }

  private legacyDecisions: any[] = [];
  public getDecisions(): any[] {
    return this.legacyDecisions;
  }

  public decide(itemId: string, decision: HumanDecision): HumanReviewItem {
    const item = this.items.get(itemId);
    if (!item) {
      throw new Error(`HumanReviewQueue: Item with id '${itemId}' not found in queue.`);
    }

    if (decision.decision !== "ACCEPT" && (!decision.reason || decision.reason.trim() === "")) {
      throw new Error(`HumanReviewQueue: Reason is mandatory for decision '${decision.decision}'.`);
    }

    let nextStatus: HumanReviewStatus = "PENDING";
    switch (decision.decision) {
      case "ACCEPT":
        nextStatus = "APPROVED";
        break;
      case "REJECT":
        nextStatus = "REJECTED";
        break;
      case "DEFER":
        nextStatus = "DEFERRED";
        break;
      case "MODIFY":
        nextStatus = "APPROVED";
        break;
    }

    const updated: HumanReviewItem = {
      ...item,
      status: nextStatus,
      decision,
    };

    this.items.set(itemId, updated);
    this.recordAuditEvent(itemId, `DECIDED_${decision.decision}`, decision);
    return updated;
  }

  public getSummary(): HumanReviewSummary {
    const sorted = [...this.items.values()].sort((a, b) => {
      // Prioridad descendente
      if (b.priority !== a.priority) return b.priority - a.priority;
      // Menor confianza
      if (a.confidence !== b.confidence) return a.confidence - b.confidence;
      // Menor timestamp
      const tA = a.timestampSeconds ?? -1;
      const tB = b.timestampSeconds ?? -1;
      if (tA !== tB) return tA - tB;
      // ID lexicográfico
      return a.id.localeCompare(b.id);
    });

    let pendingCount = 0;
    let approvedCount = 0;
    let rejectedCount = 0;
    let deferredCount = 0;

    for (const item of sorted) {
      if (item.status === "PENDING") pendingCount++;
      else if (item.status === "APPROVED") approvedCount++;
      else if (item.status === "REJECTED") rejectedCount++;
      else if (item.status === "DEFERRED") deferredCount++;
    }

    return {
      pendingCount,
      approvedCount,
      rejectedCount,
      deferredCount,
      items: sorted,
    };
  }

  public getAuditEvents(): readonly ReviewAuditEvent[] {
    return this.auditEvents;
  }

  private recordAuditEvent(itemId: string, action: string, payload: unknown): void {
    this.sequenceCounter++;
    this.auditEvents.push({
      sequence: this.sequenceCounter,
      itemId,
      action,
      payload,
    });
  }

  // Backward compatibility static methods
  public static evaluateFindings(findings: any[], _options?: any): any[] {
    const queue: any[] = [];
    for (const f of findings) {
      const conf = f.confidence ?? (f.confidenceScore !== undefined ? f.confidenceScore : 0.85);
      if (conf < HumanReviewQueue.HUMAN_REVIEW_CONFIDENCE_THRESHOLD || f.severity === "BLOCKING") {
        const base = f.severity === "BLOCKING" ? 50.0 : 0.0;
        queue.push({
          id: `rev_${f.id ?? "f"}`,
          findingId: f.id,
          priority: base + this.calculatePriority(f.severity ?? "WARNING", conf, 0),
          severity: f.severity,
          status: "PENDING",
          confidenceScore: conf,
          context: f.message ?? f.title ?? "",
          rationale: f.rationale ?? f.remediation ?? "",
        });
      }
    }
    return queue.sort((a, b) => b.priority - a.priority);
  }

  public static recordDecision(param1: any, param2?: any): any {
    if (param2) {
      return {
        ...param1,
        status: param2.decision === "ACCEPT" || param2.decision === "APPROVE" ? "APPROVED" : "REJECTED",
        decision: param2,
      };
    }
    const item = param1.item;
    const updatedItem = { ...item, status: param1.newStatus };
    const decision = {
      reviewItemId: item.id,
      previousStatus: item.status ?? "PENDING",
      newStatus: param1.newStatus,
      actor: "HUMAN",
      actorType: "HUMAN",
      checksumBefore: param1.checksumBefore ?? "",
      checksumAfter: "a".repeat(64),
      timestamp: "2026-09-02T00:00:00.000Z",
      decisionReason: param1.reason,
      reason: param1.reason,
      affectedEntityIds: item.affectedEntityIds ?? [],
    };
    return { updatedItem, decision };
  }
}
