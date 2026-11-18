export interface AgentPolicy {
  maxOperationsPerSession: number;
  allowedActionTypes: string[];
  allowDestructiveDeletions: boolean;
  maxDurationSeconds: number;
}

export const DefaultAgentPolicy: AgentPolicy = {
  maxOperationsPerSession: 500,
  allowedActionTypes: [
    "create_project",
    "modify_layer",
    "add_layer",
    "remove_layer",
    "apply_captions",
    "apply_preset",
    "trim_clip",
    "move_clip",
  ],
  allowDestructiveDeletions: true,
  maxDurationSeconds: 7200,
};

export class AgentMemory {
  private decisions: any[] = [];
  private observations: any[] = [];

  public logDecision(d: any): void {
    this.decisions.push(d);
  }

  public logObservation(o: any): void {
    this.observations.push(o);
  }

  public getDecisions(): any[] {
    return [...this.decisions];
  }

  public getObservations(): any[] {
    return [...this.observations];
  }

  public clear(): void {
    this.decisions = [];
    this.observations = [];
  }
}
