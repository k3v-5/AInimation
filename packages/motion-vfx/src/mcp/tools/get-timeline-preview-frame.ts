import { CaptionEvaluator } from "../../captions/core/CaptionEvaluator.js";
import { BaseElement } from "../../elements/BaseElement.js";
import { Layer } from "../../core/layer.js";
import { ExportManifestBuilder } from "../../exporters/common/ExportManifest.js";
import { McpProjectNotFoundError, McpValidationError } from "../errors/mcp-errors.js";
import { GetTimelinePreviewFrameSchema } from "../schemas/mcp-tools.schema.js";
import { MCPProjectStore } from "../types.js";

/**
 * Handler de la herramienta MCP `get_timeline_preview_frame` (Fase 17).
 * Inspecciona el estado evaluado en el instante t reutilizando el motor core existente.
 */
export async function handleGetTimelinePreviewFrame(rawArgs: unknown) {
  const parseResult = GetTimelinePreviewFrameSchema.safeParse(rawArgs);
  if (!parseResult.success) {
    throw new McpValidationError("Invalid arguments for get_timeline_preview_frame", {
      issues: parseResult.error.issues,
    });
  }

  const { projectId, revisionId, time } = parseResult.data;

  // 1. Obtener snapshot inmutable
  const snapshot = MCPProjectStore.getRevision(projectId, revisionId);
  if (!snapshot) {
    throw new McpProjectNotFoundError(projectId, revisionId);
  }

  const comp = snapshot.ir.composition ?? snapshot.ir;
  const elements = comp.getElements ? comp.getElements() : [];
  const layers = comp.getLayers ? comp.getLayers() : [];
  const items = elements.length > 0 ? elements : layers;

  // 2. Evaluar capas activas en el instante t
  const activeLayers: Array<{
    id: string;
    name: string;
    inPoint: number;
    outPoint: number;
    transform?: any;
    opacity?: number;
  }> = [];

  for (const item of items) {
    const start = item.startTime ?? 0;
    const end = item.endTime ?? (start + (item.duration ?? 0));

    if (time >= start && time <= end) {
      let transformState: any;
      let opacityState = 1.0;

      if (item.transform && typeof item.transform.evaluate === "function") {
        transformState = item.transform.evaluate(time);
      }
      if (item.transform?.opacity && typeof item.transform.opacity.getValueAtTime === "function") {
        opacityState = item.transform.opacity.getValueAtTime(time);
      }

      activeLayers.push({
        id: item.id,
        name: item.name,
        inPoint: start,
        outPoint: end,
        transform: transformState,
        opacity: opacityState,
      });
    }
  }

  // 3. Evaluar captions activos en el instante t si existen
  let activeCaptionWord: any;
  if (snapshot.ir.captions && typeof snapshot.ir.captions.getWordAtTime === "function") {
    activeCaptionWord = snapshot.ir.captions.getWordAtTime(time);
  }

  // 4. Calcular hash determinista del frame evaluado
  const framePayload = {
    projectId: snapshot.projectId,
    revisionId: snapshot.revisionId,
    time,
    activeLayerCount: activeLayers.length,
    activeLayers: activeLayers.map((l) => ({ id: l.id, transform: l.transform, opacity: l.opacity })),
    activeCaptionWord: activeCaptionWord ? activeCaptionWord.text : null,
  };

  const frameHash = ExportManifestBuilder.sha256(ExportManifestBuilder.canonicalize(framePayload));

  return {
    projectId: snapshot.projectId,
    revisionId: snapshot.revisionId,
    time,
    frameHash,
    activeLayersCount: activeLayers.length,
    activeLayers,
    activeCaptionWord,
  };
}
