import { SyncEvent, SyncGroup } from "../types/index.js";

/**
 * Grafo de sincronización audiovisual unificado (*Sync Event Graph*) (Fase 13).
 */
export class SyncEventGraph {
  private syncGroups: SyncGroup[] = [];

  public createSyncGroup(
    id: string,
    time: number,
    name: string,
    events: Omit<SyncEvent, "id">[]
  ): SyncGroup {
    const group: SyncGroup = {
      id,
      time,
      name,
      events: events.map((e, idx) => ({ ...e, id: `${id}_evt_${idx}` })),
    };
    this.syncGroups.push(group);
    return group;
  }

  public getGroups(): SyncGroup[] {
    return this.syncGroups;
  }

  public getEventsAt(t: number, tolerance = 0.05): SyncEvent[] {
    const matched: SyncEvent[] = [];
    for (const group of this.syncGroups) {
      if (Math.abs(group.time - t) <= tolerance) {
        matched.push(...group.events);
      }
    }
    return matched;
  }
}
