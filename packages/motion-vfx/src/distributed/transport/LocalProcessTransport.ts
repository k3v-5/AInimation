import { MessageTransport } from "./MessageTransport.js";
import { TransportEnvelope } from "./TransportEnvelope.js";

export class LocalProcessTransport implements MessageTransport {
  private _buffers: Map<string, TransportEnvelope<any>[]> = new Map();

  public async send<T>(envelope: TransportEnvelope<T>): Promise<void> {
    const buf = this._buffers.get(envelope.recipient) ?? [];
    buf.push(envelope);
    this._buffers.set(envelope.recipient, buf);
  }

  public async receive<T>(recipient: string): Promise<TransportEnvelope<T>[]> {
    const buf = this._buffers.get(recipient) ?? [];
    this._buffers.set(recipient, []);
    return buf;
  }

  public async clear(): Promise<void> {
    this._buffers.clear();
  }
}
