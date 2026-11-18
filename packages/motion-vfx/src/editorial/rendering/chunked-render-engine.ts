import crypto from "crypto";

export interface ChunkedRenderSettings {
  codec: "PRORES_422_HQ" | "H264" | "DNXHR";
  width: number;
  height: number;
  fps: number;
  qualityCrf?: number;
}

export interface ChunkedRenderJob {
  jobId: string;
  sourceIrHash: string;
  totalDurationSeconds: number;
  fps: number;
  totalFrames: number;
  settings: ChunkedRenderSettings;
}

export interface RenderChunk {
  chunkId: string;
  jobId: string;
  chunkIndex: number;
  startTimeSeconds: number;
  endTimeSeconds: number;
  frameStart: number;
  frameEnd: number; // inclusive
  expectedFrameCount: number;
  chunkHashSha256: string;
  status: "PENDING" | "COMPLETED" | "FAILED";
}

export interface RenderAssemblyResult {
  isComplete: boolean;
  totalAssembledFrames: number;
  assembledDurationSeconds: number;
  canonicalMasterHash: string;
  verificationReport: {
    missingFrames: number[];
    duplicateFrames: number[];
    isContiguous: boolean;
    errors: string[];
  };
}

/**
 * REQ-037 & Distributed Render Chunking Architecture
 * Particiona, distribuye y valida el renderizado determinista en bloques contiguos sin pérdidas ni solapamientos.
 */
export class ChunkedRenderEngine {
  /**
   * Divide un trabajo de renderizado en bloques temporales deterministas
   */
  public static partitionJob(
    job: ChunkedRenderJob,
    targetChunkDurationSeconds = 5.0
  ): RenderChunk[] {
    const chunks: RenderChunk[] = [];
    const totalFrames = Math.round(job.totalDurationSeconds * job.fps);
    const framesPerChunk = Math.max(1, Math.round(targetChunkDurationSeconds * job.fps));

    let currentFrame = 0;
    let chunkIndex = 0;

    while (currentFrame < totalFrames) {
      const frameStart = currentFrame;
      const frameEnd = Math.min(totalFrames - 1, frameStart + framesPerChunk - 1);
      const expectedFrameCount = frameEnd - frameStart + 1;

      const startTimeSeconds = Number((frameStart / job.fps).toFixed(4));
      const endTimeSeconds = Number(((frameEnd + 1) / job.fps).toFixed(4));

      const chunkId = `chk_${job.jobId}_${String(chunkIndex).padStart(4, "0")}`;
      const payload = `${job.jobId}_${chunkIndex}_${frameStart}_${frameEnd}_${job.sourceIrHash}`;
      const chunkHashSha256 = crypto.createHash("sha256").update(payload, "utf8").digest("hex");

      chunks.push({
        chunkId,
        jobId: job.jobId,
        chunkIndex,
        startTimeSeconds,
        endTimeSeconds,
        frameStart,
        frameEnd,
        expectedFrameCount,
        chunkHashSha256,
        status: "COMPLETED",
      });

      currentFrame = frameEnd + 1;
      chunkIndex++;
    }

    return chunks;
  }

  /**
   * REQ-037: Render Verification Engine
   * Inspecciona y valida que la secuencia de chunks sea 100% contigua, sin frames perdidos ni duplicados
   */
  public static verifyAndAssemble(
    job: ChunkedRenderJob,
    chunks: RenderChunk[]
  ): RenderAssemblyResult {
    const errors: string[] = [];
    const missingFrames: number[] = [];
    const duplicateFrames: number[] = [];

    // 1. Ordenar chunks canónicamente por chunkIndex
    const sortedChunks = [...chunks].sort((a, b) => a.chunkIndex - b.chunkIndex);

    let expectedNextFrame = 0;
    let totalFramesSeen = 0;

    for (let i = 0; i < sortedChunks.length; i++) {
      const c = sortedChunks[i];

      if (c.jobId !== job.jobId) {
        errors.push(`CHUNK_JOB_MISMATCH: Chunk ${c.chunkId} pertenece a otro trabajo.`);
      }

      if (c.frameStart > expectedNextFrame) {
        // Hueco / Gap detectado
        for (let f = expectedNextFrame; f < c.frameStart; f++) {
          missingFrames.push(f);
        }
        errors.push(`FRAME_GAP_DETECTED: Falta intervalo [${expectedNextFrame}, ${c.frameStart - 1}]`);
      } else if (c.frameStart < expectedNextFrame) {
        // Solapamiento / Overlap detectado
        for (let f = c.frameStart; f < expectedNextFrame; f++) {
          duplicateFrames.push(f);
        }
        errors.push(`FRAME_OVERLAP_DETECTED: Solapamiento en intervalo [${c.frameStart}, ${expectedNextFrame - 1}]`);
      }

      expectedNextFrame = c.frameEnd + 1;
      totalFramesSeen += c.expectedFrameCount;
    }

    const expectedTotalFrames = Math.round(job.totalDurationSeconds * job.fps);
    if (expectedNextFrame < expectedTotalFrames) {
      for (let f = expectedNextFrame; f < expectedTotalFrames; f++) {
        missingFrames.push(f);
      }
      errors.push(`TRAILING_FRAMES_MISSING: Faltan frames finales hasta ${expectedTotalFrames - 1}`);
    }

    const isContiguous = errors.length === 0;
    const masterPayload = sortedChunks.map((c) => c.chunkHashSha256).join(":");
    const canonicalMasterHash = crypto.createHash("sha256").update(masterPayload, "utf8").digest("hex");

    return {
      isComplete: isContiguous,
      totalAssembledFrames: totalFramesSeen,
      assembledDurationSeconds: Number((totalFramesSeen / job.fps).toFixed(4)),
      canonicalMasterHash,
      verificationReport: {
        missingFrames,
        duplicateFrames,
        isContiguous,
        errors,
      },
    };
  }
}
