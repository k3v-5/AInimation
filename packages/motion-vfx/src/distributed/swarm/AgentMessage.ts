import { AgentRole } from "./AgentRole.js";
import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";

export interface AgentMessage {
  messageId: string;
  senderRole: AgentRole;
  recipientRole?: AgentRole | "broadcast";
  type: "task_assigned" | "proposal_submitted" | "conflict_detected" | "qa_feedback" | "step_completed";
  payload: Record<string, unknown>;
  sequenceNumber: number;
  deterministicHash: string;
}

export function createAgentMessage(params: {
  messageId: string;
  senderRole: AgentRole;
  recipientRole?: AgentRole | "broadcast";
  type: "task_assigned" | "proposal_submitted" | "conflict_detected" | "qa_feedback" | "step_completed";
  payload?: Record<string, unknown>;
  sequenceNumber: number;
}): AgentMessage {
  const payload = params.payload ?? {};
  const recipientRole = params.recipientRole ?? "broadcast";

  const deterministicHash = ProjectSerializer.hashCanonical({
    messageId: params.messageId,
    senderRole: params.senderRole,
    recipientRole,
    type: params.type,
    payload,
    sequenceNumber: params.sequenceNumber,
  });

  return {
    messageId: params.messageId,
    senderRole: params.senderRole,
    recipientRole,
    type: params.type,
    payload,
    sequenceNumber: params.sequenceNumber,
    deterministicHash,
  };
}
