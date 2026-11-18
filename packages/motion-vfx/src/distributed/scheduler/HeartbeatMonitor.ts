import { WorkerPool } from "./WorkerPool.js";
import { TaskLease } from "../tasks/TaskLease.js";

export class HeartbeatMonitor {
  private _leases: Map<string, TaskLease> = new Map();

  constructor(private _pool: WorkerPool) {}

  public registerLease(lease: TaskLease): void {
    this._leases.set(lease.leaseId, { ...lease });
  }

  public recordHeartbeat(leaseId: string, currentLogicalTime: number): boolean {
    const lease = this._leases.get(leaseId);
    if (!lease || !lease.active) return false;

    lease.heartbeatCounter++;
    lease.expiresAtLogical = currentLogicalTime + 10; // extender lease
    return true;
  }

  public checkExpiredLeases(currentLogicalTime: number): TaskLease[] {
    const expired: TaskLease[] = [];
    for (const lease of this._leases.values()) {
      if (lease.active && currentLogicalTime > lease.expiresAtLogical) {
        lease.active = false;
        expired.push(lease);
      }
    }
    return expired;
  }

  public revokeLease(leaseId: string): void {
    const lease = this._leases.get(leaseId);
    if (lease) {
      lease.active = false;
    }
  }
}
