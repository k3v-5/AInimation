import { MessageTransport } from "./MessageTransport.js";
import { TransportEnvelope } from "./TransportEnvelope.js";

export class InMemoryTransport implements MessageTransport {
  private _queues: Map<string, TransportEnvelope<any>[]> = new Map();

  public async send<T>(envelope: TransportEnvelope<T>): Promise<void> {
    const list = this._queues.get(envelope.recipient) ?? [];
    list.push(envelope);
    this._queues.set(envelope.recipient, list);
  }

  public async receive<T>(recipient: string): Promise<TransportEnvelope<T>[]> {
    const list = this._queues.get(recipient) ?? [];
    this._queues.set(recipient, []);
    return list;
  }

  public async clear(): Promise<void> {
    this._queues.clear();
  }
}
