import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";

export interface DistributedEvent {
  eventId: string;
  jobId: string;
  eventType: "task_scheduled" | "task_started" | "task_completed" | "task_failed" | "proposal_created" | "merge_completed" | "worker_scaled";
  payload: Record<string, unknown>;
  sequenceNumber: number;
  deterministicHash: string;
}

export class DistributedEventLog {
  private _events: DistributedEvent[] = [];
  private _seq = 0;

  public record(jobId: string, eventType: DistributedEvent["eventType"], payload: Record<string, unknown> = {}): DistributedEvent {
    this._seq++;
    const eventId = `devent_${jobId}_${this._seq}`;

    const deterministicHash = ProjectSerializer.hashCanonical({
      eventId,
      jobId,
      eventType,
      payload,
      sequenceNumber: this._seq,
    });

    const event: DistributedEvent = {
      eventId,
      jobId,
      eventType,
      payload,
      sequenceNumber: this._seq,
      deterministicHash,
    };

    this._events.push(event);
    return event;
  }

  public getEvents(jobId?: string): DistributedEvent[] {
    if (!jobId) return [...this._events];
    return this._events.filter((e) => e.jobId === jobId);
  }

  public get size(): number {
    return this._events.length;
  }
}
