import { TransportEnvelope } from "./TransportEnvelope.js";

export interface MessageTransport {
  send<T>(envelope: TransportEnvelope<T>): Promise<void>;
  receive<T>(recipient: string): Promise<TransportEnvelope<T>[]>;
  clear(): Promise<void>;
}
