import { AgentRole } from "./AgentRole.js";
import { SwarmAgent, SpecializedSwarmAgent } from "./SwarmAgent.js";
import { AgentProposal } from "./AgentProposal.js";
import { AgentMessage, createAgentMessage } from "./AgentMessage.js";
import { TaskDefinition } from "../tasks/TaskDefinition.js";
import { ThreeWayMergeArbiter, MergeArbiterResult } from "./ThreeWayMergeArbiter.js";
import { SwarmCoordinationError } from "../core/DistributedErrors.js";

export class SwarmCoordinator {
  private _agents: Map<AgentRole, SwarmAgent> = new Map();
  private _messages: AgentMessage[] = [];
  private _sequence = 0;

  constructor() {
    // Registrar agentes especializados por defecto
    const defaultRoles: AgentRole[] = ["director", "editor", "motion", "audio", "qa_critic"];
    for (const role of defaultRoles) {
      this.registerAgent(new SpecializedSwarmAgent(role));
    }
  }

  public registerAgent(agent: SwarmAgent): this {
    this._agents.set(agent.role, agent);
    return this;
  }

  public getAgent(role: AgentRole): SwarmAgent | undefined {
    return this._agents.get(role);
  }

  public get messages(): AgentMessage[] {
    return [...this._messages];
  }

  public async dispatchTask(task: TaskDefinition, baseRevisionId: string): Promise<AgentProposal> {
    const role = (task.requiredRole as AgentRole) ?? "director";
    const agent = this._agents.get(role);

    if (!agent) {
      throw new SwarmCoordinationError(`No agent registered for role: ${role}`, { taskId: task.taskId });
    }

    this._sequence++;
    const msg = createAgentMessage({
      messageId: `msg_${this._sequence}`,
      senderRole: "director",
      recipientRole: role,
      type: "task_assigned",
      payload: { taskId: task.taskId, type: task.type },
      sequenceNumber: this._sequence,
    });
    this._messages.push(msg);

    const proposal = await agent.processTask(task, baseRevisionId);

    this._sequence++;
    const doneMsg = createAgentMessage({
      messageId: `msg_${this._sequence}`,
      senderRole: role,
      recipientRole: "director",
      type: "proposal_submitted",
      payload: { proposalId: proposal.proposalId, confidence: proposal.confidence },
      sequenceNumber: this._sequence,
    });
    this._messages.push(doneMsg);

    return proposal;
  }

  public mergeProposals(proposals: AgentProposal[], baseRevisionId: string): MergeArbiterResult {
    return ThreeWayMergeArbiter.merge(proposals, baseRevisionId);
  }
}
