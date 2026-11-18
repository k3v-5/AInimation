import { TaskDAG } from "./TaskDAG.js";
import { createTaskDefinition } from "./TaskDefinition.js";

export class TaskPlanner {
  /**
   * Compila un plan de producción distribuido en un grafo TaskDAG determinista.
   */
  public static planProduction(params: {
    jobId: string;
    chunkCount?: number;
    enablePerceptualQA?: boolean;
  }): TaskDAG {
    const dag = new TaskDAG();
    const chunks = Math.max(1, params.chunkCount ?? 2);

    // 1. Tarea de Story Planning (Director)
    const taskPlan = createTaskDefinition({
      taskId: `${params.jobId}_task_01_plan`,
      jobId: params.jobId,
      type: "plan_story",
      requiredRole: "director",
      dependencies: [],
      payload: { stage: "story_planning" },
    });
    dag.addTask(taskPlan);

    // 2. Tarea de Edición de Timeline (Editor)
    const taskEdit = createTaskDefinition({
      taskId: `${params.jobId}_task_02_edit`,
      jobId: params.jobId,
      type: "edit_timeline",
      requiredRole: "editor",
      dependencies: [taskPlan.taskId],
      payload: { stage: "timeline_assembly" },
    });
    dag.addTask(taskEdit);

    // 3. Tareas Concurrentes de Motion y Audio
    const taskMotion = createTaskDefinition({
      taskId: `${params.jobId}_task_03_motion`,
      jobId: params.jobId,
      type: "design_motion",
      requiredRole: "motion",
      dependencies: [taskEdit.taskId],
      payload: { stage: "kinetic_design" },
    });
    dag.addTask(taskMotion);

    const taskAudio = createTaskDefinition({
      taskId: `${params.jobId}_task_03_audio`,
      jobId: params.jobId,
      type: "mix_audio",
      requiredRole: "audio",
      dependencies: [taskEdit.taskId],
      payload: { stage: "audio_mixing" },
    });
    dag.addTask(taskAudio);

    // 4. Tareas de Renderizado en Chunks
    const renderTaskIds: string[] = [];
    for (let c = 0; c < chunks; c++) {
      const chunkId = `${params.jobId}_task_04_render_chunk_${c}`;
      const taskRender = createTaskDefinition({
        taskId: chunkId,
        jobId: params.jobId,
        type: "render_chunk",
        dependencies: [taskMotion.taskId, taskAudio.taskId],
        payload: { chunkIndex: c, totalChunks: chunks },
      });
      dag.addTask(taskRender);
      renderTaskIds.push(chunkId);
    }

    // 5. Tarea de QA Perceptual
    const taskQA = createTaskDefinition({
      taskId: `${params.jobId}_task_05_perceptual_qa`,
      jobId: params.jobId,
      type: "perceptual_qa",
      requiredRole: "qa_critic",
      dependencies: renderTaskIds,
      payload: { stage: "visual_audio_validation" },
    });
    dag.addTask(taskQA);

    // 6. Tarea de Exportación y Mux
    const taskMux = createTaskDefinition({
      taskId: `${params.jobId}_task_06_mux_export`,
      jobId: params.jobId,
      type: "mux_export",
      dependencies: [taskQA.taskId],
      payload: { stage: "final_delivery" },
    });
    dag.addTask(taskMux);

    return dag;
  }
}
