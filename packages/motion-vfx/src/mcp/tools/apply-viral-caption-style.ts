import { ViralCaptionPresetRegistry } from "../../captions/presets/ViralCaptionPresets.js";
import { McpProjectNotFoundError, McpValidationError } from "../errors/mcp-errors.js";
import { ApplyViralCaptionStyleSchema } from "../schemas/mcp-tools.schema.js";
import { MCPProjectSnapshot, MCPProjectStore } from "../types.js";

/**
 * Handler de la herramienta MCP `apply_viral_caption_style` (Fase 17).
 * Aplica estilos virales de la Fase 16 derivando una nueva revisión inmutable.
 */
export async function handleApplyViralCaptionStyle(rawArgs: unknown) {
  const parseResult = ApplyViralCaptionStyleSchema.safeParse(rawArgs);
  if (!parseResult.success) {
    throw new McpValidationError("Invalid arguments for apply_viral_caption_style", {
      issues: parseResult.error.issues,
    });
  }

  const { projectId, revisionId, preset, overrides, safeZoneProfile } = parseResult.data;

  // 1. Obtener snapshot inmutable padre
  const parentSnapshot = MCPProjectStore.getRevision(projectId, revisionId);
  if (!parentSnapshot) {
    throw new McpProjectNotFoundError(projectId, revisionId);
  }

  // 2. Obtener preset de subtítulos de Fase 16
  const presetConfig = ViralCaptionPresetRegistry.getPreset(preset);

  // 3. Clonar la IR y aplicar el estilo
  const updatedIR = { ...parentSnapshot.ir };
  if (updatedIR.captions) {
    updatedIR.captions = {
      ...updatedIR.captions,
      safeZoneProfile: safeZoneProfile ?? presetConfig.safeZoneProfile,
      defaultStyle: {
        ...presetConfig.style,
        fontSize: overrides?.fontSize ?? presetConfig.style.fontSize,
        color: overrides?.color ?? presetConfig.style.color,
      },
    };
  }

  // 4. Calcular nueva identidad de revisión inmutable
  const newRevisionId = MCPProjectStore.computeRevisionId(
    parentSnapshot.revisionId,
    "apply_viral_caption_style",
    updatedIR
  );

  const newSnapshot: MCPProjectSnapshot = {
    projectId: parentSnapshot.projectId,
    revisionId: newRevisionId,
    parentRevisionId: parentSnapshot.revisionId,
    operation: "apply_viral_caption_style",
    createdAt: new Date().toISOString(),
    ir: updatedIR,
    summary: { ...parentSnapshot.summary },
  };

  // 5. Guardar nueva revisión inmutable
  MCPProjectStore.saveRevision(newSnapshot);

  return {
    projectId: newSnapshot.projectId,
    parentRevisionId: parentSnapshot.revisionId,
    newRevisionId: newSnapshot.revisionId,
    status: "applied",
    appliedPreset: preset,
    safeZoneProfile: updatedIR.captions?.safeZoneProfile,
  };
}
