import { RenderGraph, RenderNode } from "../graph/RenderGraph.js";
import { FrameScheduler } from "../scheduler/FrameScheduler.js";
import {
  OutputProfile,
  RenderFrame,
  RenderJob,
  RenderManifest,
  RenderProgress,
} from "../types/index.js";
import { RenderValidator } from "../validation/RenderValidator.js";

/**
 * Pipeline principal de renderizado audiovisual de extremo a extremo (Fase 9).
 */
export class RenderPipeline {
  /**
   * Ejecuta un trabajo de renderizado produciendo el flujo de fotogramas y el manifiesto final.
   */
  public static async executeJob(
    job: RenderJob,
    onProgress?: (progress: RenderProgress) => void
  ): Promise<{ manifest: RenderManifest; frames: RenderFrame[] }> {
    job.state = "preparing";

    const totalDuration = job.range ? job.range.duration : 10.0;
    const fps = job.outputProfile.fps;
    const totalFrames = Math.max(1, Math.round(totalDuration * fps));
    const width = Math.round(job.outputProfile.width * job.settings.resolutionScale);
    const height = Math.round(job.outputProfile.height * job.settings.resolutionScale);

    // 1. Inicializar Render Graph
    const graph = new RenderGraph();
    const rootNode: RenderNode = {
      id: "root_output",
      type: "output",
      inputs: [],
      parameters: { width, height, codec: job.outputProfile.codec },
      cacheable: true,
    };
    graph.addNode(rootNode);

    job.state = "rendering";
    const renderedFrames: RenderFrame[] = [];

    // 2. Iterar fotogramas a través del FrameScheduler
    for await (const context of FrameScheduler.generateFrames(
      totalFrames,
      fps,
      width,
      height,
      onProgress
    )) {
      const frame = graph.evaluateNode("root_output", context, job.rendererVersion);
      renderedFrames.push(frame);
    }

    job.state = "completed";

    // 3. Generar Manifiesto de Render
    const manifest: RenderManifest = {
      jobId: job.id,
      projectId: job.projectId,
      rendererVersion: job.rendererVersion,
      framesCompleted: renderedFrames.length,
      totalFrames,
      outputProfile: job.outputProfile,
      outputPath: `/exports/${job.id}.${job.outputProfile.container}`,
      duration: totalDuration,
      completedAt: new Date().toISOString(),
    };

    // 4. Validar especificaciones
    const validation = RenderValidator.validateOutput(
      {
        width,
        height,
        fps,
        duration: totalDuration,
        codec: job.outputProfile.codec,
        framesRendered: renderedFrames.length,
      },
      {
        ...job.outputProfile,
        width,
        height,
      },
      totalDuration
    );

    if (!validation.valid) {
      job.state = "failed";
      throw new Error(`RENDER_VALIDATION_FAILED: ${validation.issues.join(" | ")}`);
    }

    return { manifest, frames: renderedFrames };
  }
}
