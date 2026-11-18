import { createHash } from "node:crypto";
import { FrameContext, RenderFrame } from "../types/index.js";

export interface RenderNode {
  id: string;
  type: string;
  inputs: string[]; // Node IDs
  parameters: Record<string, unknown>;
  cacheable: boolean;
  evaluate?: (context: FrameContext, inputFrames: RenderFrame[]) => RenderFrame;
}

/**
 * Grafo acíclico dirigido (DAG) de renderizado y evaluación con caché de nodos (Fase 9).
 */
export class RenderGraph {
  private nodes = new Map<string, RenderNode>();
  private nodeCache = new Map<string, RenderFrame>(); // cacheKey -> frame

  public addNode(node: RenderNode): this {
    this.nodes.set(node.id, node);
    return this;
  }

  public getNode(id: string): RenderNode | undefined {
    return this.nodes.get(id);
  }

  public get size(): number {
    return this.nodes.size;
  }

  /**
   * Calcula el hash determinista para la caché de un nodo.
   */
  public computeCacheKey(
    node: RenderNode,
    frameNumber: number,
    rendererVersion = "1.0.0"
  ): string {
    const raw = `${node.type}:${JSON.stringify(node.parameters)}:${frameNumber}:${rendererVersion}`;
    return createHash("sha256").update(raw).digest("hex").slice(0, 16);
  }

  /**
   * Evalúa un nodo del grafo con soporte para reutilización por caché.
   */
  public evaluateNode(
    nodeId: string,
    context: FrameContext,
    rendererVersion = "1.0.0"
  ): RenderFrame {
    const node = this.nodes.get(nodeId);
    if (!node) {
      return {
        frameNumber: context.frame,
        time: context.time,
        width: context.width,
        height: context.height,
        channels: 4,
      };
    }

    const cacheKey = this.computeCacheKey(node, context.frame, rendererVersion);
    if (node.cacheable && this.nodeCache.has(cacheKey)) {
      return this.nodeCache.get(cacheKey)!;
    }

    // Evaluar entradas recursivamente
    const inputFrames = node.inputs.map((inId) =>
      this.evaluateNode(inId, context, rendererVersion)
    );

    let outputFrame: RenderFrame;
    if (node.evaluate) {
      outputFrame = node.evaluate(context, inputFrames);
    } else {
      outputFrame = {
        frameNumber: context.frame,
        time: context.time,
        width: context.width,
        height: context.height,
        channels: 4,
        metadata: { nodeId: node.id, nodeType: node.type },
      };
    }

    if (node.cacheable) {
      this.nodeCache.set(cacheKey, outputFrame);
    }

    return outputFrame;
  }

  public clearCache(): void {
    this.nodeCache.clear();
  }

  public get cachedEntriesCount(): number {
    return this.nodeCache.size;
  }
}
