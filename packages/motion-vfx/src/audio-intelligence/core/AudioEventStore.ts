import { Time } from "../../core/types.js";
import { AudioEvent, AudioEventType } from "../types/index.js";

/**
 * Almacén y motor de consulta temporal de eventos acústicos (Fase 5I).
 */
export class AudioEventStore {
  private _events: AudioEvent[] = [];

  constructor(events: AudioEvent[] = []) {
    for (const e of events) {
      this.addEvent(e);
    }
  }

  public get events(): AudioEvent[] {
    return [...this._events];
  }

  public get size(): number {
    return this._events.length;
  }

  public addEvent(event: AudioEvent): this {
    this._events.push({ ...event });
    this._events.sort((a, b) => a.time - b.time);
    return this;
  }

  public getAt(time: Time, tolerance = 0.05): AudioEvent[] {
    return this._events.filter((e) => Math.abs(e.time - time) <= tolerance);
  }

  public getBetween(start: Time, end: Time): AudioEvent[] {
    const res: AudioEvent[] = [];
    let low = 0;
    let high = this._events.length - 1;
    let first = this._events.length;
    while (low <= high) {
      const mid = (low + high) >> 1;
      if (this._events[mid].time >= start) {
        first = mid;
        high = mid - 1;
      } else {
        low = mid + 1;
      }
    }
    for (let i = first; i < this._events.length; i++) {
      if (this._events[i].time > end) break;
      res.push(this._events[i]);
    }
    return res;
  }

  public getByType(type: AudioEventType): AudioEvent[] {
    return this._events.filter((e) => e.type === type);
  }

  public findNearest(time: Time, type?: AudioEventType): AudioEvent | undefined {
    let candidates = this._events;
    if (type) {
      candidates = candidates.filter((e) => e.type === type);
    }
    if (candidates.length === 0) return undefined;

    let closest = candidates[0];
    let minDiff = Math.abs(candidates[0].time - time);

    for (let i = 1; i < candidates.length; i++) {
      const diff = Math.abs(candidates[i].time - time);
      if (diff < minDiff) {
        minDiff = diff;
        closest = candidates[i];
      }
    }

    return closest;
  }
}
