import { AgentRole } from "./AgentRole.js";
import { AgentProposal, createAgentProposal, ChangeSet } from "./AgentProposal.js";
import { TaskDefinition } from "../tasks/TaskDefinition.js";

export interface SwarmAgent {
  readonly role: AgentRole;
  processTask(task: TaskDefinition, baseRevisionId: string): Promise<AgentProposal>;
}

export class SpecializedSwarmAgent implements SwarmAgent {
  constructor(public readonly role: AgentRole) {}

  public async processTask(task: TaskDefinition, baseRevisionId: string): Promise<AgentProposal> {
    const changeSet: ChangeSet = {
      changeSetId: `cs_${this.role}_${task.taskId}`,
      description: `Executed task ${task.type} by ${this.role}`,
      operations: [
        {
          type: "set-metadata",
          targetId: "project_meta",
          property: `agent_${this.role}_task`,
          value: task.taskId,
        },
      ],
    };

    return createAgentProposal({
      proposalId: `prop_${this.role}_${task.taskId}`,
      agentRole: this.role,
      baseRevisionId,
      changeSet,
      confidence: 0.98,
      rationale: `Applied standard ${this.role} specialization for ${task.type}`,
    });
  }
}
