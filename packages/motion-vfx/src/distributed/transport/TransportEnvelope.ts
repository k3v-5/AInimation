import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";

export interface TransportEnvelope<T = unknown> {
  messageId: string;
  sender: string;
  recipient: string;
  payload: T;
  sequence: number;
  checksum: string;
}

export function createTransportEnvelope<T>(params: {
  messageId: string;
  sender: string;
  recipient: string;
  payload: T;
  sequence: number;
}): TransportEnvelope<T> {
  const checksum = ProjectSerializer.hashCanonical({
    messageId: params.messageId,
    sender: params.sender,
    recipient: params.recipient,
    payload: params.payload,
    sequence: params.sequence,
  });

  return {
    messageId: params.messageId,
    sender: params.sender,
    recipient: params.recipient,
    payload: params.payload,
    sequence: params.sequence,
    checksum,
  };
}
