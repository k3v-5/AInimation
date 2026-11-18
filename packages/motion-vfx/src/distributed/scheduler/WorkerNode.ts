import { TaskDefinition } from "../tasks/TaskDefinition.js";
import { TaskResult, createTaskResult } from "../tasks/TaskResult.js";
import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";

export type WorkerState = "idle" | "busy" | "draining" | "offline";

export interface WorkerCapabilities {
  supportedTaskTypes: string[];
  maxConcurrentTasks: number;
  cpuUnits: number;
  memoryMb: number;
}

export class WorkerNode {
  public state: WorkerState = "idle";
  public activeTasks: Map<string, TaskDefinition> = new Map();
  public lastHeartbeatLogical: number = 0;

  constructor(
    public readonly workerId: string,
    public readonly capabilities: WorkerCapabilities = {
      supportedTaskTypes: ["plan_story", "edit_timeline", "design_motion", "mix_audio", "render_chunk", "perceptual_qa", "mux_export"],
      maxConcurrentTasks: 2,
      cpuUnits: 4,
      memoryMb: 8192,
    }
  ) {}

  public canAccept(task: TaskDefinition): boolean {
    if (this.state !== "idle" && this.state !== "busy") return false;
    if (this.activeTasks.size >= this.capabilities.maxConcurrentTasks) return false;
    return this.capabilities.supportedTaskTypes.includes(task.type);
  }

  public assignTask(task: TaskDefinition): void {
    this.activeTasks.set(task.taskId, task);
    this.state = this.activeTasks.size >= this.capabilities.maxConcurrentTasks ? "busy" : "idle";
  }

  public async executeTask(task: TaskDefinition): Promise<TaskResult> {
    this.assignTask(task);

    // Simulación de cómputo determinista basado en el payload
    const outputPayload = {
      executedBy: this.workerId,
      taskType: task.type,
      status: "SUCCESS",
      processedKeys: Object.keys(task.payload).sort(),
    };

    const outputArtifacts: Record<string, string> = {
      [`artifact_${task.taskId}`]: ProjectSerializer.hashCanonical(outputPayload),
    };

    this.activeTasks.delete(task.taskId);
    this.state = this.activeTasks.size === 0 ? "idle" : "busy";

    return createTaskResult({
      taskId: task.taskId,
      workerId: this.workerId,
      success: true,
      outputPayload,
      outputArtifacts,
      durationTicks: 1,
    });
  }

  public heartbeat(logicalTime: number): void {
    this.lastHeartbeatLogical = logicalTime;
  }
}
