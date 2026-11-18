import { AIDirector } from "../../ai-director/core/AIDirector.js";
import { CreativeBrief, Platform } from "../../ai-planner/types/index.js";
import { EditingPlanCompiler } from "../../ai-planner/core/EditingPlanCompiler.js";
import { CaptionIntelligenceEngine } from "../../captions/intelligence/CaptionIntelligenceEngine.js";
import { CaptionNormalizer } from "../../captions/normalizer/CaptionNormalizer.js";
import { SRTParser } from "../../captions/transcript/SRTParser.js";
import { McpValidationError } from "../errors/mcp-errors.js";
import { CreateVideoFromScriptSchema } from "../schemas/mcp-tools.schema.js";
import { MCPProjectSnapshot, MCPProjectStore, ProjectIdentityInput } from "../types.js";

/**
 * Handler de la herramienta MCP `create_video_from_script` (Fase 17).
 * Orquesta Script -> Director -> Plan -> Compilación -> Captions -> IR Canónica.
 */
export async function handleCreateVideoFromScript(rawArgs: unknown) {
  const parseResult = CreateVideoFromScriptSchema.safeParse(rawArgs);
  if (!parseResult.success) {
    throw new McpValidationError("Invalid arguments for create_video_from_script", {
      issues: parseResult.error.issues,
    });
  }

  const args = parseResult.data;

  // 1. Calcular identidad determinista del proyecto
  const identityInput: ProjectIdentityInput = {
    script: args.script,
    styleId: args.styleId,
    durationTarget: args.durationTarget,
    aspectRatio: args.aspectRatio,
    fps: args.fps,
    language: args.language,
    seed: args.seed,
    schemaVersion: "1.7.0",
    engineVersion: "1.7.0",
  };

  const projectId = MCPProjectStore.computeProjectId(identityInput);

  if (args.dryRun) {
    return {
      projectId,
      status: "dry_run_success",
      plan: {
        styleId: args.styleId,
        durationTarget: args.durationTarget,
        aspectRatio: args.aspectRatio,
        fps: args.fps,
      },
    };
  }

  // 2. Orquestar Dirección de IA
  const director = new AIDirector();

  const brief: CreativeBrief = {
    objective: args.script.slice(0, 100),
    targetDuration: args.durationTarget,
    platform: (args.aspectRatio === "16:9" ? "youtube" : "tiktok") as Platform,
    styleId: args.styleId,
  };

  const session = await director.directSession(brief);

  if (!session.plan) {
    throw new Error("AI Director failed to produce a valid editing plan");
  }

  // 3. Compilar Plan de Edición a IR Canónica
  const compiledProject = EditingPlanCompiler.compile(session.plan);

  // 4. Procesar subtítulos con Caption Intelligence si fueron provistos
  const rawCaptions = (args as any).captionsSRT;
  if (rawCaptions) {
    const rawDoc = SRTParser.parse(rawCaptions);
    const captionDoc = CaptionNormalizer.normalize(rawDoc);
    const enrichedCaptions = new CaptionIntelligenceEngine().analyzeDocument(captionDoc);
    (compiledProject as any).captions = enrichedCaptions;
  }

  const layerCount = compiledProject.composition.getLayers().length;

  // 5. Calcular revisionId determinista e inmutable
  const revisionId = MCPProjectStore.computeRevisionId("root", "create_video_from_script", compiledProject);

  const snapshot: MCPProjectSnapshot = {
    projectId,
    revisionId,
    parentRevisionId: undefined,
    operation: "create_video_from_script",
    createdAt: new Date().toISOString(),
    ir: compiledProject,
    summary: {
      duration: compiledProject.duration,
      width: compiledProject.width,
      height: compiledProject.height,
      fps: compiledProject.fps,
      layerCount,
    },
  };

  // 6. Guardar en almacén inmutable
  MCPProjectStore.saveRevision(snapshot);

  return {
    projectId,
    revisionId,
    status: "created",
    duration: compiledProject.duration,
    width: compiledProject.width,
    height: compiledProject.height,
    fps: compiledProject.fps,
    sectionCount: compiledProject.sectionCount,
    shotCount: compiledProject.shotCount,
    layerCount,
    decisionsCount: session.decisions.length,
    summary: snapshot.summary,
  };
}
